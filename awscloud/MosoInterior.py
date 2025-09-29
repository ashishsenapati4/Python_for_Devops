#!/usr/bin/env python3
"""
Create AWS resources to host the "Moso Interior" Tooplate template:
- Key pair
- EC2 security group (SSH from your public IP, HTTP from anywhere)
- t2.micro EC2 instance running Amazon Linux 2023
- ALB (internet-facing) spanning all subnets in the default VPC, security group allowing HTTP from anywhere
- Target group + listener + register instance
Prints ALB endpoint (DNS name) at the end.

Requires:
    pip install boto3 requests
AWS creds/config must be available (env, profile, or IAM role).
"""

import boto3
import botocore
import requests
import time
import sys
import os

# Configurable
TEMPLATE_NAME = "MosoInterior"  # used for naming resources
TOOPLATE_DOWNLOAD_URL = "https://www.tooplate.com/download/2133_moso_interior"  # Moso Interior template
KEY_NAME = f"{TEMPLATE_NAME}-key"
KEY_FILE = f"{KEY_NAME}.pem"
EC2_SG_NAME = f"{TEMPLATE_NAME}-sg-ec2"
ALB_SG_NAME = f"{TEMPLATE_NAME}-sg-alb"
ALB_NAME = f"{TEMPLATE_NAME}-ALB"
TG_NAME = f"{TEMPLATE_NAME}-tg"
INSTANCE_NAME = f"{TEMPLATE_NAME}-web-1"
INSTANCE_TYPE = "t2.micro"
HTTP_PORT = 80
SSH_PORT = 22

# Create boto3 clients
session = boto3.session.Session()
region = session.region_name or "us-east-1"
ec2 = session.resource('ec2', region_name=region)
ec2_client = session.client('ec2', region_name=region)
elbv2_client = session.client('elbv2', region_name=region)
iam_client = session.client('iam', region_name=region)

def get_my_public_ip():
    try:
        ip = requests.get("https://checkip.amazonaws.com/", timeout=10).text.strip()
        if '/' not in ip:
            ip = ip + "/32"
        print(f"Detected public IP for SSH rule: {ip}")
        return ip
    except Exception as e:
        print("Unable to determine public IP automatically:", e)
        print("Defaulting SSH CIDR to 0.0.0.0/0 (NOT recommended).")
        return "0.0.0.0/0"

def get_default_vpc():
    res = ec2_client.describe_vpcs(Filters=[{'Name':'isDefault','Values':['true']}])
    vpcs = res.get('Vpcs', [])
    if not vpcs:
        raise SystemExit("No default VPC found in region. Script expects a default VPC.")
    return vpcs[0]['VpcId']

def get_subnets_for_vpc(vpc_id):
    res = ec2_client.describe_subnets(Filters=[{'Name':'vpc-id','Values':[vpc_id]}])
    subnets = res.get('Subnets', [])
    if not subnets:
        raise SystemExit("No subnets found in default VPC.")
    return subnets  # list of dicts

