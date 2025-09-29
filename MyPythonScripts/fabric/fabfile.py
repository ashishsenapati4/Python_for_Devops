"""
from fabric.api import *

def greetings(name):
    print("Hello {}".format(name))

def system_info():
    print("Disk Space.")
    local("df -h")

    print("Memory Info")
    local("free -m")

    print("Uptime")
    local("uptime")

def remote_exec():
    run("hostname")
    print("####################################################")
    run("df -h")
    print("####################################################")
    run("free -m")
    print("####################################################")
    run("uptime")

    print()
    sudo("yum install zip unzip wget -y")


def websetup(weburl,dirname):

    print("####################################################")
    print("Installing dependencies")
    print("####################################################")
    sudo("yum install httpd wget unzip -y")


    print("####################################################")
    print("Start and enable service")
    print("####################################################")
    sudo("systemctl start httpd")
    sudo("systemctl enable httpd")


    print("####################################################")
    local("apt install zip unzip -y")


    print("####################################################")
    print("Downloading and pushing website to webservers")
    print("####################################################")
    local(("wget -O website.zip %s" % weburl))
    local(("unzip -o website.zip"))


    print("####################################################")
    with lcd(dirname):
            local("zip -r tooplate.zip *")
            put("tooplate.zip", "/var/www/html", use_sudo=True)
    with cd("/var/www/html"):
            sudo("unzip -o tooplate.zip")
    sudo("systemctl restart httpd")
    print("website setup is done")

"""