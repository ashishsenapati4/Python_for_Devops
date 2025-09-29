import boto3

ec2 = boto3.client('ec2')

# Replace with your public IP address
my_ip = 'YOUR_IP_ADDRESS/32'

# Create a key pair
key_pair_name = 'my-key-pair'
key_pair = ec2.create_key_pair(KeyName=key_pair_name)
with open(f"{key_pair_name}.pem", "w") as file:
    file.write(key_pair['KeyMaterial'])
print(f"Key pair '{key_pair_name}' created and saved as {key_pair_name}.pem")

# Create a security group
sg_name = 'my-sec-group'
description = 'Allow SSH from my IP and HTTP from anywhere'
vpc_id = ec2.describe_vpcs()['Vpcs'][0]['VpcId']

sg_response = ec2.create_security_group(
    GroupName=sg_name,
    Description=description,
    VpcId=vpc_id
)
sg_id = sg_response['GroupId']

# Authorize inbound rules
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': my_ip}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

print(f"Security group '{sg_name}' created with ID {sg_id}")