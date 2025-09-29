try:
    number = int(input("Enter a number: "))
    print(type(number))
    result = 10 / number
except ValueError:
    print("Invalid Input! Enter a valid number.")
except ZeroDivisionError:
    print("Cannot divide a number by zero")
except Exception as e:
    print(f"Uexpected error: {e}")
else:
    print(f"The result is {result}")

print("Happy coding")