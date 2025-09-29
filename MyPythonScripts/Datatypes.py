str1 = "I am a string"

#Numbers
num1 = 123
float1 = 2.0

# List / Collection of multi datatypes, enclosed in square brackets(mutable)
first_list = [str1, "DevOps", 47, num1, 1.5]
print(first_list)

#Tuple / Collection of multi datatypes, enclosed in square brackets(immutable)
first_tuple = (str1, "DevOps", 47, num1, 1.5)
print(first_tuple)

#Dictionary / Collection of key:value pairs, curly braces
first_dictionary = {"Name":"Ashish", "Weight":80,"Exercises":["Boxing","Dancing","Jogging"]}
print(first_dictionary)

print("Variable first_list is a : ", type(first_list))
print("Variable first_tuple is a : ", type(first_tuple))
print("Variable first_dictionary is a : ", type(first_dictionary))

#Boolean
x = False
y = True

print(x," =>Type:",type(x))
print(y," =>Type:",type(y))