def create_keypair_if_not_exists(key_name, key_file_path):
    try:
        # check if key exists
        existing = ec2_client.describe_key_pairs(KeyNames=[key_name])
        print(f"Key pair {key_name} already exists in AWS; will not recreate. Attempting to reuse locally if found.")
        if os.path.exists(key_file_path):
            print(f"Local key {key_file_path} already exists — reusing it.")
            return
        else:
            print(f"Local key file {key_file_path} not found. Please fetch the private key from AWS console or delete the AWS key and re-run.")
            return
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
            pass
        else:
            raise

    print(f"Creating key pair: {key_name}")
    kp = ec2_client.create_key_pair(KeyName=key_name)
    key_material = kp['KeyMaterial']
    with os.fdopen(os.open(key_file_path, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
        f.write(key_material)
    os.chmod(key_file_path, 0o400)
    print(f"Saved key to {key_file_path} (chmod 400)")

def create_security_group(vpc_id, group_name, description, ingress_rules):
    # Check existing
    existing = ec2_client.describe_security_groups(Filters=[{'Name':'group-name','Values':[group_name]}, {'Name':'vpc-id','Values':[vpc_id]}])
    if existing.get('SecurityGroups'):
        sg = existing['SecurityGroups'][0]
        print(f"Security Group {group_name} already exists: {sg['GroupId']}")
        return sg['GroupId']
    print(f"Creating security group {group_name} in VPC {vpc_id}")
    resp = ec2_client.create_security_group(Description=description, GroupName=group_name, VpcId=vpc_id)
    sg_id = resp['GroupId']
    print(f"Created SG {sg_id}. Now authorizing ingress...")
    permissions = []
    for rule in ingress_rules:
        permissions.append({
            'IpProtocol': rule.get('IpProtocol','tcp'),
            'FromPort': rule['FromPort'],
            'ToPort': rule['ToPort'],
            'IpRanges': [{'CidrIp': cidr} for cidr in rule.get('CidrIps', [])],
        })
    ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=permissions)
    print("Ingress rules set.")
    return sg_id

def find_amzn2023_ami():
    # Query AWS for images owned by amazon where name indicates Amazon Linux 2023
    print("Searching for latest Amazon Linux 2023 AMI...")
    filters = [
        {'Name':'owner-alias','Values':['amazon']},
    ]
    # Try multiple name patterns
    name_patterns = ['*amzn-2023*', '*Amazon-Linux-2023*', '*amzn2023*', '*al2023*', '*amazon-linux-2023*']
    images = []
    for pat in name_patterns:
        try:
            resp = ec2_client.describe_images(Filters=[{'Name':'name','Values':[pat]}], Owners=['amazon'])
            images += resp.get('Images', [])
        except Exception:
            continue
    if not images:
        # fallback: try amazon linux 2 latest
        print("Could not find Amazon Linux 2023 images by pattern; falling back to Amazon Linux 2 latest AMI.")
        # Use SSM parameter for Amazon Linux 2
        ssm = session.client('ssm', region_name=region)
        try:
            param = ssm.get_parameter(Name="/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
            return param['Parameter']['Value']
        except Exception as e:
            raise SystemExit("Failed to find AL2023 or fallback AMI. Error: " + str(e))

    # pick latest by CreationDate
    images = sorted(images, key=lambda i: i.get('CreationDate',''), reverse=True)
    ami_id = images[0]['ImageId']
    print(f"Selected AMI {ami_id} named '{images[0].get('Name')}'")
    return ami_id

def create_instance(ami_id, instance_type, key_name, sg_id, subnet_id, user_data, tag_name):
    print("Launching EC2 instance...")
    instances = ec2.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[sg_id],
        SubnetId=subnet_id,
        UserData=user_data,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key':'Name','Value':tag_name}]
        }],
    )
    instance = instances[0]
    print(f"Instance launched {instance.id}. Waiting until running...")
    instance.wait_until_running()
    instance.load()
    print(f"Instance is running. Private IP: {instance.private_ip_address}, Public IP: {instance.public_ip_address}")
    return instance.id, instance.instance_id if hasattr(instance, 'instance_id') else instance.id, instance.public_ip_address, instance.private_ip_address

def create_target_group(name, vpc_id, port=80):
    print("Creating target group:", name)
    resp = elbv2_client.create_target_group(
        Name=name[:32],  # TG name max 32 chars
        Protocol='HTTP',
        Port=port,
        VpcId=vpc_id,
        TargetType='instance',
        HealthCheckProtocol='HTTP',
        HealthCheckPath='/',
        HealthCheckPort=str(port),
        Matcher={'HttpCode':'200,301,302'}
    )
    tg_arn = resp['TargetGroups'][0]['TargetGroupArn']
    print("Target group ARN:", tg_arn)
    return tg_arn

