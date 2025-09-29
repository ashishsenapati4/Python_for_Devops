import random


def time_activity(*arg, **kwarg):
    print(arg)
    print(kwarg)

    min = sum(arg) + random.randint(0,50)
    choice = random.choice(list(kwarg.keys()))
    print(f"You can spend {min} Minutes on activity {kwarg[choice]}")




time_activity(10,20,30, hobby="Dancing", fun="Cycling", work="DevOps")