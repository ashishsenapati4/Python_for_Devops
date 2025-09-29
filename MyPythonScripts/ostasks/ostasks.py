"""
#!/usr/bin/python3

import os

user_list = ["alpha","beta","gamma"]

print("#######################################")
print("Adding User")

for usr in user_list:
    exitcode = os.system("id {}".format(usr) )

    if exitcode != 0:
        print("########################################")


        print(f"User {usr} does not exist adding it.")

        print("########################################")
        print()
        os.system("useradd {}".format(usr))
    else:
        print("########################################")

        print(f"User {usr} already added. Found.")
        print("#########################################")
        print()

#Condition to check if group exits or not. Add if not exist
exitcode = os.system("grep science /etc/group")
if exitcode != 0:
    print("Group science does not exist. Adding it.")
    print("########################################")
    print()
    os.system("groupadd science")

else:
    print("Group already exist. skipping it")
    print("#################################")
    print()

#Adding all users to science group
for user in user_list:
    print(f"Adding {user} into the science group")
    print("#####################################")
    print()
    os.system("usermod -G science {}".format(user))

#Adding a directroy and assigning permission and ownership to that
print("Adding directory")
print("##################################")
print()

if os.path.isdir("/opt/science_dir"):
    print ("Directory exists. Skipping")
else:
    os.mkdir("/opt/science_dir")

print("Assigning permission and ownership to the directory.")
print("#####################################################")
print()
os.system("chown :science /opt/science_dir")

os.system("chmod 770 /opt/science_dir")
"""