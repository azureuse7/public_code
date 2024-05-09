How to Work With Variables and Different Types of Data in Python

To create a new variable in Python, you just need to type out the name of the variable, followed by an equal sign and the value.

def main():
    book = 'Dracula'
    author = 'Bram Stoker'
    release_year = 1897
    goodreads_rating = 4.01

    print(book)
    print(author)
    print(release_year)
    print(goodreads_rating)


if __name__ == '__main__':
    main()
    
# Dracula
# Bram Stoker
# 1897
# 4.01



As long as you're keeping these guidelines in mind, declaring variables in Python is very straightforward.

Instead of declaring the variables in separate lines, you can declare them in one go as follows:

def main():
    book, author, release_year, goodreads_rating = 'Dracula', 'Bram Stoker', 1897, 4.01

    print(book)
    print(author)
    print(release_year)
    print(goodreads_rating)


if __name__ == '__main__':
    main()
    
# Dracula
# Bram Stoker
# 1897
# 4.01


All you have to do is write the individual variable names in a single line using commas as separators.

Then after the equal sign you have to write the corresponding values in the same order as their names again using commas as separators.

In fact, you can also print them all out in one go. The print() method can take multiple parameters separated by commas.

def main():
    book, author, release_year, goodreads_rating = 'Dracula', 'Bram Stoker', 1897, 4.01

    print(book, author, release_year, goodreads_rating)


if __name__ == '__main__':
    main()
    
# Dracula Bram Stoker 1897 4.01

These parameters are then printed on the terminal in a single line using spaces for separating each of them.

Speaking of the print() method, you can use the + sign to add variables with strings inside a print method:

def main():
    book, author, release_year, goodreads_rating = 'Dracula', 'Bram Stoker', 1897, 4.01

    print(book + ' is a novel by ' + author + ', published in ' + release_year + '. It has a rating of ' + goodreads_rating + ' on goodreads.')


if __name__ == '__main__':
    main()


# TypeError: can only concatenate str (not "int") to str

If you try to run this code you'll get a TypeError that says Python can concatenate or add together strings not integers.

In the code snippet above, book, author, release_year, and goodreads_rating are all variables of different types.

The book and author variables are strings. The release_year is an integer and finally the goodreads_rating variable is a floating point number.

Whenever Python encounters a + sign in front of a numeric type, it assumes that the programmer may be performing an arithmetic operation.

The easiest way to solve this problem is to convert the numeric types to strings. You can do that by calling the str() method on the numeric variables.

def main():
    book, author, release_year, goodreads_rating = 'Dracula', 'Bram Stoker', 1897, 4.01

    print(book + ' is a novel by ' + author + ', published in ' + str(release_year) + '. It has a rating of ' + str(goodreads_rating) + ' on goodreads.')


if __name__ == '__main__':
    main()

# Dracula is a novel by Bram Stoker, published in 1897. It has a rating of 4.01 on goodreads.

That's better – but you can make that line of code even more readable by using a f string.

def main():
    book, author, release_year, goodreads_rating = 'Dracula', 'Bram Stoker', 1897, 4.01

    print(f'{book} is a novel by {author}, published in {release_year}. It has a rating of {goodreads_rating} on goodreads.')


if __name__ == '__main__':
    main()

# Dracula is a novel by Bram Stoker, published in 1897. It has a rating of 4.01 on goodreads.

You can turn a regular string to a f string by putting a f in front of it and suddenly you can write variable names inside curly braces right within the string itself.

There is one last thing that's bugging me, and that's the length of the line of code itself. Fortunately you can split long strings into multiple shorter ones as follows:

def main():
    book, author, release_year, goodreads_rating = 'Dracula', 'Bram Stoker', 1897, 4.01

    print(f'{book} is a novel by {author}, published in {release_year}.'
          f' It has a rating of {goodreads_rating} on goodreads.')


if __name__ == '__main__':
    main()

# Dracula is a novel by Bram Stoker, published in 1897. It has a rating of 4.01 on goodreads.

Now that's how a good piece of Python code should look. I'd suggest you try to make your code readable from the very beginning – you'll thank me later for that.

Other than int and float, there is another numeric type called complex in Python. It was specifically designed for dealing with numbers like 500+2j.

There are also boolean data that can hold the value True or False and nothing else. You can actually ask Python questions and it'll answer in boolean.

Throughout this book you'll not see complex numbers in action and booleans will come into play much later. So for now, lets focus on simple numbers and strings.

How to Work With Simple Numbers i