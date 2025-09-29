#Defining functions
# def add(arg1, arg2):
#     total = arg1 + arg2
#     return total
# res = add(9,8)
# print(res)
# print(add(90,78))

'''
def adder(arg1, arg2):
    print(arg1+arg2)

print(adder(90,7)) '''

'''
def sum(arg, arg2):
    x = 0
    for i in arg:
        x = x+i
    for j in arg2:
        x = x+j
    return x

out = sum((19,2,3,2),[89,78])
print(out)


def greetings(msg="Morning"):
    print(f"Good {msg}")
    print("Welcome!")

greetings()
greetings("Evening") '''

def vac_feedbck(vac, efficacy):
    print(f"{vac} Vaccine is having {efficacy} % efficacy.")
    if (efficacy > 50) and (efficacy <= 75):
        print("Seems not so effective, Needs more trial")
    elif(efficacy > 75) and (efficacy < 90):
        print("Can consider this vaccine")
    elif(efficacy > 90):
        print("Sure, will take the shot.")
    else:
        print("Needs many more trails");

vac_feedbck("Astrazenica", 98)
vac_feedbck("Kukur", 40)