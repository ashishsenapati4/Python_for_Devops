# if-else condition

# x = 40
#
# if x > 40:
#     print("x is greater than 40")
# elif x == 40:
#     print("x is equal to 40")
# else:
#     print("x is less than 40")

"""
    This script will implement our knowledge on
    conditions and different datatypes
"""
print("Many Skill Sets Available")
print("Find out your match.")

print("Enter Capitalised Values: ")

devops = ["Linux", "Vagrant", "Bash Scripting", "AWS", "Jenkins", "Python", "Ansible"]
Development = ("NodeJS","Angularjs","Java", ".NET", "Python")

cntr_emp1 = {"Name":"Santa", "Skill":"Blockchain", "Code":1824}
cntr_emp2 = {"Name":"Jockey", "Skill":"AI", "Code":9933}


skill = input("Enter your Skill: ")

if(skill in devops and skill in Development):
    print(f"Skill: {skill} You can work for both devops and Development Team")
elif(skill in devops):
    print(f"Skill: {skill}. You can work for Devops Team")
elif(skill in Development):
    print(f"Skill: {skill} You can work for Development Team")
elif(skill == cntr_emp1["Skill"] or skill == cntr_emp2["Skill"]):
    print(f"We have Contract based opening for {skill} Skill")
else:
    print("Your skillset is not matching our profile. Apologies.")