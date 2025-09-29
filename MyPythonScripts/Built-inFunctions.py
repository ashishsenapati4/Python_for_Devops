'''
# String built ins
string_message = "corona is deadly"
print(string_message)
print(string_message.capitalize())

#dir() function
print(dir(string_message))
print(dir(""))

print(dir([]))
var1 = ['a','b','45'] #list
print(type(var1))

print(dir(())) #tuple
var2 = (1,2,45,'u',"Hey")

print(dir({}))
var3 = {"Hii","Bye"} #set

msg = "this is a message"
print(msg.upper())
print(msg.islower())
print(msg.isupper())

print(msg.find("message"))
print(msg[10:17])
print(msg.find("not")) #not found --> returns -1
'''

"""
seq1 = ("192","168","40","90")
print(".".join(seq1))
print("-".join(seq1))
print("/".join(seq1))


mountains = ["Everest", "Sahyadri","Alps", "K2"]
print(mountains)

mountains.append("Oregon mountain")
print(mountains)

mountains.extend(["mt Rainer", "Satpuda"])
print(mountains)

mountains.insert(1,"Mt Abu")
print(mountains)

mountains.pop()
print(mountains)

mountains.pop()
print(mountains)

mountains.pop(5)
print(mountains)

"""

cntr_emp = {"Name":"Santa", "Skill":"Java", "Code":1024}
print(cntr_emp.keys())
print(cntr_emp.values())
cntr_emp.clear()
print(cntr_emp)
