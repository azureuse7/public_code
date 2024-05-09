How to Write Conditional Statements in Python

This is where it gets interesting. In Python or in any other programming language you can make decisions based on conditions.

I hope you remember the boolean data type from a previous section – the one that can only hold True or False values.

Well, you can use a boolean with an if statement (a conditional statement) in Python to perform an action conditionally.

def main():
    number = int(input('what number would you like to check?\n- '))

    if number % 2 == 0:
        print(f"{number} is even.")
    else:
        print(f"{number} is odd.")


if __name__ == '__main__':
    main()

# what number would you like to check?
# - 10
# 10 is even.


You start by writing out if followed by a condition and a colon. By condition, what I mean is a statement that evaluates to a boolean value (true or false).

You've been using the == operator since the beginning and already know that it checks whether the value on the left side of it is equal to the one in the right or not.

So, if you divide a given number by 2 and the remainder is 0, that's an even number – otherwise, it'll be odd.

You can use the if...else statement to choose between two different options. But, if you have multiple options to choose from, you can use the if...elif...else statement.

def main():
    year = int(input('which year would you like to check?\n- '))

    if year % 400 == 0 and year % 100 == 0:
        print(f"{year} is leap year.")
    elif year % 4 == 0 and year % 100 != 0:
        print(f"{year} is leap year.")
    else:
        print(f"{year} is not leap year.")


if __name__ == '__main__':
    main()

# which year would you like to check?
# - 2004
# 2004 is leap year.


The elif statement usually goes after an if statement and before an else statement.

Think of it like "else if", so if the if statement fails, then the elif will take over. You write it exactly like a regular if statement.

Another new thing in this example is the and operator. It's one of the logical operators in Python. It does what it does in real life.

If the expressions on both sides of the and statement evaluates to true, then the whole expression evaluates to true. Simple.

Don't worry if you do not understand the and operator in detail at the moment. You'll learn about it and its siblings in the very next section.

Another thing you need to understand is that these if statements are just regular statements so you can do pretty much anything inside them.

def main():
    number = int(input('what number would you like to check?\n- '))

    is_not_prime = False

    if number == 1:
        print(f"{number} is not a prime number.")
    elif number > 1:
        for n in range(2, number):
            if (number % n) == 0:
                is_not_prime = True
                break

        if is_not_prime:
            print(f"{number} is not a prime number.")
        else:
            print(f"{number} is a prime number.")


if __name__ == '__main__':
    main()

# what number would you like to check?
# - 10
# 10 is not a prime number.


This example is a bit more complex than what you've seen so far. So let me break it down for you. The program checks whether a given number is a prime number or not.

First, you take a number from the user. For a number to be prime, it has to be divisible only by 1 and itself. Since 1 is only divisible by 1, it's not a prime number.

Now, if the given number is larger than 1, then you'd have to divide the number with all the numbers from 2 to that particular number.

If the number is divisible by any of these numbers, then you'll turn the is_not_prime variable to True, and break the loop.

The break statement simply breaks out of a loop immediately. There is also the continue statement that can skip the current iteration instead of breaking out.

Finally, if the is_not_prime variable is True then the number is not prime, otherwise it's a prime number.

So as you can see, not only you can put loops inside a conditional statement but also put conditional statements inside a loop.

The final example that I'd like to show you is the for...else statement. As you can see in the example above, you have a for statement followed by a if...else statement.

def main():
    number = int(input('what number would you like to check?\n- '))

    if number == 1:
        print(f"{number} is not a prime number.")
    elif number > 1:
        for n in range(2, number):
            if (number % n) == 0:
                print(f"{number} is not a prime number.")
                break
        else:
            print(f"{number} is a prime number.")


if __name__ == '__main__':
    main()

# what number would you like to check?
# - 5
# 5 is a prime number.


If you put an else statement on the same level as a for statement, then Python will execute whatever you put inside that else block as soon as the loop has finished.