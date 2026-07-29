class Calc:
    def add(self, x, y):
        return x + y

    def sub(self, x, y):
        return x - y

    def mul(self, x, y):
        return x * y

    def div(self, x, y):
        if y == 0:
            return 'خطأ: لا يمكن القسمه على صفر'
        else:
            return x / y

    def pow(self, x, y):
        return x ** y

    def sqrt(self, x):
        if x < 0:
            return 'خطأ: لا يمكن اخذ الجذر التربيعي لعدد سالب'
        else:
            return x ** 0.5

    def sin(self, x):
        return __import__('math').sin(x)

    def cos(self, x):
        return __import__('math').cos(x)

    def tan(self, x):
        return __import__('math').tan(x)

    def log(self, x):
        if x <= 0:
            return 'خطأ: لا يمكن اخذ اللوجاريتم لعدد غير موجب'
        else:
            return __import__('math').log(x)


def main():
    calc = Calc()

    print('1. إضافة')
    print('2. طرح')
    print('3. ضرب')
    print('4. قسمة')
    print('5. رفع للقوة')
    print('6. أخذ الجذر التربيعي')
    print('7. دالة الساين')
    print('8. دالة الكوزاين')
    print('9. دالة التانجنت')
    print('10. دالة اللوجاريتم')

    choice = input('ادخل رقم الخيار: ')

    if choice == '1':
        x = float(input('ادخل العدد الأول: '))
        y = float(input('ادخل العدد الثاني: '))
        print(calc.add(x, y))

    elif choice == '2':
        x = float(input('ادخل العدد الأول: '))
        y = float(input('ادخل العدد الثاني: '))
        print(calc.sub(x, y))

    elif choice == '3':
        x = float(input('ادخل العدد الأول: '))
        y = float(input('ادخل العدد الثاني: '))
        print(calc.mul(x, y))

    elif choice == '4':
        x = float(input('ادخل العدد الأول: '))
        y = float(input('ادخل العدد الثاني: '))
        print(calc.div(x, y))

    elif choice == '5':
        x = float(input('ادخل العدد الأول: '))
        y = float(input('ادخل العدد الثاني: '))
        print(calc.pow(x, y))

    elif choice == '6':
        x = float(input('ادخل العدد: '))
        print(calc.sqrt(x))

    elif choice == '7':
        x = float(input('ادخل الزاوية بالراديان: '))
        print(calc.sin(x))

    elif choice == '8':
        x = float(input('ادخل الزاوية بالراديان: '))
        print(calc.cos(x))

    elif choice == '9':
        x = float(input('ادخل الزاوية بالراديان: '))
        print(calc.tan(x))

    elif choice == '10':
        x = float(input('ادخل العدد: '))
        print(calc.log(x))

    else:
        print('خطأ: الخيار غير متوفر')


if __name__ == '__main__':
    main()