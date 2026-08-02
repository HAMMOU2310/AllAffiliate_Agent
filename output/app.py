class AdvancedCalculator:
    def __init__(self):
        self.history = []

    def add(self, num1, num2):
        result = num1 + num2
        self.history.append(f"Added {num1} and {num2}, result = {result}")
        return result

    def subtract(self, num1, num2):
        result = num1 - num2
        self.history.append(f"Subtracted {num2} from {num1}, result = {result}")
        return result

    def multiply(self, num1, num2):
        result = num1 * num2
        self.history.append(f"Multiplied {num1} and {num2}, result = {result}")
        return result

    def divide(self, num1, num2):
        if num2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        result = num1 / num2
        self.history.append(f"Divided {num1} by {num2}, result = {result}")
        return result

    def power(self, num1, num2):
        result = num1 ** num2
        self.history.append(f"Raised {num1} to the power of {num2}, result = {result}")
        return result

    def sqrt(self, num1):
        result = num1 ** 0.5
        self.history.append(f"Took square root of {num1}, result = {result}")
        return result

    def sin(self, num1):
        result = __import__("math").sin(num1)
        self.history.append(f"Took sine of {num1}, result = {result}")
        return result

    def cos(self, num1):
        result = __import__("math").cos(num1)
        self.history.append(f"Took cosine of {num1}, result = {result}")
        return result

    def tan(self, num1):
        result = __import__("math").tan(num1)
        self.history.append(f"Took tangent of {num1}, result = {result}")
        return result

    def print_history(self):
        for entry in self.history:
            print(entry)


def main():
    calculator = AdvancedCalculator()
    while True:
        print("\nAdvanced Calculator Menu:")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Exponentiation")
        print("6. Square Root")
        print("7. Sine")
        print("8. Cosine")
        print("9. Tangent")
        print("10. Print History")
        print("11. Quit")

        choice = input("Choose an operation (1-11): ")

        if choice in ["1", "2", "3", "4", "5"]:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            if choice == "1":
                print(f"Result: {calculator.add(num1, num2)}")
            elif choice == "2":
                print(f"Result: {calculator.subtract(num1, num2)}")
            elif choice == "3":
                print(f"Result: {calculator.multiply(num1, num2)}")
            elif choice == "4":
                try:
                    print(f"Result: {calculator.divide(num1, num2)}")
                except ZeroDivisionError as e:
                    print(str(e))
            elif choice == "5":
                print(f"Result: {calculator.power(num1, num2)}")

        elif choice in ["6", "7", "8", "9"]:
            num1 = float(input("Enter a number: "))
            if choice == "6":
                print(f"Result: {calculator.sqrt(num1)}")
            elif choice == "7":
                print(f"Result: {calculator.sin(num1)}")
            elif choice == "8":
                print(f"Result: {calculator.cos(num1)}")
            elif choice == "9":
                print(f"Result: {calculator.tan(num1)}")

        elif choice == "10":
            calculator.print_history()

        elif choice == "11":
            break

        else:
            print("Invalid choice. Please choose a valid operation.")


if __name__ == "__main__":
    main()