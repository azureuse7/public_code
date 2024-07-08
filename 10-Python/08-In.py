# How to Use the in Operator in Python

# The in operator is the most common way of checking for any object's existence. For example, assume that you have a string and you want to check if it contains the word "red" or not.

def main():
    a_string = 'Little Red Riding-Hood comes to me one Christmas Eve to give me information of the cruelty and ' \
                'treachery of that dissembling Wolf who ate her grandmother. '

    print('Red' in a_string)


if __name__ == '__main__':
    main()

# True


# It's literally like asking Python, if the word Red is in the a_string variable. And Python will give you either True or False as an answer.

# The in operator is not exclusive to strings. You can actually use it on any other collection type such as lists, tuples, and ranges.

def main():
    books = ['Dracula', 'Frankenstein', 'The Omen', 'The Exorcist', 'The Legend of Sleepy Hollow']
    movies = ('A Christmas Carol', 'The Sea Beast', 'Enchanted', 'Pinocchio', 'The Addams Family')
    numbers = range(10)

    print('A Christmas Carol' in books)
    print('Enchanted' in movies)
    print(5 in numbers)


if __name__ == '__main__':
    main()

# False
# True
# True


# A Christmas Carol doesn't exist in the books list so it's a False statement. The other two statements are right, so they're True.

# You may also want to find out about the absence of an object. For that, you can use the not operator in conjunction with the in operator.

def main():
    books = ['Dracula', 'Frankenstein', 'The Omen', 'The Exorcist', 'The Legend of Sleepy Hollow']
    movies = ('A Christmas Carol', 'The Sea Beast', 'Enchanted', 'Pinocchio', 'The Addams Family')
    numbers = range(10)

    print('A Christmas Carol' not in books)
    print('Enchanted' not in movies)
    print(15 not in numbers)


if __name__ == '__main__':
    main()

# True
# False
# True


# A Christmas Carol doesn't exist in the books list, so the first statement evaluates to true. The second one evaluates to false because Enchanted is present in the movies list.

# The last one is self explanatory at this point. The in and not in operators come in very handy when working with conditional statements.