def create_alb(name, subnet_ids, sg_id):
    print("Creating ALB:", name)
    resp = elbv2_client.create_load_balancer(
        Name=name[:32],
        Subnets=subnet_ids,
        SecurityGroups=[sg_id],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    alb = resp['LoadBalancers'][0]
    alb_arn = alb['LoadBalancerArn']
    alb_dns = alb['DNSName']
    print("ALB ARN:", alb_arn)
    print("ALB DNS:", alb_dns)
    return alb_arn, alb_dns

def create_listener(alb_arn, tg_arn, port=80):
    print("Creating listener on port", port)
    resp = elbv2_client.create_listener(
        LoadBalancerArn=alb_arn,
        Protocol='HTTP',
        Port=port,
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': tg_arn
        }],
    )
    listener_arn = resp['Listeners'][0]['ListenerArn']
    print("Listener ARN:", listener_arn)
    return listener_arn

def register_targets(tg_arn, instance_id, port=80):
    print(f"Registering instance {instance_id} with target group")
    elbv2_client.register_targets(TargetGroupArn=tg_arn, Targets=[{'Id': instance_id, 'Port': port}])

def wait_for_targets_healthy(tg_arn, instance_id, timeout_seconds=300):
    print("Waiting for target to become healthy (may take a minute)...")
    elapsed = 0
    while elapsed < timeout_seconds:
        resp = elbv2_client.describe_target_health(TargetGroupArn=tg_arn, Targets=[{'Id':instance_id}])
        states = resp.get('TargetHealthDescriptions', [])
        if states:
            state = states[0]['TargetHealth']['State']
            print("Target state:", state)
            if state == 'healthy':
                return True
        time.sleep(6)
        elapsed += 6
    print("Timeout waiting for healthy target.")
    return False

