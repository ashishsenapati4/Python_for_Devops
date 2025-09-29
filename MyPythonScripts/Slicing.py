# planet1="Closest to Sun"
#
# print(planet1[-1])
# print(planet1[-2])
# print(planet1[-3])
#
# #Slicing a string, get a substring from a string
# print(planet1[0:9])
#
# #slice only Sun from the planet1 string
# print(planet1[-3:])
# #or
# print(planet1[11:])
#
# #Slicing a tuple
# # devops = ("Linux", "Vagrant", "Bash Scripting", "AWS", "Jenkins", "Python", "Ansible")
# # print(devops[0])
# # print(devops[-2])
# # print(devops[0:2])
# #
# # print(devops[2:5][1])
# # print(type(devops[2:5][1]))
# #
# # #print(devops[2:5]) - > get the string Scripting from the result of this slice
# # print(devops[2:5][0][5:]) #Scripting
#
# #Slicing a List
# devops = ["Linux", "Vagrant", "Bash Scripting", "AWS", "Jenkins", "Python", "Ansible"]
# print(devops[0])
# print(devops[-2])
# print(devops[0:2])
#
# print(devops[2:5][1])
# print(type(devops[2:5][1]))
#
# #print(devops[2:5]) - > get the string Scripting from the result of this slice
# print(devops[2:5][0][5:]) #Scripting

# Dictionary Example
Skills = {"devops":("Linux", "Vagrant", "Bash Scripting", "AWS", "Jenkins", "Python", "Ansible"), "Development":["Java", "NodeJS", ".NET"]}
print(Skills)
print(Skills["devops"])
print(Skills["Development"])

print(Skills["devops"][-1])
print(Skills["Development"][-1:-3:-1]) # Last -1 is for negative step looping backwards