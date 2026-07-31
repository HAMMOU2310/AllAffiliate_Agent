# Define a function for addition
def add(x, y):
    return x + y

# Define a function for subtraction
def subtract(x, y):
    return x - y

# Define a function for multiplication
def multiply(x, y):
    return x * y

# Define a function for division
def divide(x, y):
    if y == 0:
        return "Error: Division by zero is not allowed"
    return x / y

# Define a function for exponentiation
def exponent(x, y):
    return x ** y

# Define a function for square root
def sqrt(x):
    if x < 0:
        return "Error: Square root of negative number is not a real number"
    return x ** 0.5

# Define a function for logarithm
def log(x):
    if x <= 0:
        return "Error: Logarithm of non-positive number is not defined"
    return x

# Define a function for sine
def sin(x):
    return x

# Define a function for cosine
def cos(x):
    return x

# Define a function for tangent
def tan(x):
    return x

# Create a dictionary to store the functions
functions = {
    '1': add,
    '2': subtract,
    '3': multiply,
    '4': divide,
    '5': exponent,
    '6': sqrt,
    '7': log,
    '8': sin,
    '9': cos,
    '10': tan,
}

# Create a main function to handle user input
def main():
    while True:
        print("Advanced Calculator")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Exponentiation")
        print("6. Square root")
        print("7. Logarithm")
        print("8. Sine")
        print("9. Cosine")
        print("10. Tangent")
        print("11. Quit")
        
        choice = input("Enter your choice: ")
        
        if choice == '11':
            break
        
        if choice in functions:
            if choice in ['6', '7', '8', '9', '10']:
                num = float(input("Enter a number: "))
                print(functions[choice](num))
            else:
                num1 = float(input("Enter the first number: "))
                num2 = float(input("Enter the second number: "))
                print(functions[choice](num1, num2))
        else:
            print("Invalid choice. Please try again.")

# Call the main function
main()