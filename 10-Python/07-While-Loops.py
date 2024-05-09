def main():
    for x in range(1, 6):
        print()
        for y in range(1, 11):
            print(f"{x} x {y} = {x * y}")


if __name__ == '__main__':
    main()

#
# 1 x 1 = 1
# 1 x 2 = 2
# 1 x 3 = 3
# 1 x 4 = 4


To create a multiplication table we need two operands: one remains constant for the entire table and the other increases by 1 until it reaches 10.

Here, x represents the left operand or the constant one and y represents the right operand or the variable one.

The first loop iterates through a range of 1 to 5 and the second loop iterates through a range of 1 to 10.

Since the ending number of a range is exclusive, you need to put a number that is 1 higher than the desired ending number.

First the Python interpreter encounters the outer loop and starts executing it. While inside that loop, the value of x is 1.

The interpreter then encounters the inner loop and starts executing that. While inside the inner loop, the value of x remains 1 but the value of y increases in each iteration.

The inner loop is the body of the outer loop in this case, so the first iteration of the outer loop lasts until the inner loop finishes.

After finishing 10 iterations of the inner loop, the interpreter comes back to the outer loop and starts executing it once again.

This time the value of x becomes 2 since that's what comes next in the range.

Just like that, the outer loop executes 5 times and the inner loop executes 10 times for each of those iterations.

Like a lot of other concepts, wrapping your head around nested loops can be difficult, but practice will make things easier.

I'd suggest you go ahead and implement this program using while loops to test your understanding.

You can also take the two numbers from the user and print the multiplication table within that range.

For example, if the user puts 5 and 10 as inputs, then you'll print out the multiplication tables of all the numbers from 5 to 10.

You can nest loops to even deeper levels, but going deeper than two loops may cause performance issues so be careful with that.