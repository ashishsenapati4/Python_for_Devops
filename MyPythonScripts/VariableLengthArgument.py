#Variable length arguments *Args(Non keyword  Arguments)
'''
def order_food(item, *args):
    print(f"You have ordered {item}")
    # print(args)

    for i in args:
        print(f"You have ordered {i}")

    print("Enjoy the party")

order_food("salad","Chicken","Pizza","Soup")
'''

#Variable length arguments **kwargs (Keyword Arguments)

import random
def time_activity(*args, **kwargs):
    print(args)
    print(kwargs)

    min = sum(args) + random.randint(0, 50)
    print(min)

    choice = random.choice(list(kwargs.keys()))

    print(kwargs.keys())
    print(choice)

    print(f"You have to spend {min} minutes for {kwargs[choice]}")

time_activity(10,20,10, hobby="Dance", sport="Boxing", fun="Driving", Work="DevOps")