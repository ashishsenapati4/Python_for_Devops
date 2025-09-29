import random
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

def order_food(item, *args):
    print(f"You have ordered {item}")
    # print(args)

    for i in args:
        print(f"You have ordered {i}")

    print("Enjoy the party")



def time_activity(*arg, **kwarg):
    print(arg)
    print(kwarg)

    min = sum(arg) + random.randint(0,50)
    choice = random.choice(list(kwarg.keys()))
    print(f"You can spend {min} Minutes on activity {kwarg[choice]}")
