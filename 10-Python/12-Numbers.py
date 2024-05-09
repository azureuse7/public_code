How to Work With Simple Numbers in Python

Simple numbers in Python are of two types. Whole numbers are integers and numbers with floating points in them are floats.

In Python, you can represent integers using four different bases. These are decimal, hexadecimal, octal, and binary.

BASE

REPRESENTATION

Decimal

404

Hexadecimal

0x194

Octal

0o624

Binary

0b000110010100

So you can represent the value of 404 in hexadecimal, octal, or binary by prefixing the corresponding value with 0x, 0o, or 0b respectively.

On the other hand you can represent floats with the precision of up to 15 significant digits in Python. Any digit after the 15th place may be inaccurate.

There are six different arithmetic operations that you can perform on any of the simple numeric types. The simplest of the bunch are addition and subtraction.

def main():
    num_1 = 15
    num_2 = 12

    print(f'sum of num_1 and num_2 is: {num_1 + num_2}')
    print(f'difference of num_1 and num_2 is: {num_1 - num_2}')

if __name__ == '__main__':
    main()

# sum of num_1 and num_2 is: 27
# difference of num_1 and num_2 is: 3

In case of a subtraction operation, the result will be negative if the second operand is larger than the first one.

def main():
    num_1 = 15
    num_2 = 12

    print(f'difference of num_2 and num_1 is: {num_2 - num_1}')

if __name__ == '__main__':
    main()

# difference of num_2 and num_1 is: -3

Similarly you can perform multiplication and division operations using their corresponding operators.

def main():
    num_1 = 15
    num_2 = 12

    print(f'product of num_1 and num_2 is: {num_1 * num_2}')
    print(f'quotient of num_1 and num_2 is: {num_1 / num_2}')
    print(f'floored quotient of num_1 and num_2 is: {num_1 // num_2}')


if __name__ == '__main__':
    main()

# product of num_1 and num_2 is: 180
# quotient of num_1 and num_2 is: 1.25
# floored quotient of num_1 and num_2 is: 1


Keep in mind that you can not divide a number by zero in Python. If you attempt that, you'll get a ZeroDivisionError error (more on that later).

Output from a division operation will always be a float value, unless you perform a floored division by using two division operators.

def main():
    num_1 = 15
    num_2 = 12

    print(f'floored quotient of num_1 and num_2 is: {num_1 // num_2}')


if __name__ == '__main__':
    main()

# floored quotient of num_1 and num_2 is: 1


In this case the result will be rounded off to the nearest integer low – so, for example, 0.25 will be lost. So only perform this operation when such loss of data is permissible.

The last operation to discuss is finding the remainder of a division operation.

def main():
    num_1 = 15
    num_2 = 12

    print(f'remainder of num_1 / num_2 is: {num_1 % num_2}')


if __name__ == '__main__':
    main()

# remainder of num_1 / num_2 is: 3


This operation is also called a modulo or modulus operation. So if someone mentions the modulo or modulus operator, they're referring to the percent sign.

You can turn an unsigned number into a negative one just by adding a - sign in front of it. You can also freely convert between integer to float and vice versa.

def main():
    float_variable = 1.25
    integer_variable = 55

    print(f'{float_variable} converted to an integer is: {int(float_variable)}')
    print(f'{integer_variable} converted to a float is: {float(integer_variable)}')


if __name__ == '__main__':
    main()

# 1.25 converted to an integer is: 1
# 55 converted to a float is: 55.0


Loss of data in case of a float to integer conversion is inevitable, so be careful. You can use the int() and float() methods on strings as well (more on that later).

Any arithmetic operation involving a float operand will always produce a float result, unless converted to integer explicitly.

def main():
    float_variable = 5.0
    integer_variable = 55

    print(f'the sum of {float_variable} and {integer_variable} is: {float_variable + integer_variable}')
    print(f'the sum of {float_variable} and {integer_variable} '
          f'converted to integer is: {int(float_variable + integer_variable)}')


if __name__ == '__main__':
    main()

# the sum of 5.0 and 55 is: 60.0
# the sum of 5.0 and 55 converted to integer is: 60


If you ever want to get the absolute value of a signed value you can do so using the abs() method.

def main():
    num_1 = -5.8

    print(f'the absolute value of {num_1} is: {abs(num_1)}')


if __name__ == '__main__':
    main()

# the absolute value of -5.8 is: 5.8


There is a similar method pow(x, y) that you can use to apply x as the power of y like this.

def main():
    x = 2
    y = 3

    print(f'{2} to the power of {3} is: {pow(2, 3)}')
    print(f'{2} to the power of {3} is: {2 ** 3}')


if __name__ == '__main__':
    main()

# 2 to the power of 3 is: 8
# 2 to the power of 3 is: 8


You can perform the same operation using two multiplication operators but I always prefer the pow() method.

Finally there is the divmod() method that you can use to combine the division and modulo operation.

def main():
    num_1 = 8
    num_2 = 2

    print(f'division and modulus of {num_1} and {num_2} is: {divmod(num_1, num_2)}')


if __name__ == '__main__':
    main()

# division and modulus of 8 and 2 is: (4, 0)


The method returns a tuple of numbers (more on that later). The first one is the result of the division and the second one is the result of the modulo operation.

These are the basic operations you can perform on simple numbers right from the get go. But you can do much more once you start to pull in the built-in modules.