def main():
    my_ip_cidr = get_my_public_ip()
    vpc_id = get_default_vpc()
    print("Default VPC:", vpc_id)
    subnets = get_subnets_for_vpc(vpc_id)
    subnet_ids = [s['SubnetId'] for s in subnets]
    print("Found subnets in default VPC:", subnet_ids)

    # Create keypair (or reuse existing). Private key saved locally if created.
    create_keypair_if_not_exists(KEY_NAME, KEY_FILE)

    # Create EC2 security group (allow SSH from your IP, HTTP from anywhere)
    ec2_sg_id = create_security_group(
        vpc_id,
        EC2_SG_NAME,
        f"Security group for EC2 ({TEMPLATE_NAME})",
        ingress_rules=[
            {'FromPort': SSH_PORT, 'ToPort': SSH_PORT, 'CidrIps': [my_ip_cidr]},
            {'FromPort': HTTP_PORT, 'ToPort': HTTP_PORT, 'CidrIps': ['0.0.0.0/0']},
        ]
    )
    print("EC2 SG ID:", ec2_sg_id)

    # Create ALB security group (allow HTTP from anywhere)
    alb_sg_id = create_security_group(
        vpc_id,
        ALB_SG_NAME,
        f"Security group for ALB ({TEMPLATE_NAME})",
        ingress_rules=[
            {'FromPort': HTTP_PORT, 'ToPort': HTTP_PORT, 'CidrIps': ['0.0.0.0/0']},
        ]
    )
    print("ALB SG ID:", alb_sg_id)

    # Find latest Amazon Linux 2023 AMI
    ami_id = find_amzn2023_ami()
    print("Using AMI:", ami_id)

    # Prepare user_data script that installs webserver, downloads Tooplate template and extracts
    user_data = f"""#!/bin/bash
# cloud-init
set -eux
# Attempt to use dnf (Amazon Linux 2023 uses dnf); fallback to yum
if command -v dnf >/dev/null 2>&1; then
    PKG=dnf
else
    PKG=yum
fi
$PKG -y update || true
# install unzip and httpd
$PKG -y install unzip httpd || $PKG -y install unzip nginx || true

# prefer httpd (apache) if installed
if command -v httpd >/dev/null 2>&1; then
    systemctl enable --now httpd
    WEBROOT=/var/www/html
else
    if command -v nginx >/dev/null 2>&1; then
        systemctl enable --now nginx
        WEBROOT=/usr/share/nginx/html
    else
        # fallback to python simple server
        WEBROOT=/var/www/html
        mkdir -p $WEBROOT
    fi
fi

cd /tmp
# download Tooplate template zip (Moso Interior)
curl -L -o template.zip "{TOOPLATE_DOWNLOAD_URL}" || wget -O template.zip "{TOOPLATE_DOWNLOAD_URL}" || true
# attempt unzip
if [ -f template.zip ]; then
  unzip -o template.zip -d /tmp/template || true
  # Find root HTML files and copy to webroot
  if [ -d /tmp/template ]; then
    # some zip may expand into a folder; copy contents
    rsync -a /tmp/template/ $WEBROOT/ || cp -r /tmp/template/* $WEBROOT/ || true
  else
    echo "template not extracted; leaving default webroot content"
  fi
fi

# set ownership and permissions
if [ -d "$WEBROOT" ]; then
  chown -R ec2-user:ec2-user "$WEBROOT" || true
  chmod -R 755 "$WEBROOT" || true
fi

# create index if missing
if [ ! -f "$WEBROOT/index.html" ]; then
  cat > $WEBROOT/index.html <<'HTML'
<!doctype html>
<html><head><meta charset="utf-8"><title>{TEMPLATE_NAME} placeholder</title></head>
<body><h1>{TEMPLATE_NAME} template placeholder</h1><p>The template download may have failed. Please check.</p></body></html>
HTML
fi

echo "userdata finished"
"""

    # choose one subnet to launch EC2 in (use first)
    chosen_subnet = subnet_ids[0]
    print("Launching EC2 in subnet:", chosen_subnet)

    instance_id = None
    try:
        # create instance
        instances = ec2.create_instances(
            ImageId=ami_id,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[ec2_sg_id],
            SubnetId=chosen_subnet,
            UserData=user_data,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': INSTANCE_NAME}]
            }]
        )
        inst = instances[0]
        print("Launched instance id:", inst.id)
        inst.wait_until_running()
        inst.reload()
        instance_id = inst.id
        print("Instance running. Public IP:", inst.public_ip_address, "Private IP:", inst.private_ip_address)
    except Exception as e:
        print("Failed to create instance:", e)
        sys.exit(1)

    # Create target group (HTTP)
    tg_arn = create_target_group(TG_NAME, vpc_id, port=HTTP_PORT)

    # Create ALB across all subnets found
    alb_arn, alb_dns = create_alb(ALB_NAME, subnet_ids, alb_sg_id)

    # Create listener forwarding to TG
    listener_arn = create_listener(alb_arn, tg_arn, port=HTTP_PORT)

    # Register EC2 instance with target group
    register_targets(tg_arn, instance_id, port=HTTP_PORT)

    # Wait for target to become healthy (best-effort)
    healthy = wait_for_targets_healthy(tg_arn, instance_id, timeout_seconds=240)
    if not healthy:
        print("Target didn't become healthy yet — it may still work. Check health in console if necessary.")

    print("\n=== SUCCESS ===")
    print(f"ALB DNS Name / Endpoint: http://{alb_dns}")
    print("ALB will forward to target group:", tg_arn)
    print("EC2 instance ID:", instance_id)
    print("EC2 security group:", ec2_sg_id)
    print("ALB security group:", alb_sg_id)
    print("Key pair name:", KEY_NAME, "private key saved to:", KEY_FILE)
    print("If you need to SSH: ssh -i", KEY_FILE, f"ec2-user@{inst.public_ip_address}")
    print("Remember to clean up resources when done (terminate instance, delete ALB, TG, SGs, keypair) to avoid charges.")

if __name__ == "__main__":
    main()
