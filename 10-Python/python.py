

total = 0
for i in range(1, 5):  #(add all the integera for 1 to 5 not 5 total )
    total += i
print(total) #(and we then printed total)

#answer 10
#################################################################

#while loop

total2 = 0   #(new variable  total2)
j = 1            #(we need iniilize  it )
while j < 5:     ##(while j is less the 5 do the follwoing)
    total2 += j      #(add j to total)
    j +=1            #(add  to j, now we will go back to the while statmnet)
print(total2)

#answer 10 

#################################################################

given_list = [5, 4 , 4 , 4 , 3, 1 -2, -3 , -5]  # given list
total3 = 0 #
i = 0 #
while given_list[i] > 0: # first check element in given list that is 5,
# this element is greater then 0
    total3 += given_list[i] #
    i += 1 # incremnet i with 1
print(total3)

answer 17

#################################################################


# what if there is no negative example 
given_list = [5, 4 , 4 , 4 , 3,]

total = 0

i = 0

while given_list[i] > 0:
    total += given_list[i]
    i += 1 # increment i with 1
    print(total)


error 


#################################################################
what if there is no negative example 


given_list2 = [5, 4 , 4 , 4 , 3, -2 , -3 , -5]
total4 = 0

for element in given_list2:  # add all elemnent to total 4
    total4 += element
print(element)

#################################################################

# what if we want to break soon as we see a negative 
# sum of positive numbers 

given_list2 = [5, 4 , 4 , 4 , 3, -2 , -3 , -5]
total4 = 0
for element in given_list2:  # add all elemnent to total 4
    if element <= 0:
        break
        total4 += element
print(element)


#################################################################

given_list2 = [5, 4 ., 4 , 4 , 3, -2 , -3 , -5 )
total5 = 0 
i = 0
while True:
total5 += given_list2[i]
i += 1
if given_list2[i] <= 0:
break 
print(total5)

17

#################################################################

a = ["apple", "banana", "republic"]
for element in a:
    print(element)
	
apple
banana
republic

#################################################################



for i in range(len(a)): # 0, 1, 2
    for j in range(i + 1):
        # i = 0 -> j = 0
        # i = 1 -> j = 0, 1
        # i = 2 -> j = 0, 1, 2
        print(a[i])
		
		
		apple

banana

banana

republic

republic

republic
#################################################################


# Can you compute the sum of all multiples
# of 3 and 5 that are less than 100?
print(list(range(1, 100)))

[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

total = 0
for i in range(1, 100):
    if i % 3 == 0 or i % 5 == 0:
        total += i
        print(total)

#################################################################

# Tutorial 6

given_list = [7, 5, 4, 4, 3, 1, -2, -3, -5, -7]
total2 = 0

j = len(given_list) - 1
while given_list[j] < 0:
    total2 += given_list[j]
    j -= 1
    print(total2)


-17

#################################################################

Dictionaries In Python
d = {}
#d = {"George": 24, "Tom": 32}   could also write so it has some predefind value

d["George"] = 24
d["Tom"] = 32
d["Jenny"] = 16

print(d["George"])

print(d["George"])
24

print(d["Tom"])
32

print(d["Alice"])
KeyError                                  Traceback (most recent call last)
<ipython-input-6-e722e03f8739> in <module>()
----> 1 print(d["Alice"])

KeyError: 'Alice'
-------------
print(d["Jenny"])
16

d["Jenny"] = 20

print(d["Jenny"])
20

# keys are commonly strings or numbers
d[10] = 100

print(d[10])
100
#################################################################

# how to iterate over key-value pairs?
for key, value in d.items():
    print("key:")
    print(key)
    print("value:")
    print(value)
    print("")
	
	key:

George

value:

24



key:

Tom

value:

32



key:

Jenny

value:

20



key:

10

value:

100

#################################################################
class Robot:


   def introduce_self(self):  # function
     print("My name is " + self.name)  # this in Java


r1 = Robot()  # objects
r1.name = "Tom"
r1.color = "red"
r1.weight = 30

r2 = Robot()
r2.name = "Jerry"
r2.color = "blue"
r2.weight = 40



r1.introduce_self()
r2.introduce_self()


r1.name get from self.name 

class Robot:
    def __init__(self, name, color, weight):
        self.name = name
        self.color = color
        self.weight = weight

    def introduce_self(self):
       print("My name is " + self.name)


#################################################################

r1 = Robot("Tom", "red", 30)
r2 = Robot("Jerry", "blue", 40)

r1.introduce_self()
r2.introduce_self()

2
	
mesage = "Hello Python Crash Course reader!"
print(mesage)



name = "ada lovelace"
print(name.title())

name = "Ada Lovelace"
print(name.upper())
print(name.lower())


first_name = "gautam"
last_name = "thakur"
fullname = first_name+ " "+ last_name
print(fullname)



first_name = "gautam"
last_name = "thakur"
fullname = first_name+ " "+ last_name
print("hello, "+ fullname.title()+ "!")


:
first_name = "gautam"
last_name = "thakur"
fullname = first_name+ " "+ last_name
message = "hello, "+ fullname.title()+ "!"
print(message)


Adding Whitespace to Strings with Tabs or Newlines
print("\tgautam")


# To add a newline in a string, use the character combination \n:

print("Languages:\nPython\nC\nJava")
Python
C 
Java 

#################################################################

# You can also combine tabs and newlines in a single string. The string "\n\t" tells Python to move to a new line, and start the next line with a tab
 
print("Languages:\n\tPython\n\tC\n\tJava")
    Python 
    C 
    JavaScript 
 
Stripping Whitespace

# #################################################################

 
Avoiding Type Errors with the str() Function
. For example, say you want to wish someone a happy birthday. You might write code like this:

age = 23
message = "Happy " + age + "rd Birthday!"
print(message)


# You might expect this code to print the simple birthday greeting, Happy 23rd birthday! 
# But if you run this code, you’ll see that it generates an error:
 
Traceback (most recent call last): 
  File "birthday.py", line 2, in <module>     message = "Happy " + age + "rd Birthday!" 
 TypeError: Can't convert 'int' object to str implicitly 
 
# This is a type error. It means Python can’t recognize the kind of information you’re using. 
# In this example Python sees at  that you’re using a variable that has an integer value (int), 
# but it’s not sure how to interpret that value. Python knows that the variable could represent either 
# the numerical value 23 or the characters 2 and 3. When you use integers within strings like this, 
# you need to specify explicitly that you want Python to use the integer as a string of characters. 
# You can do this by wrapping the variable in the str() function, which tells Python to represent non-string values as strings:


age = 23
message = "Happy " + str(age) + "rd Birthday!"
print(message)


#################################################################
# List

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles)

['trek', 'cannondale', 'redline', 'specialized'] 
bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0])

#################################################################

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0].title())


# Index Positions Start at 0, Not 1
 
################################################################# 

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0].title())
print(bicycles[3])


#################################################################

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[-1])


##################################################################

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
message = "My first bicycle was a " + bicycles[0].title() + "."
print(message)

##################################################################

# For example, let’s say we have a list of motorcycles, and the first item in the list is 'honda'. How would we change the value of this first item?

motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)
motorcycles[0] = 'ducati'
print(motorcycles)

##################################################################
 
# The code at  defines the original list, with 'honda' as the first element. The code at  changes the value of the first item to 'ducati'. The output shows that the first item has indeed been changed, and the rest of the list stays the same:
 
['honda', 'yamaha', 'suzuki']
['ducati', 'yamaha', 'suzuki']
 
# You can change the value of any item in a list, not just the first item.
# appending Elements to the End of a List
# The simplest way to add a new element to a list is to append the item to the list. 

# in the previous example, we’ll add the new element 'ducati' to the end of the list:Fu
 
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)
motorcycles.append('ducati')
print(motorcycles)


 
The append() method at  adds 'ducati' to the end of the list without affecting any of the other elements in the list:
 
['honda', 'yamaha', 'suzuki']
['honda', 'yamaha', 'suzuki', 'ducati']
 

##################################################################

# Inserting Elements into a List
# You can add a new element at any position in your list by using the insert() method. You do this by specifying the index of the new element and the value of the new item.

motorcycles = ['honda', 'yamaha', 'suzuki']
motorcycles.insert(0, 'ducati')
print(motorcycles)


# Removing Elements from a List
 
motorcycles = ['honda', 'yamaha', 'suzuki']
del motorcycles[0]
print(motorcycles)
 
# The code at  uses del to remove the first item, 'honda', from the list of motorcycles:
 
['honda', 'yamaha', 'suzuki']
['yamaha', 'suzuki'] 
 

# here’s how to remove the second item, 'yamaha', in the list:
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)
del motorcycles[1]
print(motorcycles)

# The second motorcycle is deleted from the list:
 
['honda', 'yamaha', 'suzuki']
['honda', 'suzuki']
 
# In both examples, you can no longer access the value that was removed from the list after the del statement is used.
# removing an Item Using the pop() Method
# Let’s pop a motorcycle from the list of motorcycles:
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

popped_motorcycle = motorcycles.pop()

print(motorcycles)
print(popped_motorcycle)

 
#  we pop a value from the list and store that value in the variable popped_motorcycle. We print the list at  to show that a value has been removed from the list. Then we print the popped value at  to prove that we still have access to the value that was removed.
 
['honda', 'yamaha', 'suzuki'] 
['honda', 'yamaha'] suzuki
 
# How might this pop() method be useful? Imagine that the motorcycles in the list are stored in chronological order according to when we owned them. If this is the case, we can use the pop() method to print a statement about the last motorcycle we bought:
 
motorcycles = ['honda', 'yamaha', 'suzuki'] 
last_owned = motorcycles.pop() print("The last motorcycle I owned was a " + last_owned.title() + ".")
 
# The output is a simple sentence about the most recent motorcycle we owned:
 
# Popping Items from any Position in a List

motorcycles = ['honda', 'yamaha', 'suzuki']
first_owned = motorcycles.pop(0)
print('The first motorcycle I owned was a ' + first_owned.title() + '.')


 
# Remember that each time you use pop(), the item you work with is no longer stored in the list.
# If you’re unsure whether to use the del statement or the pop() method, here’s a simple way to decide: when you want to delete an item from a list and not use that item in any way, use the del statement; if you want to use an item as you remove it, use the pop() method.
# removing an Item by Value

# For example, let’s say we want to remove the value 'ducati' from the list of motorcycles. 
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']
print(motorcycles)
motorcycles.remove('ducati')
print(motorcycles)


['honda', 'yamaha', 'suzuki', 'ducati'] 
['honda', 'yamaha', 'suzuki']  

# You can also use the remove() method to work with a value that’s being removed from a list. Let’s remove the value 'ducati' and print a reason for removing it from the list:

motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']
print(motorcycles)
too_expensive = 'ducati'
motorcycles.remove(too_expensive)
print(motorcycles)
print("\nA " + too_expensive.title() + " is too expensive for me.")
 
['honda', 'yamaha', 'suzuki', 'ducati'] 
['honda', 'yamaha', 'suzuki']
# A Ducati is too expensive for me.
 
# organizing a list
# Sorting a List Permanently with the sort() Method

cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)


##################################################################

# reverse alphabetical 

cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort(reverse=True)
print(cars)

# Sorting a List Temporarily with the sorted() Function
# To maintain the original order of a list but present it in a sorted order, you can use the sorted() function. The sorted() function lets you display your list in a particular order but doesn’t affect the actual order of the list.

cars = ['bmw', 'audi', 'toyota', 'subaru']
print("Here is the original list:")
print(cars)
print("\nHere is the sorted list:")
print(sorted(cars))
print("\nHere is the original list again:")
print(cars)


# We first print the list in its original order at 
#  and then in alphabetical order at 
# . After the list is displayed in the new order, we show that the list is still stored in its original order at . 
 
# Here is the original list: 
['bmw', 'audi', 'toyota', 'subaru'] 
# Here is the sorted list: 
['audi', 'bmw', 'subaru', 'toyota']
#  Here is the original list again:
['bmw', 'audi', 'toyota', 'subaru']
 
# Notice that the list still exists in its original order at  after the sorted() function has been used. The sorted() function can also accept a reverse=True argument if you want to display a list in reverse alphabetical order.
# by-one errors when determining the length of a list.
# introduced in this chapter at least once .
# avoiding Index errors when working with lists
# One type of error is common 

 
motorcycles = ['honda', 'yamaha', 'suzuki'] 
print(motorcycles[3])
 
# This example results in an index error:
 
Traceback (most recent call last):
  File "motorcycles.py", line 3, in <module>
    print(motorcycles[3]) IndexError: list index out of range 
 
# Python attempts to give you the item at index 3. But when it searches the list, no item in motorcycles has an index of 3. 

# Keep in mind that whenever you want to access the last item in a list you use the index -1. This will always work, even if your list has changed size since the last time you accessed it:
 
motorcycles = ['honda', 'yamaha', 'suzuki'] print(motorcycles[-1])
 
The index -1 always returns the last item in a list, in this case the value 'suzuki':
 
The only time this approach will cause an error is when you request the last item from an empty list:
 
motorcycles = [] print(motorcycles[-1])
 
No items are in motorcycles, so Python returns another index error:
 
Traceback (most recent call last): 
  File "motorcyles.py", line 3, in <module> 
    print(motorcycles[-1]) IndexError: list index out of range
 
 
4
. 
###################################################################

magicians = ['alice', 'david', 'carolina']
for magician in magicians:
    print(magician)

###################################################################

# We begin by defining a list at 
# , we define a for loop. This line tells Python to pull a name from the list magicians, and store it in the variable magician. 
#  we tell Python to print the name that was just stored in magician. 
# Python then repeats lines  and , once for each name in the list. It might help to read this code as 
# “For every magician in the list of magicians, print the magician’s name.” 
 
alice david carolina
 
For example, in a simple loop like we used in magicians.py, Python initially reads the first line of the loop:
 
This line tells Python to retrieve the first value from the list magicians and store it in the variable magician. This first value is 'alice'. Python then reads the next line:
 
Python prints the current value of magician, which is still 'alice'. Because the list contains more values, Python returns to the first line of the loop:
 
Python retrieves the next name in the list, 'david', and stores that value in magician. Python then executes the line:
 
Python prints the current value of magician again, which is now 'david'. 
Python repeats the entire loop once more with the last value in the list, 'carolina'. Because no more values are in the list, Python moves on to the next line in the program. In this case nothing comes after the for loop, so the program simply ends.

Also keep in mind when writing your own for loops that you can choose any name you want for the temporary variable that holds each value in the list. However, it’s helpful to choose a meaningful name that represents a single item from the list. For example, here’s a good way to start a for loop for a list of cats, a list of dogs, and a general list of items:
 
for cat in cats: for dog in dogs: for item in list_of_items:
 

###################################################################

magicians = ['alice', 'david', 'carolina']
for magician in magicians:
    print(magician.title() + ", that was a great trick!")

##################################################################

magicians = ['alice', 'david', 'carolina']
for sana in magicians:
    print(sana.title() + ", that was a great trick!")

 
Alice, that was a great trick! 
David, that was a great trick! 
Carolina, that was a great trick!

##################################################################
 
magicians = ['alice', 'david', 'carolina']
for magician in magicians:
    print(magician.title() + ", that was a great trick!")
    print("I can't wait to see your next trick, " + magician.title() + ".\n")
 
 
Alice, that was a great trick! 
I can't wait to see your next trick, Alice. 
David, that was a great trick! 
I can't wait to see your next trick, David. 
Carolina, that was a great trick! 
I can't wait to see your next trick, Carolina.
 
###################################################################

magicians = ['alice', 'david', 'carolina']
for magician in magicians:
    print(magician.title() + ", that was a great trick!")
    print("I can't wait to see your next trick, " + magician.title() + ".\n")
    print("Thank you, everyone. That was a great magic show!")


 
Alice, that was a great trick! 
I can't wait to see your next trick, Alice. 
David, that was a great trick! 
I can't wait to see your next trick, David. 
Carolina, that was a great trick! 
I can't wait to see your next trick, Carolina. 
Thank you, everyone. That was a great magic show!
 



##################################################################
 
making numerical lists

Using the range() Function
Python’s range() function makes it easy to generate a series of numbers. For example, you can use the range() function to print a series of numbers like this:

for value in range(1,5):
    print(value)

:
 
1
2
3
4
 

Using range() to Make a List of Numbers

numbers = list(range(1,6))
print(numbers)
[1, 2, 3, 4, 5]

We can also use the range() function to tell Python to skip numbers in a given range. For example, here’s how we would list the even numbers between 1 and 10:
even_numbers = list(range(2,11,2))
print(even_numbers)


In this example, the range() function starts with the value 2 and then adds 2 to that value. It adds 2 repeatedly until it reaches or passes the end value, 11, and produces this result:
 

Here’s how you might put the first 10 square numbers into a list:
 

squares = [] #1
for value in range(1,11): #2
    square = value ** 2 #3
    squares.append(square)#4
print(squares)#5

 
We start with an empty list called squares at . At , we tell Python to loop through each value from 1 to 10 using the range() function. Inside the loop, the current value is raised to the second power and stored in the variable square at . At , each new value of square is appended to the list squares. Finally, when the loop has finished running, the list of squares is printed at :
 
To write this code more concisely, omit the temporary variable square and append each new value directly to the list:
 
squares = []
for value in range(1,11):
    squares.append(value ** 2)

print(squares)


 
The code at  does the same work as the lines at  and  in squares.py. Each value in the loop is raised to the second power and then immediately appended to the list of squares.
You can use either of these two approaches when you’re making more complex lists. Sometimes using a temporary variable makes your code easier to read; other times it makes the code unnecessarily long. Focus first on writing code that you understand clearly, which does what you want it to do. Then look for more efficient approaches as you review your code.
List Comprehensions
. A list comprehension allows you to generate this same list in just one line of code. A list comprehension combines the for loop and the creation of new elements into one line, and automatically appends each new element. 

The following example builds the same list of square numbers you saw earlier but uses a list comprehension:
 
squares = [value ** 2 for value in range(1, 11)]
print(squares)
 	

 
 
It takes practice to write your own list comprehensions, but you’ll find them worthwhile once you become comfortable creating ordinary lists. When you’re writing three or four lines of code to generate lists and it begins to feel repetitive, consider writing your own list comprehensions.
Slicing a List
To make a slice, you specify the index of the first and last elements you want to work with. As with the range() function, Python stops one item before the second index you specify. To output the first three elements in a list, you would request indices 0 through 3, which would return elements 0, 1, and 2.

players = ['charles', 'martina', 'michael', 'florence', 'eli']
print(players[0:3])


 
if you want the second, third, and fourth items in a list, you would start the slice at index 1 and end at index 4:
 

players = ['charles', 'martina', 'michael', 'florence', 'eli']
print(players[1:4])

 
Looping Through a Slice

players = ['charles', 'martina', 'michael', 'florence', 'eli']
print("Here are the first three players on my team:")
for player in players[:3]:
    print(player.title())


Instead of looping through the entire list of players at , Python loops through only the first three names:
 
Here are the first three players on my team: 
Charles 
Martina 
Michael
 

##################################################################

# Copying a List
# For example, imagine we have a list of our favorite foods and want to make a separate list of 
# foods that a friend likes. This friend likes everything in our list so far, so we can create their list by copying ours:
 

my_foods = ['pizza', 'falafel', 'carrot cake']
friend_foods = my_foods[:]

print("My favorite foods are:")
print(my_foods)
print("\nMy friend's favorite foods are:")
print(friend_foods)

 
My favorite foods are: 
['pizza', 'falafel', 'carrot cake'] 
My friend's favorite foods are: 
['pizza', 'falafel', 'carrot cake'] 
 
# To prove that we actually have two separate lists, we’ll add a new food to each list and show that each list keeps track of 
# the appropriate person’s favorite foods:
 

my_foods = ['pizza', 'falafel', 'carrot cake'] 
friend_foods = my_foods[:]
my_foods.append('cannoli') 
friend_foods.append('ice cream')
print("My favorite foods are:")
print(my_foods)
print("\nMy friend's favorite foods are:") print(friend_foods)


 
My favorite foods are:  ['pizza', 'falafel', 'carrot cake', 'cannoli']
My friend's favorite foods are:  ['pizza', 'falafel', 'carrot cake', 'ice cream']
 
The output at  shows that 'cannoli' now appears in our list of favorite foods but 'ice cream' doesn’t. At  we can see that 'ice cream' now appears in our friend’s list but 'cannoli' doesn’t. 

If we had simply set friend_foods equal to my_foods, we would not produce two separate lists. For example, here’s what happens when you try to copy a list without using a slice:
 
my_foods = ['pizza', 'falafel', 'carrot cake']
# This doesn't work:
friend_foods = my_foods
my_foods.append('cannoli')
friend_foods.append('ice cream')
print("My favorite foods are:")
print(my_foods)
print("\nMy friend's favorite foods are:")
print(friend_foods)


 
Instead of storing a copy of my_foods in friend_foods at , we set friend_foods equal to my_foods. This syntax actually tells Python to connect the new variable friend_foods to the list that is already contained in my_foods, so now both variables point to the same list. As a result, when we add 'cannoli' to my_foods, it will also appear in friend_foods. Likewise 'ice cream' will appear in both lists, even though it appears to be added only to friend_foods.
The output shows that both lists are the same now, which is not what we wanted:
 
My favorite foods are: 
['pizza', 'falafel', 'carrot cake', 'cannoli', 'ice cream']
My friend's favorite foods are: 
['pizza', 'falafel', 'carrot cake', 'cannoli', 'ice cream']
 

tuples
Defining a Tuple
A tuple looks just like a list except you use parentheses instead of square brackets


dimensions = (200, 50)
print(dimensions[0])
print(dimensions[1])

 
200
50
 
Let’s see what happens if we try to change one of the items in the tuple dimensions:
 
dimensions = (200, 50)
 dimensions[0] = 250
 
The code at  tries to change the value of the first dimension, but Python returns a type error. Basically, because we’re trying to alter a tuple, which can’t be done to that type of object, Python tells us we can’t assign a new value to an item in a tuple:
 
Traceback (most recent call last):
  File "dimensions.py", line 3, in <module>
    dimensions[0] = 250 TypeError: 'tuple' object does not support item assignment
 
Looping Through All Values in a Tuple
 
dimensions = (200, 50)
for dimension in dimensions:
    print(dimension)



200
50

Writing over a Tuple
Although you can’t modify a tuple, you can assign a new value to a variable that holds a tuple. So if we wanted to change our dimensions, we could redefine the entire tuple:


 

dimensions = (200, 50)
print("Original dimensions:")
for dimension in dimensions:
    print(dimension)
dimensions = (400, 100)
print("\nModified dimensions:")
for dimension in dimensions:
    print(dimension)

 
The block at  defines the original tuple and prints the initial dimensions. At , we store a new tuple in the variable dimensions. We then print the new dimensions at . Python doesn’t raise any errors this time, because overwriting a variable is valid:
 
Original dimensions: 
200 
50 
Modified dimensions: 
400 
100
 
When compared with lists, tuples are simple data structures. Use them when you want to store a set of values that should not be changed throughout the life of a program.
 

5
I f s tat e m e n t s
 
a simple example

cars = ['audi', 'bmw', 'subaru', 'toyota']
for car in cars:
    if car == 'bmw':
        print(car.upper())
    else:
        print(car.title())
 

Audi 
BMW 
Subaru 
Toyota
 
Conditional tests
 

Checking for Inequality


requested_topping = 'mushrooms'

if requested_topping != 'anchovies': #!=  no 
    print("hold on anchovies")


requested_topping = 'mushrooms'

if requested_topping != 'mushrooms':
    print("hold on anchovies")

Numerical Comparisons

answer = 17
if answer != 42:
    print("That is not the correct answer. Please try again!")


##################################################################

 
Checking Whether a Value Is Not in a List


banned_users = ['andrew', 'carolina', 'david']
user = 'marie'
if user not in banned_users:
    print(user.title() + ", you can post a response if you wish.")

##################################################################

age = 19
if age >= 18:
    print("You are old enough to vote!")

##################################################################

age = 19
if age >= 18:
    print("You are old enough to vote!")
    print("Have you registered to vote yet?")

##################################################################

if-else Statements

age = 17
if age >= 18:
    print("You are old enough to vote!")
    print("Have you registered to vote yet?")
else:
    print("Sorry, you are too young to vote.")
    print("Please register to vote as soon as you turn 18!")

 
Sorry, you are too young to vote.
Please register to vote as soon as you turn 18!
 

##################################################################


age = 12
if age < 4:
    print("Your admission cost is $0.")
elif age < 18:
    print("Your admission cost is $5.")
else:
    print("Your admission cost is $10.")

 
 amusement_ 
 

age = 12
if age < 4:
    price = 0
elif age < 18:
    price = 5
else:
    price = 10
print("Your admission cost is $" + str(price) + ".")

Your admission cost is $5.
Using Multiple elif Blocks
age = 12
if age < 4:
    price = 0
elif age < 18:
    price = 5
elif age < 65:
    price = 10
else:
    price = 5
print("Your admission cost is $" + str(price) + ".")


Omitting the else Block
Python does not require an else block at the end of an if-elif chain. 

age = 12
if age < 4:
    price = 0
elif age < 18:
    price = 5
elif age < 65:
    price = 10
    price = 5
print("Your admission cost is $" + str(price) + ".")

##################################################################

Testing Multiple Conditions
The if-elif-else chain is powerful, but it’s only appropriate to use when you just need one test to pass. As soon as Python finds one test that passes, it skips the rest of the tests. 

However, sometimes it’s important to check all of the conditions of interest


requested_toppings = ['mushrooms', 'extra cheese']
if 'mushrooms' in requested_toppings:
    print("Adding mushrooms.")
if 'pepperoni' in requested_toppings:
    print("Adding pepperoni.")
if 'extra cheese' in requested_toppings:
    print("Adding extra cheese.")

print("\nFinished making your pizza!")


 
 
Adding mushrooms.
Adding extra cheese.
Finished making your pizza!
 
This code would not work properly if we used an if-elif-else block, because the code would stop running after only one test passes. Here’s what that would look like:

requested_toppings = ['mushrooms', 'extra cheese']

if 'mushrooms' in requested_toppings:
    print("Adding mushrooms.")
elif 'pepperoni' in requested_toppings:
    print("Adding pepperoni.")
elif 'extra cheese' in requested_toppings:
    print("Adding extra cheese.")
print("\nFinished making your pizza!")


 
The test for 'mushrooms' is the first test to pass, so mushrooms are added to the pizza. However, the values 'extra cheese' and 'pepperoni' are never checked, because Python doesn’t run any tests beyond the first test that passes in an if-elif-else chain. The customer’s first topping will be added, but all of their other toppings will be missed:
 
Adding mushrooms.
Finished making your pizza!
 

using if statements with lists


# The pizzeria displays a message whenever a topping is added to your pizza, as it’s being made. The code for this action can be written very efficiently by making a list of toppings the customer has requested and using a loop to announce each topping as it’s added to the pizza:
 
requested_toppings = ['mushrooms', 'green peppers', 'extra cheese']
for requested_topping in requested_toppings:
    print("Adding " + requested_topping + ".")
print("\nFinished making your pizza!")

Adding mushrooms.
Adding green peppers.
Adding extra cheese.
Finished making your pizza!

###################################################################
 
# But what if the pizzeria runs out of green peppers? An if statement inside the for loop can handle this situation appropriately:
requested_toppings = ['mushrooms', 'green peppers', 'extra cheese']
for requested_topping in requested_toppings:
    if requested_topping == 'green peppers':
        print("Sorry, we are out of green peppers right now.")
else:
        print("Adding " + requested_topping + ".")
print("\nFinished making your pizza!")



This time we check each requested item before adding it to the pizza. The code at  checks to see if the person requested green peppers. If so, we display a message informing them why they can’t have green peppers. The else block at  ensures that all other toppings will be added to the pizza.
The output shows that each requested topping is handled appropriately.
 
Adding mushrooms.
Sorry, we are out of green peppers right now.
Adding extra cheese.
Finished making your pizza!
 
Checking That a List Is Not Empty


requested_toppings = []  #create an empty list 
if requested_toppings:   # do a quick check python return true or false 
    for requested_topping in requested_toppings:
        print("Adding " + requested_topping + ".")
        print("\nFinished making your pizza!")
else:
    print("Are you sure you want a plain pizza?")

 
Using Multiple Lists
. What if a customer actually wants french fries on their pizza? 

Let’s watch out for unusual topping requests before we build a pizza. The following example defines two lists. The first is a list of available toppings at the pizzeria, and the second is the list of toppings that the user has requested. This time, each item in requested_toppings is checked against the list of available toppings before it’s added to the pizza:

 
available_toppings = ['mushrooms', 'olives', 'green peppers','pepperoni', 'pineapple', 'extra cheese']
requested_toppings = ['mushrooms', 'french fries', 'extra cheese']
for requested_topping in requested_toppings:
    if requested_topping in available_toppings:
        print("Adding " + requested_topping + ".")
    else:
        print("Sorry, we don't have " + requested_topping + ".")
print("\nFinished making your pizza!")

 
At  we define a list of available toppings at this pizzeria. Note that this could be a tuple if the pizzeria has a stable selection of toppings. At , we make a list of toppings that a customer has requested. Note the unusual request, 'french fries'. At  we loop through the list of requested toppings. Inside the loop, we first check to see if each requested topping is actually in the list of available toppings . If it is, we add that topping to the pizza. If the requested topping is not in the list of available toppings, the else block will run . The else block prints a message telling the user which toppings are unavailable.
This code syntax produces clean, informative output:
 
Adding mushrooms.
Sorry, we don't have french fries.
Adding extra cheese.
Finished making your pizza!
 
styling your if statements
 

# DICtI o n a r I e s 


alien_0 = {'color': 'green', 'points': 5}
print(alien_0['color'])
print(alien_0['points'])
green 5

###################################################################

alien_0 = {'color': 'green', 'points': 5}
new_points = alien_0['points']
print("You just earned " + str(new_points) + " points!")
 
 

alien_0 = {
    'color': 'green', 'points': 5
}

a = alien_0['points']
print(a)

Adding New Key-Value Pairs
alien_0 = {'color': 'green', 'points': 5}
print(alien_0)
alien_0['x_position'] = 0
alien_0['y_position'] = 25
print(alien_0)

 
{'color': 'green', 'points': 5}
{'color': 'green', 'points': 5, 'y_position': 25, 'x_position': 0}
 
Modifying Values in a Dictionary 

. For example, consider an alien that changes from green to yellow as a game progresses:

alien_0 = {'color': 'green'}
print("The alien is " + alien_0['color'] + ".")
alien_0['color'] = 'yellow'
print("The alien is now " + alien_0['color'] + ".")

The alien is green.
The alien is now yellow.

For a more interesting example, let’s track the position of an alien that can move at different speeds. We’ll store a value representing the alien’s current speed and then use it to determine how far to the right the alien should move:
alien_0 = {'x_position': 0, 'y_position': 25, 'speed': 'medium'}
print("Original x-position: " + str(alien_0['x_position']))

# Move the alien to the right.
# Determine how far to move the alien based on its current speed
if alien_0['speed'] == 'slow':
    x_increment = 1
elif alien_0['speed'] == 'medium':
    x_increment = 2
else:
    # This must be a fast alien
    x_increment = 3
    # The new position is the old position plus the increment.
alien_0['x_position'] = alien_0['x_position'] + x_increment
print("New x-position: " + str(alien_0['x_position']))
check above 
 
 
Original x-position: 0
New x-position: 2
 
alien = {
    'gautam': 0,
    'bikram': 25,
    'speed' : 'medium'
}

print("original" + str(alien['gautam']))

if alien ['speed'] == 'slow':
    add = 1
elif alien ['speed'] == 'medium':
    add = 2
else:
    add = 3

alien ['gautam'] = alien['gautam'] + add

print("new" + str(alien['gautam']))



Removing Key-Value Pairs:For example, let’s remove the key 'points' from the alien_0 dictionary along with its value:

alien_0 = {'color': 'green', 'points': 5}
print(alien_0)
del alien_0['points']
print(alien_0)

 
{'color': 'green', 'points': 5}
{'color': 'green'}
 
looping through a dictionary
Looping Through All Key-Value Pairs
The following dictionary would store one person’s username, first name, and last name:
 
.what if you wanted to see everything stored in this user’s dictionary? To do so, you could loop through the dictionary using a for loop:
 
user_0 = {
    'username': 'efermi',
    'first': 'enrico',
    'last': 'fermi',
    }

for key, value in user_0.items():
    print("\nKey: " + key)
    print("Value: " + value)
 
 
Key: last
Value: fermi
Key: first
Value: enrico
Key: username
Value: efermi


user_0 = {
    'username': 'efermi',
    'first': 'enrico',
    'last': 'fermi',
    }

for a, b in user_0.items():
    print("\ngautam: " + a)
    print("sana: " + b)

 
gautam: username
sana: efermi

gautam: first
sana: enrico

gautam: last
sana: fermi


 
 	favorite_languages = {
    'sarah': 'c',
    'edward': 'ruby',
    'phil': 'python',
    }
for name, language in favorite_languages.items():

    print(name.title() + "'s favorite language is " +  language.title() + ".")
 
 
Jen's favorite language is Python.
Sarah's favorite language is C.
Phil's favorite language is Python.
Edward's favorite language is Ruby.
 
sana = {
    'sarah': 'c',
    'edward': 'ruby',
    'phil': 'python',
    }
for name, language in sana.items():

    print(name + "favorite language is " +  language)



Looping Through All the Keys in a Dictionary
The keys() method is useful when you don’t need to work with all of the values in a dictionary. Let’s loop through the favorite_languages dictionary and print the names of everyone who took the poll:
favorite_languages = {
    'jen': 'python',
    'sarah': 'c',
    'edward': 'ruby',
    'phil': 'python',
    }

for name in favorite_languages.keys():
    print(name.title())

 
The line at  tells Python to pull all the keys from the dictionary favorite_languages and store them one at a time in the variable name. The output shows the names of everyone who took the poll:
 
Jen
Sarah
Phil
Edward
 
Looping through the keys is actually the default behavior when looping through a dictionary, so this code would have exactly the same output if you wrote . . . 
 
rather than . . .
 
nesting
Sometimes you’ll want to store a set of dictionaries in a list or a list of items as a value in a dictionary. This is called nesting. You can nest a set of dictionaries inside a list, a list of items inside a dictionary, or even a dictionary inside another dictionary. Nesting is a powerful feature, as the following examples will demonstrate.
A List of Dictionaries
The alien_0 dictionary contains a variety of information about one alien, but it has no room to store information about a second alien, 
alien_0 = {'color': 'green', 'points': 5}
alien_1 = {'color': 'yellow', 'points': 10}
alien_2 = {'color': 'red', 'points': 15}
aliens = [alien_0, alien_1, alien_2]
for alien in aliens:
    print(alien)


##################################################################

We first create three dictionaries, each representing a different alien. At  we pack each of these dictionaries into a list called aliens. Finally, we loop through the list and print out each alien:
 
{'color': 'green', 'points': 5} 
{'color': 'yellow', 'points': 10} 
{'color': 'red', 'points': 15}
 
A more realistic example would involve more than three aliens with code that automatically generates each alien. In the following example we use range() to create a fleet of 30 aliens:
 
#Make an empty list for storing aliens.
aliens = []
#Make 30 green aliens.
for alien_number in range(30):
    new_alien = {'color': 'green', 'points': 5, 'speed': 'slow'}
    aliens.append(new_alien)

# Show the first 5 aliens:
for alien in aliens[:5]:
    print(alien)
    print("...")
# Show how many aliens have been created.
print("Total number of aliens: " + str(len(aliens)))
This example begins with an empty list to hold all of the aliens that will be created. 
 range() returns a set of numbers, which just tells Python how many times we want the loop to repeat. Each time the loop runs we create a new alien 
 and then append each new alien to the list aliens 
 we use a slice to print the first five aliens, and then at 
 we print the length of the list to prove we’ve actually generated the full fleet of 30 aliens:

{'speed': 'slow', 'color': 'green', 'points': 5} 
{'speed': 'slow', 'color': 'green', 'points': 5} 
{'speed': 'slow', 'color': 'green', 'points': 5} 
{'speed': 'slow', 'color': 'green', 'points': 5} 
{'speed': 'slow', 'color': 'green', 'points': 5} ...
Total number of aliens: 30

, to change the first three aliens to yellow, medium-speed aliens worth 10 points each, we could do this:


# Make an empty list for storing aliens.
aliens = []

# Make 30 green aliens.
for alien_number in range (0,30):
    new_alien = {'color': 'green', 'points': 5, 'speed': 'slow'}
    aliens.append(new_alien)


for alien in aliens[0:3]:
    if alien['color'] == 'green':
        alien['color'] = 'yellow'
        alien['speed'] = 'medium'
        alien['points'] = 10


# Show the first 5 aliens:
for alien in aliens[0:5]:
    print(alien)
print("...")


 
{'speed': 'medium', 'color': 'yellow', 'points': 10} 
{'speed': 'medium', 'color': 'yellow', 'points': 10} 
{'speed': 'medium', 'color': 'yellow', 'points': 10} 
{'speed': 'slow', 'color': 'green', 'points': 5} 
{'speed': 'slow', 'color': 'green', 'points': 5} ...
 
A List in a Dictionary
pizza = {
    'crust': 'thick',
    'toppings': ['mushrooms', 'extra cheese'],
    }

print("You ordered a " + pizza['crust'] + "-crust pizza " +     "with the following toppings:")

for topping in pizza['toppings']:

    print("\t" + topping)

 

 
# You ordered a thick-crust pizza with the following toppings:     mushrooms     
# extra cheese

 

favorite_languages = {
    'jen': ['python', 'ruby'],
    'sarah': ['c'],
    'edward': ['ruby', 'go'],
    'phil': ['python', 'haskell'],
    }

for name, languages in favorite_languages.items():

    print("\n" + name.title() + "'s favorite languages are:")

    for language in languages:
        print("\t" + language.title())


 
As you can see at  the value associated with each name is now a list. Notice that some people have one favorite language and others have multiple favorites. When we loop through the dictionary at , we use the variable name languages to hold each value from the dictionary, because we know that each value will be a list. Inside the main dictionary loop, we use another for loop  to run through each person’s list of favorite languages. Now each person can list as many favorite languages as they like:
 
Jen's favorite languages are: 
    Python 
    Ruby 
Sarah's favorite languages are: 
    C 
Phil's favorite languages are: 
    Python 
    Haskell 
Edward's favorite languages are: 
    Ruby 
    Go
 



To refine this program even further, you could include an if statement at the beginning of the dictionary’s for loop to see whether each person has more than one favorite language by examining the value of len(languages). If a person has more than one favorite, the output would stay the same. If the person has only one favorite language, you could change the wording to reflect that. For example, you could say Sarah's favorite language is C.
    'aeinstein': {
        'first': 'albert',
        'last': 'einstein',
        'location': 'princeton',
        },
    'mcurie': {
        'first': 'marie',
        'last': 'curie',
        'location': 'paris',
        },
    }
 for username, user_info in users.items():
     print("\nUsername: " + username)
     full_name = user_info['first'] + " " + user_info['last']     location = user_info['location']
     print("\tFull name: " + full_name.title())     print("\tLocation: " + location.title())
 
We first define a dictionary called users with two keys: one each for the usernames 'aeinstein' and 'mcurie'. The value associated with each key is a dictionary that includes each user’s first name, last name, and location. At  we loop through the users dictionary. Python stores each key in the variable username, and the dictionary associated with each username goes into the variable user_info. Once inside the main dictionary loop, we print the username at .
At  we start accessing the inner dictionary. The variable user_info, which contains the dictionary of user information, has three keys: 'first', 
'last', and 'location'. We use each key to generate a neatly formatted full name and location for each person, and then print a summary of what we know about each user :
 
Username: aeinstein 
    Full name: Albert Einstein 
    Location: Princeton 
Username: mcurie 
    Full name: Marie Curie 
    Location: Paris
 
Notice that the structure of each user’s dictionary is identical. Although not required by Python, this structure makes nested dictionaries easier to work with. If each user’s dictionary had different keys, the code inside the for loop would be more complicated.
7


name = input("Please enter your name: ") # input() function pauses your pogram 
print("Hello, " + name + "!")


Please enter your name: Eric Hello, Eric!
 
You can store your prompt in a variable and pass that variable to the input() function.

prompt = "If you tell us who you are, we can personalize the messages you see."
prompt += "\nWhat is your first name? "
name = input(prompt)
print("\nHello, " + name + "!")

Using int() to Accept Numerical Input
 
# In this example, when we enter 21 at the prompt, Python interprets the number as a string, but the value is then converted to a numerical representation by int() . Now Python can run the conditional test: it compares age (which now contains the numerical value 21) and 18 to see if age is greater than or equal to 18. This test evaluates to True.
# How do you use the int() function in an actual program? Consider a program that determines whether people are tall enough to ride a roller coaster:

height = input("How tall are you, in inches? ")
height = int(height)
if height >= 36:
    print("\nYou're tall enough to ride!")
else:
    print("\nYou'll be able to ride when you're a little older.")



# How tall are you, in inches? 71 You're tall enough to ride!


# The modulo operator doesn’t tell you how many times one number fits into another; it just tells you what the remainder is.
# When one number is divisible by another number, the remainder is 0, so the modulo operator always returns 0. You can use this fact to determine if a number is even or odd:

number = input("Enter a number, and I'll tell you if it's even or odd: ")

number = int(number)

if number % 2 == 0:

    print("\nThe number " + str(number) + " is even.")
else:
    print("\nThe number " + str(number) + " is odd.")

###################################################################

Introducing while loops
The while Loop in Action


You can use a while loop to count up through a series of numbers. For example, the following while loop counts from 1 to 5:
a = 1

while a <=5:
    print(a)

    a += 1


In the first line, we start counting from 1 by setting the value of current_number to 1. 

The while loop is then set to keep running as long as the value of current_number is less than or equal to 5. 

The code inside the loop prints the value of current_number and then adds 1 to that value with current_number += 1. (The += operator is shorthand for current_number = current_number + 1.) 
Python repeats the loop as long as the condition current_number <= 5 is true. Because 1 is less than 5, Python prints 1 and then adds 1, making the current number 2. Because 2 is less than 5, Python prints 2 and adds 1 again, making the current number 3, and so on. Once the value of current_number is greater than 5, the loop stops running and the program ends:
1
2
3
4





 
prompt += "\nEnter 'quit' to end the program. "
 message = ""  while message != 'quit':     message = input(prompt)     print(message)
 
prompt = "\nTell me something, and I will repeat it back to you:"
prompt += "\nEnter 'quit' to end the program. "
message = ""
while message != 'quit':
    message = input(prompt)
    print(message)


 
Now the program makes a quick check before displaying the message and only prints the message if it does not match the quit value:
 
Tell me something, and I will repeat it back to you: 
Enter 'quit' to end the program. Hello everyone!
Hello everyone!
Tell me something, and I will repeat it back to you: Enter 'quit' to end the program. quit
 
Using a Flag

 
prompt = "\nTell me something, and I will repeat it back to you:"
prompt += "\nEnter 'quit' to end the program.
active = True
while active:
    message = input(prompt)
    if message == 'quit':
        active = False
    else:
        print(message)



 
We set the variable active to True 
 so the program starts in an active state. Doing so makes the while statement simpler because no comparison is made in the while statement itself; the logic is taken care of in other parts of the program. As long as the active variable remains True, the loop will continue running . 
In the if statement inside the while loop, we check the value of message once the user enters their input. If the user enters 'quit' , we set active to False, and the while loop stops. If the user enters anything other than 'quit' 
, we print their input as a message.

Using break to Exit a Loop
To exit a while loop immediately without running any remaining code in the loop, regardless of the results of any conditional test, use the break statement. 

. 
We can stop the while loop in this program by calling break as soon as the user enters the 'quit' value:

prompt = "\nPlease enter the name of a city you have visited:"
prompt += "\n(Enter 'quit' when you are finished.) "
while True:
    city = input(prompt)
    if city == 'quit':
        break
    else:
        print("I'd love to go to " + city.title() + "!")

 
 	
 
A loop that starts with while True  will run forever unless it reaches a break statement. The loop in this program continues asking the user to enter the names of cities they’ve been to until they enter 'quit'. When they enter 'quit', the break statement runs, causing Python to exit the loop:
 

Using continue in a Loop

Rather than breaking out of a loop entirely without executing the rest of its code, you can use the continue statement to return to the beginning of the loop based on the result of a conditional test. For example, consider a loop that counts from 1 to 10 but prints only the odd numbers in that range


current_number = 0
while current_number < 10:
    current_number += 1
    if current_number % 2 == 0:
        continue
    print(current_number)

 gautam = 0              #We set Gautam = 0 
while gautam < 10:       # its less than 10 pythin enters a while loop
    gautam += 1           # we incremnet by 1
    if gautam % 2 ==0:     #
        continue
    print(gautam)
First we set current_number to 0. Because it’s less than 10, Python enters the while loop. Once inside the loop, we increment the count by 1 at , so current_number is 1. The if statement then checks the modulo of current_number and 2. If the modulo is 0 (which means current_number is divisible by 2), the continue statement tells Python to ignore the rest of the loop and return to the beginning. If the current number is not divisible by 2, the rest of the loop is executed and Python prints the current number:
1 
3 
5 
7 
9
Avoiding Infinite Loops
Every while loop needs a way to stop running so it won’t continue to run forever.
For example, this counting loop should count from 1 to 5:
x = 1
while x <= 5:
    print(x)
    x += 1

 
while x <= 5:     print(x)     x += 1
 
But if you accidentally omit the line x += 1 (as shown next), the loop will run forever:
 
# This loop runs forever! x = 1 while x <= 5:     print(x)
 
Now the value of x will start at 1 but never change. As a result, the conditional test x <= 5 will always evaluate to True and the while loop will run forever, printing a series of 1s, like this:
 
1
1
1
1
--snip--
 
. If your program gets stuck in an infinite loop, press ctrl-C or just close the terminal window displaying your program’s output. 

using a while loop with lists and dictionaries
. 
Moving Items from One List to Another
Consider a list of newly registered but unverified users of a website. After we verify these users, how can we move them to a separate list of confirmed users? 
#Start with users that need to be verified,
# and an empty list to hold confirmed users.


unconfirmed_users = ['alice', 'brian', 'candace']
confirmed_users = []

# Verify each user until there are no more unconfirmed users.
# Move each verified user into the list of confirmed users.

while unconfirmed_users:
    current_user = unconfirmed_users.pop()
    print("Verifying user: " + current_user.title())
    confirmed_users.append(current_user)


# Display all confirmed users.
print("\nThe following users have been confirmed:")
for confirmed_user in confirmed_users:
    print(confirmed_user.title())

 
We begin with a list of unconfirmed users at  (Alice, Brian, and Candace) and an empty list to hold confirmed users. 
The while loop at  runs as long as the list unconfirmed_users is not empty. Within this loop, the pop() function at 

 removes unverified users one at a time from the end of unconfirmed_users. Here, because Candace is last in the unconfirmed_users list, her name will be the first to be removed, stored in current_user, and added to the confirmed_users list at . Next is Brian, then Alice.
We simulate confirming each user by printing a verification message and then adding them to the list of confirmed users. As the list of unconfirmed users shrinks, the list of confirmed users grows. When the list of unconfirmed users is empty, the loop stops and the list of confirmed users is printed:
 
Verifying user: Candace 
Verifying user: Brian 
Verifying user: Alice 
The following users have been confirmed: 
Candace 
Brian 
Alice
 
Removing All Instances of Specific Values from a List
Say you have a list of pets with the value 'cat' repeated several times. To remove all instances of that value, you can run a while loop until 'cat' is no longer in the list, as shown here:
pets = ['dog', 'cat', 'dog', 'goldfish', 'cat', 'rabbit', 'cat']
print(pets)
while 'cat' in pets:
    pets.remove('cat')
print(pets)



 
We start with a list containing multiple instances of 'cat'. After printing the list, Python enters the while loop because it finds the value 'cat' in the list at least once. Once inside the loop, Python removes the first instance of 'cat', returns to the while line, and then reenters the loop when it finds that 'cat' is still in the list. It removes each instance of 'cat' until the value is no longer in the list, at which point Python exits the loop and prints the list again:
 
['dog', 'cat', 'dog', 'goldfish', 'cat', 'rabbit', 'cat'] 
['dog', 'dog', 'goldfish', 'rabbit']
 
Filling a Dictionary with User Input
Let’s make a polling program in which each pass through the loop prompts for the participant’s name and response. 
responses = {}
#Set a flag to indicate that polling is active.

polling_active = True

while polling_active:
# Prompt for the person's name and response.
    name = input("\nWhat is your name? ")
    response = input("Which mountain would you like to climb someday? ")

# Store the response in the dictionary:
    responses[name] = response

# Find out if anyone else is going to take the poll.
    repeat = input("Would you like to let another person respond? (yes/ no) ")
    if repeat == 'no':
     polling_active = False

# Polling is complete. Show the results.
print("\n--- Poll Results ---")

for name, response in responses.items():
    print(name + " would like to climb " + response + ".")

 
 	
 
The program first defines an empty dictionary (responses) and sets a flag (polling_active) to indicate that polling is active. As long as polling_active is True, Python will run the code in the while loop. 
Within the loop, the user is prompted to enter their username and a mountain they’d like to climb . That information is stored in the responses dictionary , and the user is asked whether or not to keep the poll running . If they enter yes, the program enters the while loop again. If they enter no, the polling_active flag is set to False, the while loop stops running, and the final code block at  displays the results of the poll.
If you run this program and enter sample responses, you should see output like this:
 
What is your name? Eric 
Which mountain would you like to climb someday? Denali 
Would you like to let another person respond? (yes/ no) yes 
 
What is your name? Lynn 
Which mountain would you like to climb someday? Devil's Thumb Would you like to let another person respond? (yes/ no) no 
--- Poll Results --- Lynn would like to climb Devil's Thumb. 
Eric would like to climb Denali.
 
8
f u n C t I o n s
defining a function

Passing Information to a Function
 
def describe_pet(animal_type, pet_name):
    """Display information about a pet."""
    print("I have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
describe_pet('hamster', 'harry')
 
def gautam(type, name):

    print("I have a " +type)
    print("My name "+ name)

gautam('heman', 'bikram')
 
Multiple Function Calls
You can call a function as many times as needed. Describing a second, different pet requires just one more call to describe_pet():

def describe_pet(animal_type, pet_name):
    """Display information about a pet."""
    print("\nI have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
describe_pet('hamster', 'harry')
describe_pet('dog', 'willie')

 
I have a hamster. 
My hamster's name is Harry. 
I have a dog. 
My dog's name is Willie.
 


Order Matters in Positional arguments
You can get unexpected results if you mix up the order of the arguments in a function call when using positional arguments:


def describe_pet(animal_type, pet_name):
    """Display information about a pet."""
    print("\nI have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
describe_pet('harry', 'hamster')

In this function call we list the name first and the type of animal second. Because the argument 'harry' is listed first this time, that value is stored in the parameter animal_type. Likewise, 'hamster' is stored in pet_name. Now we have a “harry” named “Hamster”:


I have a harry. 
My harry's name is Hamster.


Keyword Arguments
A keyword argument is a name-value pair that you pass to a function. You directly associate the name and the value within the argument, so when you pass the argument to the function, there’s no confusion (you won’t end up with a harry named Hamster). 

def describe_pet(animal_type, pet_name):
    """Display information about a pet."""
    print("\nI have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
describe_pet(animal_type='hamster', pet_name='harry')



Default Values
When writing a function, you can define a default value for each parameter. If an argument for a parameter is provided in the function call, Python uses the argument value. If not, it uses the parameter’s default value

For example, if you notice that most of the calls to describe_pet() are being used to describe dogs, you can set the default value of animal_type to 'dog'. Now anyone calling describe_pet() for a dog can omit that information:

def describe_pet(pet_name, animal_type='dog'):
    """Display information about a pet."""
    print("I have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
describe_pet(pet_name='willie')


I have a dog. 
My dog's name is Willie.

The simplest way to use this function now is to provide just a dog’s name in the function call:
 
This function call would have the same output as the previous example. The only argument provided is 'willie', so it is matched up with the first parameter in the definition, pet_name. Because no argument is provided for animal_type, Python uses the default value 'dog'.

To describe an animal other than a dog, you could use a function call like this: describe_pet(pet_name='harry', animal_type='hamster')
Because an explicit argument for animal_type is provided, Python will ignore the parameter’s default value.
Equivalent Function Calls
often you’ll have several equivalent ways to call a function. Consider the following definition for describe_pets() with one default value provided:
 

Avoiding Argument Errors
. Unmatched arguments occur when you provide fewer or more arguments than a function needs to do its work. 
For example, here’s what happens if we try to call describe_pet() with no arguments:

def pet1(pet_name=, animal_type='dog'):
    print("i have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
pet1()

 
return Values
The value the function returns is called a return value. 

Returning a Simple Value
Let’s look at a function that takes a first and last name, and returns a neatly formatted full name:

def get_formatted_name(first_name, last_name):
    """Return a full name, neatly formatted."""
    full_name = first_name + ' ' + last_name
    return full_name.title()
musician = get_formatted_name('jimi', 'hendrix')
print(musician)


 
This might seem like a lot of work to get a neatly formatted name when we could have just written:
 

Making an Argument Optional

say we want to expand get_formatted_name() to handle middle names as well. A first attempt to include middle names might look like this:

def get_formatted_name(first_name, middle_name, last_name):
    """Return a full name, neatly formatted."""
    full_name = first_name + ' ' + middle_name + ' ' + last_name
    return full_name.title()


musician = get_formatted_name('john', 'lee', 'hooker')
print(musician)



 
To make the middle name optional, we can give the middle_name argument an empty default value and ignore the argument unless the user provides a value. To make get_formatted_name() work without a middle name, we set the default value of middle_name to an empty string and move it to the end of the list of parameters:

def get_formatted_name(first_name, last_name, middle_name=''):
    """Return a full name, neatly formatted."""
    if middle_name:
        full_name = first_name + ' ' + middle_name + ' ' + last_name
    else:
        full_name = first_name + ' ' + last_name
        return full_name.title()
musician = get_formatted_name('jimi', 'hendrix')
print(musician)
musician = get_formatted_name('john', 'hooker', 'lee')
print(musician)


Returning a Dictionary
, the following function takes in parts of a name and returns a dictionary representing a person:

 def build_person(first_name, last_name):
    """Return a dictionary of information about a person."""
    person = {'first': first_name, 'last': last_name}
    return person
musician = build_person('jimi', 'hendrix')
print(musician)
	

 
. You can easily extend this function to accept optional values like a middle name, an age, an occupation, or any other information you want to store about a person. For example, the following change allows you to store a person’s age as well:

def build_person(first_name, last_name, age=''):
    """Return a dictionary of information about a person."""
    person = {'first': first_name, 'last': last_name}
    if age:
        person['age'] = age
    return person
musician = build_person('jimi', 'hendrix', age=27)
print(musician)



We add a new optional parameter age to the function definition and assign the parameter an empty default value. If the function call includes a value for this parameter, the value is stored in the dictionary. This function always stores a person’s name, but it can also be modified to store any other information you want about a person.
Using a Function with a while Loop
You can use functions with all the Python structures you’ve learned about so far. For example, let’s use the get_formatted_name() function with a while loop to greet users more formally. Here’s a first attempt at greeting people using their first and last names:
def get_formatted_name(first_name, last_name):
    """Return a full name, neatly formatted."""
    full_name = first_name + ' ' + last_name
    return full_name.title()
# This is an infinite loop!

while True:
    print("\nPlease tell me your name:")
    f_name = input("First name: ")
    l_name = input("Last name: ")
    formatted_name = get_formatted_name(f_name, l_name)
    print("\nHello, " + formatted_name + "!")



But there’s one problem with this while loop: We haven’t defined a quit condition. 

def get_formatted_name(first_name, last_name):
    """Return a full name, neatly formatted."""
    full_name = first_name + ' ' + last_name
    return full_name.title()
# This is an infinite loop!
while True:
    print("\nPlease tell me your name:")
    print("(enter 'q' at any time to quit)")

    f_name = input("First name: ")
    if f_name == 'q':
        break

    l_name = input("Last name: ")
    if l_name == 'q':
        break

    formatted_name = get_formatted_name(f_name, l_name)
    print("\nHello, " + formatted_name + "!")



Passing a list


Say we have a list of users and want to print a greeting to each. The following example sends a list of names to a function called greet_users(), which greets each person in the list individually:

def greet_users(names):
    """Print a simple greeting to each user in the list."""
    for name in names:
        msg = "Hello, " + name.title() + "!"
        print(msg)

usernames = ['hannah', 'ty', 'margot']
greet_users(usernames)



 
We define greet_users() so it expects a list of names, which it stores in the parameter names. The function loops through the list it receives and prints a greeting to each user. At  we define a list of users and then pass the list usernames to greet_users()in our function call:
 
Hello, Hannah! 
Hello, Ty! 
Hello, Margot!
 

Modifying a List in a Function
Consider a company that creates 3D printed models of designs that users submit. Designs that need to be printed are stored in a list, and after being printed they’re moved to a separate list. The following code does this without using functions:

#Start with some designs that need to be printed.

unprinted_designs = ['iphone case', 'robot pendant', 'dodecahedron']
completed_models = []

# Simulate printing each design, until none are left.
#  Move each design to completed_models after printing.
while unprinted_designs:
    current_design = unprinted_designs.pop()

# Simulate creating a 3D print from the design.

print("Printing model: " + current_design)
completed_models.append(current_design)

# Display all completed models.
print("\nThe following models have been printed:")
for completed_model in completed_models:
    print(completed_model)

 
 
Printing model: dodecahedron 
Printing model: robot pendant 
Printing model: iphone case 
The following models have been printed: dodecahedron robot pendant iphone case
 
We can reorganize this code by writing two functions, each of which does one specific job. Most of the code won’t change; we’re just making it more efficient. The first function will handle printing the designs, and the second will summarize the prints that have been made:
def print_models(unprinted_designs, completed_models):
    #1 we define the function print_models()
    while unprinted_designs:
        current_design = unprinted_designs.pop()
        print("Printing model: " + current_design)

        completed_models.append(current_design)

def show_completed_models(completed_models):
#At  we define the function show_completed_models() with one parameter:
# the list of completed models. Given this list, show_completed_models()
# displays the name of each model that was printed.
    print("\nThe following models have been printed:")
    for completed_model in completed_models:
        print(completed_model)

unprinted_designs = ['iphone case', 'robot pendant', 'dodecahedron']
completed_models = []


print_models(unprinted_designs, completed_models)
show_completed_models(completed_models)


 
. Look at the body of the program to see how much easier it is to understand what this program is doing:
 
unprinted_designs = ['iphone case', 'robot pendant', 'dodecahedron'] completed_models = []
print_models(unprinted_designs, completed_models) show_completed_models(completed_models)
 
Preventing a Function from Modifying a List
Sometimes you’ll want to prevent a function from modifying a list. For example, say that you start with a list of unprinted designs and write a function to move them to a list of completed models, as in the previous example. You may decide that even though you’ve printed all the designs, you want to keep the original list of unprinted designs for your records. But because you moved all the design names out of unprinted_designs, the list is now empty, and the empty list is the only version you have; the original is gone. In this case, you can address this issue by passing the function a copy of the list, not the original. Any changes the function makes to the list will affect only the copy, leaving the original list intact.
You can send a copy of a list to a function like this:
 
The slice notation [:] makes a copy of the list to send to the function. If we didn’t want to empty the list of unprinted designs in print_models.py, we could call print_models() like this: print_models(unprinted_designs[:], completed_models)
The function print_models() can do its work because it still receives the names of all unprinted designs. But this time it uses a copy of the original unprinted designs list, not the actual unprinted_designs list. The list completed_models will fill up with the names of printed models like it did before, but the original list of unprinted designs will be unaffected by the function.
Even though you can preserve the contents of a list by passing a copy of it to your functions, you should pass the original list to functions unless you have a specific reason to pass a copy. It’s more efficient for a function to work with an existing list to avoid using the time and memory needed to make a separate copy, especially when you’re working with large lists.
Passing an arbitrary number of arguments
consider a function that builds a pizza. It needs to accept a number of toppings, but you can’t know ahead of time how many toppings a person will want. The function in the following example has one parameter, *toppings, but this parameter collects as many arguments as the calling line provides:

def make_pizza(*toppings):
    print(toppings)

make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')

 
The asterisk in the parameter name *toppings tells Python to make an empty tuple called toppings and pack whatever values it receives into this tuple. 
 
('pepperoni',) 
('mushrooms', 'green peppers', 'extra cheese')
 
Now we can replace the print statement with a loop that runs through the list of toppings and describes the pizza being ordered:
 
def make_pizza(*toppings):
    print("\nMaking a pizza with the following toppings:")
    for topping in toppings:
        print("- " + topping)

make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')


 
The function responds appropriately, whether it receives one value or three values:
 
Making a pizza with the following toppings: 
-	pepperoni 
Making a pizza with the following toppings: 
-	mushrooms 
-	green peppers 
-	extra cheese
 
This syntax works no matter how many arguments the function receives.
Mixing Positional and Arbitrary Arguments
If you want a function to accept several different kinds of arguments, the parameter that accepts an arbitrary number of arguments must be placed last in the function definition. Python matches positional and keyword arguments first and then collects any remaining arguments in the final parameter.
For example, if the function needs to take in a size for the pizza, that parameter must come before the parameter *toppings:

def make_pizza(size, *toppings):
    print("\nMaking a " + str(size) + "-inch pizza with the following toppings:")
    for topping in toppings:
        print("- " + topping)

make_pizza(16, 'pepperoni')
make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')

 
 
Making a 16-inch pizza with the following toppings: 
-	pepperoni 
Making a 12-inch pizza with the following toppings: 
-	mushrooms 
-	green peppers 
-	extra cheese

def pizza(size, *toppings):
    print("Making a " + str(size) + "-inch pizza with the following toppings:")
    for sana in toppings:
        print("- " + sana)

pizza(16, 'pepperoni')
pizza(12, 'mushrooms', 'green peppers', 'extra cheese')


 
storing your functions in modules
You can go a step further by storing your functions in a separate file called a module and then importing that module into your main program. An import statement tells Python to make the code in a module available in the currently running program file.

Importing an Entire Module
To start importing functions, we first need to create a module. A module is a file ending in .py that contains the code you want to import into your 
def make_pizza(size, *toppings):

    print("\nMaking a " + str(size) + "-inch pizza with the following toppings:")
    for topping in toppings:
        print("- " + topping)

Now we’ll make a separate file called making_pizzas.py in the same
directory as pizza.py. This file imports the module we just created and then
makes two calls to make_pizza():

9
C l a s s e s

class Robot:  # create a class called Robot 

    def introduce_self (self):  #create a funcation called introduce_self 
        print("my name is " + self.name) # we need to add self to every method to a class


r1= Robot()  #create an object and itsa attributes 
r1.name = "tom"
r1.color = "red"
r1.weight = 30

r2 = Robot()
r2.name = "Jerry"
r2.color = "blue"
r2.weight = 40


r1.introduce_self()

r2.introduce_self()


class Robot:
    def sana (self):
        print("my name is " + self.n)


r1= Robot()
r1.n = "tom"
r1.color = "red"
r1.weight = 30

r2 = Robot()
r2.n = "Jerry"
r2.color = "blue"
r2.weight = 40


r1.sana()

r2.sana()


#1 problem here we have if we miss spell name it will not work 
-----------------------
Here we create a custom constructor 

class Robot:  #create a class Robot 

    def __init__(self, name, color, weight):  #create a custom constructor 
        self.name = name                      #it will take three argumenst 
        self.color = color
        self.weight = weight

    def gautam(self):
        print("my name is " + self.color)

r1 = Robot("Tom", "red", 30) # create a new object and set its attributes 
r2 = Robot("Jerry", "blue", 40)

r2.gautam()



class Robot: #create a class Robot
    def __init__(self, n, c, w): #create a custom constructor
        self.name = n            ##it will take three argumenst
        self.color = c
        self.weight = w

    def introduce_self(self):
        print("My name is " + self.name)


class Person: #Class person         # create a new object and set its attributes
    def __init__(self, n, p, i): 
        self.name = n
        self.personality = p
        self.isSitting = i

    def sit_down(self):
        print("My name is " + self.name)


r1 = Robot("Tom", "red", 30)
r2 = Robot("Jerry", "blue", 40)

#create a new object
p1 = Person("Alice", "aggressive", False)
p2 = Person("Becky", "aggressive", True)

#now p1 own r2

p1.robot_owned = r2
p2.robot_owned = r1

p1.robot_owned.introduce_self()


#################################################################

a = 3
b = 1
guatm=  a > b:

#################################################################


# Creating the Dog Class
# Each instance created from the Dog class will store a name and an age, and we’ll give each dog the ability to sit() and roll_over():
 
class Dog(): #1
    """A simple attempt to model a dog."""#2

    def __init__(self, name, age): #3
        """Initialize name and age attributes."""
        self.name = name #4
        self.age = age

        def sit(self): #5
            """Simulate a dog sitting in response to a command."""
            print(self.name.title() + " is now sitting.")

            def roll_over(self):
                """Simulate rolling over in response to a command."""
                print(self.name.title() + " rolled over!")

 
At  we define a class called Dog. 
At  we write a docstring describing what this class does.
the __init__() Method
We define the __init__() method to have three parameters: self, name, and age. 
The self parameter is required in the method definition, and it must come first before the other parameters. 
It must be included in the definition because when Python calls this __init__() method later (to create an instance of Dog), the method call will automatically pass the self argument. 

Every method call associated with a class automatically passes self, which is a reference to the instance itself; it gives the individual instance access to the attributes and methods in the class. When we make an instance of Dog, Python will call the __init__() method from the Dog class. We’ll pass Dog() a name and an age as arguments; self is passed automatically, so we don’t need to pass it. Whenever we want to make an instance from the Dog class, we’ll provide values for only the last two parameters, name and age.

The two variables defined at  each have the prefix self. Any variable prefixed with self is available to every method in the class, and we’ll also be able to access these variables through any instance created from the class. self.name = name takes the value stored in the parameter name and stores it in the variable name, which is then attached to the instance being created. The same process happens with self.age = age. Variables that are accessible through instances like this are called attributes.
The Dog class has two other methods defined: sit() and roll_over() . Because these methods don’t need additional information like a name or age, we just define them to have one parameter, self. The instances we create later will have access to these methods. 
 
Making an Instance from a Class

class Dog():     
--snip--
 my_dog = Dog('willie', 6)
 print("My dog's name is " + my_dog.name.title() + ".")
 print("My dog is " + str(my_dog.age) + " years old.")
 
The Dog class we’re using here is the one we just wrote in the previous example. At  we tell Python to create a dog whose name is 'willie' and whose age is 6. When Python reads this line, it calls the __init__() method in Dog with the arguments 'willie' and 6. The __init__() method creates an instance representing this particular dog and sets the name and age attributes using the values we provided. The __init__() method has no explicit return statement, but Python automatically returns an instance representing this dog. We store that instance in the variable my_dog. The naming convention is helpful here: we can usually assume that a capitalized name like Dog refers to a class, and a lowercase name like my_dog refers to a single instance created from a class.
accessing attributes
To access the attributes of an instance, you use dot notation. At  we access the value of my_dog’s attribute name by writing:
 
Dot notation is used often in Python. This syntax demonstrates how 
Python finds an attribute’s value. Here Python looks at the instance my_dog 
and then finds the attribute name associated with my_dog. This is the same attribute referred to as self.name in the class Dog. At  we use the same approach to work with the attribute age. In our first print statement, my_dog.name.title() makes 'willie', the value of my_dog’s name attribute, start with a capital letter. In the second print statement, str(my_dog.age) converts 6, the value of my_dog’s age attribute, to a string.
The output is a summary of what we know about my_dog:
 
My dog's name is Willie. 
My dog is 6 years old.
 
Calling Methods
After we create an instance from the class Dog, we can use dot notation to call any method defined in Dog. Let’s make our dog sit and roll over:
 
class Dog():     
--snip--
my_dog = Dog('willie', 6)
my_dog.sit() 
my_dog.roll_over()
 
To call a method, give the name of the instance (in this case, my_dog) and the method you want to call, separated by a dot. When Python reads my_dog.sit(), it looks for the method sit() in the class Dog and runs that code. Python interprets the line my_dog.roll_over() in the same way.
Now Willie does what we tell him to:
 
Willie is now sitting. 
Willie rolled over!
 

Creating Multiple Instances
You can create as many instances from a class as you need. Let’s create a second dog called your_dog:
 
class Dog():     
--snip--
my_dog = Dog('willie', 6) 
your_dog = Dog('lucy', 3)
print("My dog's name is " + my_dog.name.title() + ".") 
print("My dog is " + str(my_dog.age) + " years old.")
my_dog.sit()
  print("\nYour dog's name is " + your_dog.name.title() + ".") 
print("Your dog is " + str(your_dog.age) + " years old.") your_dog.sit()
 
In this example we create a dog named Willie and a dog named Lucy. Each dog is a separate instance with its own set of attributes, capable of the same set of actions:
 
My dog's name is Willie. 
My dog is 6 years old. 
Willie is now sitting. 
Your dog's name is Lucy. 
Your dog is 3 years old. 
Lucy is now sitting.
 
Even if we used the same name and age for the second dog, Python would still create a separate instance from the Dog class. You can make as many instances from one class as you need, as long as you give each instance a unique variable name or it occupies a unique spot in a list or dictionary.
try It yourself
9-1. Restaurant: Make a class called Restaurant . The __init__() method for 
Restaurant should store two attributes: a restaurant_name and a cuisine_type . Make a method called describe_restaurant() that prints these two pieces of information, and a method called open_restaurant() that prints a message indicating that the restaurant is open .
Make an instance called restaurant from your class . Print the two attributes individually, and then call both methods .
9-2. Three Restaurants: Start with your class from Exercise 9-1 . Create three different instances from the class, and call describe_restaurant() for each instance .
9-3. Users: Make a class called User . Create two attributes called first_name and last_name, and then create several other attributes that are typically stored in a user profile . Make a method called describe_user() that prints a summary of the user’s information . Make another method called greet_user() that prints a personalized greeting to the user .
Create several instances representing different users, and call both methods for each user .
working with Classes and Instances

The Car Class
Let’s write a new class representing a car. Our class will store information about the kind of car we’re working with, and it 




class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year

    def get_descriptive_name(self):

      long_name = str(self.year) + ' ' + self.make + ' ' + self.model
      return long_name.title()

my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())


                          
class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year

    def gautam(self):

      long_name = str(self.year) + ' ' + self.make + ' ' + self.model
      return long_name.title()

sana = Car('audi', 'a4', 2016)
print(sana.gautam())
         
class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year

    def gautam(self):

      bikram = str(self.year) + ' ' + self.make + ' ' + self.model
      return bikram

my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.gautam())


class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year

    def gautam(self):

      bikram = str(self.year) + ' ' + self.make + ' ' + self.model
      return bikram

verna = Car('audi', 'a4', 2016)
print(verna.gautam())

 
At  in the Car class, we define the __init__() method with the self parameter first, just like we did before with our Dog class. We also give it three other parameters: make, model, and year. The __init__() method takes in these parameters and stores them in the attributes that will be associated with instances made from this class. When we make a new Car instance, we’ll need to specify a make, model, and year for our instance.
At  we define a method called get_descriptive_name() that puts a car’s year, make, and model into one string neatly describing the car. This will spare us from having to print each attribute’s value individually. To work with the attribute values in this method, we use self.make, self.model, and self.year. At  we make an instance from the Car class and store it in the variable my_new_car. Then we call get_descriptive_name() to show what kind of car we have:
 

Setting a Default Value for an Attribute
Every attribute in a class needs an initial value, even if that value is 0 or an empty string. In some cases, such as when setting a default value, it makes sense to specify this initial value in the body of the __init__() method; if you do this for an attribute, you don’t have to include a parameter for that attribute.
Let’s add an attribute called odometer_reading that always starts with a value of 0. We’ll also add a method read_odometer() that helps us read each car’s odometer:

class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year
      self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print("This car has " + str(self.odometer_reading) + " miles on it.")



my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())
my_new_car.read_odometer()


 
This time when Python calls the __init__() method to create a new instance, it stores the make, model, and year values as attributes like it did in the previous example. Then Python creates a new attribute called odometer_reading and sets its initial value to 0 . We also have a new method called read_odometer() at  that makes it easy to read a car’s mileage.
Our car starts with a mileage of 0:
 
2016 Audi A4 This car has 0 miles on it.
 
Not many cars are sold with exactly 0 miles on the odometer, so we need a way to change the value of this attribute.
Modifying Attribute Values
You can change an attribute’s value in three ways: you can change the value directly through an instance, set the value through a method, or increment the value (add a certain amount to it) through a method. Let’s look at each of these approaches.
Modifying an attribute’s Value Directly
The simplest way to modify the value of an attribute is to access the attribute directly through an instance. Here we set the odometer reading to 23 directly:
my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())

my_new_car.odometer_reading = 23
my_new_car.read_odometer()

At  we use dot notation to access the car’s odometer_reading attribute and set its value directly. This line tells Python to take the instance my_new_car, find the attribute odometer_reading associated with it, and set the value of that attribute to 23:
 
2016 Audi A4 This car has 23 miles on it.
 
Sometimes you’ll want to access attributes directly like this, but other times you’ll want to write a method that updates the value for you.
class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year
      self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print("This car has " + str(self.odometer_reading) + " miles on it.")



my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())

my_new_car.odometer_reading = 23
my_new_car.read_odometer()

Modifying an attribute’s Value through a Method
It can be helpful to have methods that update certain attributes for you. Instead of accessing the attribute directly, you pass the new value to a method that handles the updating internally.
Here’s an example showing a method called update_odometer():
class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year
      self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print("This car has " + str(self.odometer_reading) + " miles on it.")


    def update_odometer(self, mileage):
        self.odometer_reading = mileage


my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())

my_new_car.update_odometer(23)
my_new_car.read_odometer()

 
The only modification to Car is the addition of update_odometer() at . 
This method takes in a mileage value and stores it in self.odometer_reading. 
At  we call update_odometer() and give it 23 as an argument (corresponding 
to the mileage parameter in the method definition). It sets the odometer reading to 23, and read_odometer() prints the reading:
 
2016 Audi A4 This car has 23 miles on it.
 
We can extend the method update_odometer() to do additional work every time the odometer reading is modified. Let’s add a little logic to make sure no one tries to roll back the odometer reading:
 
class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year
      self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print("This car has " + str(self.odometer_reading) + " miles on it.")


    def update_odometer(self, mileage):
        self.odometer_reading = mileage

        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage

        else:
            print("You can't roll back an odometer!")


my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())

my_new_car.update_odometer(23)
my_new_car.read_odometer()
 
Now update_odometer() checks that the new reading makes sense before modifying the attribute. If the new mileage, mileage, is greater than or equal to the existing mileage, self.odometer_reading, you can update the odometer reading to the new mileage . If the new mileage is less than the existing mileage, you’ll get a warning that you can’t roll back an odometer .
Incrementing an attribute’s Value through a Method
Sometimes you’ll want to increment an attribute’s value by a certain amount rather than set an entirely new value. Say we buy a used car and put 100 miles on it between the time we buy it and the time we register it. Here’s a method that allows us to pass this incremental amount and add that value to the odometer reading:
 
class Car():

    def __init__(self, make, model, year):
      self.make = make
      self.model = model
      self.year = year
      self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print("This car has " + str(self.odometer_reading) + " miles on it.")


    def update_odometer(self, mileage):
        self.odometer_reading = mileage

        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage

        else:
            print("You can't roll back an odometer!")

    def increment_odometer(self, miles):
        self.odometer_reading += miles

my_used_car = Car('subaru', 'outback', 2013)
print(my_used_car.get_descriptive_name())

my_used_car.update_odometer(23500)
my_used_car.read_odometer()

my_used_car.increment_odometer(100)
my_used_car.read_odometer()
 
The new method increment_odometer() at  takes in a number of miles, and adds this value to self.odometer_reading. At  we create a used car, my_used_car. We set its odometer to 23,500 by calling update_odometer() and passing it 23500 at . At  we call increment_odometer() and pass it 100 to add the 100 miles that we drove between buying the car and registering it:
 
2013 Subaru Outback This car has 23500 miles on it. 
This car has 23600 miles on it.
 
You can easily modify this method to reject negative increments so no one uses this function to roll back an odometer.
note 	
Inheritance
You don’t always have to start from scratch when writing a class. If the class you’re writing is a specialized version of another class you wrote, you can use inheritance. When one class inherits from another, it automatically takes on all the attributes and methods of the first class. The original class is called the parent class, and the new class is the child class. The child class inherits every attribute and method from its parent class but is also free to define new attributes and methods of its own.
The __init__() Method for a Child Class
The first task Python has when creating an instance from a child class is to assign values to all attributes in the parent class. To do this, the __init__() method for a child class needs help from its parent class.
As an example, let’s model an electric car. An electric car is just a specific kind of car, so we can base our new ElectricCar class on the Car class we wrote earlier. Then we’ll only have to write code for the attributes and behavior specific to electric cars.
Let’s start by making a simple version of the ElectricCar class, which does everything the Car class does:
class Car():

    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print("This car has " + str(self.odometer_reading) + " miles on it.")

    def update_odometer(self, mileage):
        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage
        else:
            print("You can't roll back an odometer!")

    def increment_odometer(self, miles):
        self.odometer_reading += miles
class ElectricCar(Car):

    def __init__(self, make, model, year):

        super().__init__(make, model, year)
        
my_tesla = ElectricCar('tesla', 'model s', 2016)
print(my_tesla.get_descriptive_name())
 
At  we start with Car. When you create a child class, the parent class must be part of the current file and must appear before the child class in the file. At  we define the child class, ElectricCar. The name of the parent class must be included in parentheses in the definition of the child class. 
The __init__() method at  takes in the information required to make a Car instance.
The super() function at  is a special function that helps Python make connections between the parent and child class. This line tells Python to call the __init__() method from ElectricCar’s parent class, which gives an ElectricCar instance all the attributes of its parent class. The name super comes from a convention of calling the parent class a superclass and the child class a subclass.
We test whether inheritance is working properly by trying to create an electric car with the same kind of information we’d provide when making a regular car. At  we make an instance of the ElectricCar class, and store it in my_tesla. This line calls the __init__() method defined in ElectricCar, which in turn tells Python to call the __init__() method defined in the parent class Car. We provide the arguments 'tesla', 'model s', and 2016.
Aside from __init__(), there are no attributes or methods yet that are particular to an electric car. At this point we’re just making sure the electric car has the appropriate Car behaviors:
 
The ElectricCar instance works just like an instance of Car, so now we can begin defining attributes and methods specific to electric cars.
Inheritance in Python 2.7
In Python 2.7, inheritance is slightly different. The ElectricCar class would look like this:
 
class Car(object):     def __init__(self, make, model, year):         --snip--
class ElectricCar(Car):
    def __init__(self, make, model, year):
        super(ElectricCar, self).__init__(make, model, year)
        --snip--
 
The super() function needs two arguments: a reference to the child class and the self object. These arguments are necessary to help Python make proper connections between the parent and child classes. When you use inheritance in Python 2.7, make sure you define the parent class using the object syntax as well.
Defining Attributes and Methods for the Child Class
Once you have a child class that inherits from a parent class, you can add any new attributes and methods necessary to differentiate the child class from the parent class.
Let’s add an attribute that’s specific to electric cars (a battery, for example) and a method to report on this attribute. We’ll store the battery size and write a method that prints a description of the battery:

class Car():

        def __init__(self, make, model, year):
            self.make = make
            self.model = model
            self.year = year
            self.odometer_reading = 0

        def get_descriptive_name(self):
            long_name = str(self.year) + ' ' + self.make + ' ' + self.model
            return long_name.title()

        def read_odometer(self):
            print("This car has " + str(self.odometer_reading) + " miles on it.")

        def update_odometer(self, mileage):
            if mileage >= self.odometer_reading:
                self.odometer_reading = mileage
            else:
                print("You can't roll back an odometer!")

        def increment_odometer(self, miles):
            self.odometer_reading += miles


class ElectricCar(Car):

    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery_size = 70


    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")


my_tesla = ElectricCar('tesla', 'model s', 2016)
print(my_tesla.get_descriptive_name())
my_tesla.describe_battery()

 
 
At  we add a new attribute self.battery_size and set its initial value to, say, 70. This attribute will be associated with all instances created from the ElectricCar class but won’t be associated with any instances of Car. We also add a method called describe_battery() that prints information about the battery at . When we call this method, we get a description that is clearly specific to an electric car:
 
2016 Tesla Model S This car has a 70-kWh battery.
 
There’s no limit to how much you can specialize the ElectricCar class. You can add as many attributes and methods as you need to model an electric car to whatever degree of accuracy you need. An attribute or method that could belong to any car, rather than one that’s specific to an electric car, should be added to the Car class instead of the ElectricCar class. Then anyone who uses the Car class will have that functionality available as well, and the ElectricCar class will only contain code for the information and behavior specific to electric vehicles. Overriding Methods from the Parent Class
You can override any method from the parent class that doesn’t fit what you’re trying to model with the child class. To do this, you define a method in the child class with the same name as the method you want to override in the parent class. Python will disregard the parent class method and only pay attention to the method you define in the child class.
Say the class Car had a method called fill_gas_tank(). This method is meaningless for an all-electric vehicle, so you might want to override this method. Here’s one way to do that:
 
def ElectricCar(Car):     --snip--
    def fill_gas_tank():
        """Electric cars don't have gas tanks."""         print("This car doesn't need a gas tank!")
 
Now if someone tries to call fill_gas_tank() with an electric car, Python will ignore the method fill_gas_tank() in Car and run this code instead. When you use inheritance, you can make your child classes retain what you need and override anything you don’t need from the parent class.
Instances as Attributes
When modeling something from the real world in code, you may find that you’re adding more and more detail to a class. You’ll find that you have a growing list of attributes and methods and that your files are becoming lengthy. In these situations, you might recognize that part of one class can be written as a separate class. You can break your large class into smaller classes that work together.
For example, if we continue adding detail to the ElectricCar class, we might notice that we’re adding many attributes and methods specific to the car’s battery. When we see this happening, we can stop and move those attributes and methods to a separate class called Battery. Then we can use a Battery instance as an attribute in the ElectricCar class:
class Battery():

    def __init__(self, battery_size=70):
        self.battery_size = battery_size

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")

class ElectricCar(Car):

    def fill_gas_tank():
        print("This car doesn't need a gas tank!")

    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery_size = 70

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")



my_tesla = ElectricCar('tesla', 'model s', 2016)
print(my_tesla.get_descriptive_name())
my_tesla.describe_battery()


class Car():

        def __init__(self, make, model, year):
            self.make = make
            self.model = model
            self.year = year
            self.odometer_reading = 0

        def get_descriptive_name(self):
            long_name = str(self.year) + ' ' + self.make + ' ' + self.model
            return long_name.title()

        def read_odometer(self):
            print("This car has " + str(self.odometer_reading) + " miles on it.")

        def update_odometer(self, mileage):
            if mileage >= self.odometer_reading:
                self.odometer_reading = mileage
            else:
                print("You can't roll back an odometer!")

        def increment_odometer(self, miles):
            self.odometer_reading += miles


class Battery():

    def __init__(self, battery_size=70):
        self.battery_size = battery_size

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")

class ElectricCar(Car):

    def fill_gas_tank():
        print("This car doesn't need a gas tank!")

    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery_size = 70

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")



my_tesla = ElectricCar('tesla', 'model s', 2016)
print(my_tesla.get_descriptive_name())
my_tesla.describe_battery()


 
At  we define a new class called Battery that doesn’t inherit from any other class. The __init__() method at  has one parameter, battery_size, in addition to self. This is an optional parameter that sets the battery’s size to 
70 if no value is provided. The method describe_battery() has been moved to this class as well .
In the ElectricCar class, we now add an attribute called self.battery . This line tells Python to create a new instance of Battery (with a default size of 70, because we’re not specifying a value) and store that instance in the attribute self.battery. This will happen every time the __init__() method is called; any ElectricCar instance will now have a Battery instance created automatically.
We create an electric car and store it in the variable my_tesla. When we want to describe the battery, we need to work through the car’s battery attribute:
 
This line tells Python to look at the instance my_tesla, find its battery attribute, and call the method describe_battery() that’s associated with the Battery instance stored in the attribute.
The output is identical to what we saw previously:
 
2016 Tesla Model S This car has a 70-kWh battery.
 
This looks like a lot of extra work, but now we can describe the battery in as much detail as we want without cluttering the ElectricCar class. Let’s add another method to Battery that reports the range of the car based on the battery size:
 
class Car():
    --snip--        
        class Battery():
    --snip--
             def get_range(self):
        """Print a statement about the range this battery provides."""        if self.battery_size == 70:
            range = 240         elif self.battery_size == 85:             range = 270
            
        message = "This car can go approximately " + str(range)
        message += " miles on a full charge."
        print(message)             class ElectricCar(Car):     --snip--        
my_tesla = ElectricCar('tesla', 'model s', 2016) print(my_tesla.get_descriptive_name()) my_tesla.battery.describe_battery()
 my_tesla.battery.get_range()


class Car():

        def __init__(self, make, model, year):
            self.make = make
            self.model = model
            self.year = year
            self.odometer_reading = 0

        def get_descriptive_name(self):
            long_name = str(self.year) + ' ' + self.make + ' ' + self.model
            return long_name.title()

        def read_odometer(self):
            print("This car has " + str(self.odometer_reading) + " miles on it.")

        def update_odometer(self, mileage):
            if mileage >= self.odometer_reading:
                self.odometer_reading = mileage
            else:
                print("You can't roll back an odometer!")

        def increment_odometer(self, miles):
            self.odometer_reading += miles


class Battery():

    def __init__(self, battery_size=70):
        self.battery_size = battery_size

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")

    def get_range(self):
        if self.battery_size == 70:
            range = 240
        elif self.battery_size == 85:
            range = 270

    message = "This car can go approximately " + str(range)
    message += " miles on a full charge."
    print(message)

class ElectricCar(Car):

    def fill_gas_tank():
        print("This car doesn't need a gas tank!")

    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery = Battery()

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")

my_tesla = ElectricCar('tesla', 'model s', 2016)
print(my_tesla.get_descriptive_name())
my_tesla.battery.describe_battery()
my_tesla.battery.get_range()


 
The new method get_range() at  performs some simple analysis. If the battery’s capacity is 70 kWh, get_range() sets the range to 240 miles, and if the capacity is 85 kWh, it sets the range to 270 miles. It then reports this value. When we want to use this method, we again have to call it through the car’s battery attribute at .
The output tells us the range of the car based on its battery size:
 
2016 Tesla Model S This car has a 70-kWh battery. 
This car can go approximately 240 miles on a full charge.
 
Modeling Real-World Objects
As you begin to model more complicated items like electric cars, you’ll wrestle with interesting questions. Is the range of an electric car a property of the battery or of the car? If we’re only describing one car, it’s probably fine to maintain the association of the method get_range() with the Battery class. But if we’re describing a manufacturer’s entire line of cars, we probably want to move get_range() to the ElectricCar class. The get_range() method would still check the battery size before determining the range, but it would report a range specific to the kind of car it’s associated with. Alternatively, we could maintain the association of the get_range() method with the battery but pass it a parameter such as car_model. The get_range() method would then report a range based on the battery size and car model.
This brings you to an interesting point in your growth as a programmer. When you wrestle with questions like these, you’re thinking at a higher logical level rather than a syntax-focused level. You’re thinking not about Python, but about how to represent the real world in code. When you reach this point, you’ll realize there are often no right or wrong approaches to modeling real-world situations. Some approaches are more efficient than others, but it takes practice to find the most efficient representations. If your code is working as you want it to, you’re doing well! Don’t be discouraged if you find you’re ripping apart your classes and rewriting them several times using different approaches. In the quest to write accurate, efficient code, everyone goes through this process.
Importing Classes
To help, Python lets you store classes in modules and then import the classes you need into your main program.
Importing a Single Class
Let’s create a module containing just the Car class. This brings up a subtle naming issue: we already have a file named car.py in this chapter, but this module should be named car.py because it contains code representing a car. We’ll resolve this naming issue by storing the Car class in a module named car.py, replacing the car.py file we were previously using. From now on, any program that uses this module will need a more specific filename, such as my_car.py. Here’s car.py with just the code from the class Car:
 
class Car():

        def __init__(self, make, model, year):
            self.make = make
            self.model = model
            self.year = year
            self.odometer_reading = 0

        def get_descriptive_name(self):
            long_name = str(self.year) + ' ' + self.make + ' ' + self.model
            return long_name.title()

        def read_odometer(self):
            print("This car has " + str(self.odometer_reading) + " miles on it.")


        def update_odometer(self, mileage):
            if mileage >= self.odometer_reading:
                self.odometer_reading = mileage
            else:
                print("You can't roll back an odometer!")

        def increment_odometer(self, miles):
            self.odometer_reading += miles
      
 
At  we include a module-level docstring that briefly describes the contents of this module. You should write a docstring for each module you create.
Now we make a separate file called my_car.py. This file will import the Car class and then create an instance from that class:
 
   my_car.py   from car import Car
my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())
my_new_car.odometer_reading = 23
my_new_car.read_odometer()



 
The import statement at  tells Python to open the car module and import the class Car. Now we can use the Car class as if it were defined in this file. The output is the same as we saw earlier:
 
2016 Audi A4 This car has 23 miles on it.
 
Importing classes is an effective way to program. Picture how long this program file would be if the entire Car class were included. When you instead move the class to a module and import the module, you still get all the same functionality, but you keep your main program file clean and easy to read. You also store most of the logic in separate files; once your classes work as you want them to, you can leave those files alone and focus on the higher-level logic of your main program.
Storing Multiple Classes in a Module
You can store as many classes as you need in a single module, although each class in a module should be related somehow. The classes Battery and ElectricCar both help represent cars, so let’s add them to the module car.py:
 
 	car.py 	"""A set of classes used to represent gas and electric cars."""
class Car():
    --snip--        
        class Battery():     """A simple attempt to model a battery for an electric car."""
    class Battery():

    def __init__(self, battery_size=60):
        self.battery_size = battery_size

    def describe_battery(self):
        print("This car has a " + str(self.battery_size) + "-kWh battery.")

    def get_range(self):
        if self.battery_size == 70:
            range = 240
        elif self.battery_size == 85:
            range = 270

        message = "This car can go approximately " + str(range)
        message += " miles on a full charge."
        print(message)

class ElectricCar(Car):

    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery = Battery()

 
Now we can make a new file called my_electric_car.py, import the ElectricCar class, and make an electric car:
 
 my_electric_ 
 	car.py	from car import ElectricCar

my_tesla = ElectricCar('tesla', 'model s', 2016)
print(my_tesla.get_descriptive_name())
my_tesla.battery.describe_battery()
my_tesla.battery.get_range()

 
This has the same output we saw earlier, even though most of the logic is hidden away in a module:
 
2016 Tesla Model S This car has a 70-kWh battery. 
This car can go approximately 240 miles on a full charge.
 
Importing Multiple Classes from a Module
You can import as many classes as you need into a program file. If we want to make a regular car and an electric car in the same file, we need to import both classes, Car and ElectricCar:
 
  my_cars.py   from car import Car, ElectricCar

my_beetle = Car('volkswagen', 'beetle', 2016) 
print(my_beetle.get_descriptive_name())
my_tesla = ElectricCar('tesla', 'roadster', 2016) 
print(my_tesla.get_descriptive_name())

 
You import multiple classes from a module by separating each class with a comma . Once you’ve imported the necessary classes, you’re free to make as many instances of each class as you need.
In this example we make a regular Volkswagen Beetle at  and an electric Tesla Roadster at :
 
2016 Volkswagen Beetle 
2016 Tesla Roadster
 
Importing an Entire Module
You can also import an entire module and then access the classes you need using dot notation. This approach is simple and results in code that is easy to read. Because every call that creates an instance of a class includes the module name, you won’t have naming conflicts with any names used in the current file.
Here’s what it looks like to import the entire car module and then create a regular car and an electric car:
 
  my_cars.py   import car
my_beetle = car.Car('volkswagen', 'beetle', 2016) 
print(my_beetle.get_descriptive_name())
my_tesla = car.ElectricCar('tesla', 'roadster', 2016) 
print(my_tesla.get_descriptive_name())
 
At  we import the entire car module. We then access the classes we need through the module_name.class_name syntax. At  we again create a Volkswagen Beetle, and at  we create a Tesla Roadster.
Importing All Classes from a Module
You can import every class from a module using the following syntax:
 
This method is not recommended for two reasons. First, it’s helpful to be able to read the import statements at the top of a file and get a clear sense of which classes a program uses. With this approach it’s unclear which classes you’re using from the module. This approach can also lead to confusion with names in the file. If you accidentally import a class with the same name as something else in your program file, you can create errors that are hard to diagnose. I show this here because even though it’s not a recommended approach, you’re likely to see it in other people’s code.
If you need to import many classes from a module, you’re better off importing the entire module and using the module_name.class_name syntax. 
You won’t see all the classes used at the top of the file, but you’ll see clearly where the module is used in the program. You’ll also avoid the potential naming conflicts that can arise when you import every class in a module.
Importing a Module into a Module
Sometimes you’ll want to spread out your classes over several modules to keep any one file from growing too large and avoid storing unrelated classes in the same module. When you store your classes in several modules, you may find that a class in one module depends on a class in another module. When this happens, you can import the required class into the first module.
For example, let’s store the Car class in one module and the ElectricCar and Battery classes in a separate module. We’ll make a new module called electric_car.py—replacing the electric_car.py file we created earlier—and copy just the Battery and ElectricCar classes into this file:
 
 electric_car.py 	"""A set of classes that can be used to represent electric cars."""
 from car import Car
class Battery():
    --snip-            class ElectricCar(Car):     --snip--
 
The class ElectricCar needs access to its parent class Car, so we import Car directly into the module at . If we forget this line, Python will raise an error when we try to make an ElectricCar instance. We also need to update the Car module so it contains only the Car class:
 
 	car.py 	"""A class that can be used to represent a car."""
class Car():     --snip--
 
Now we can import from each module separately and create whatever kind of car we need:
 
  my_cars.py   from car import Car from electric_car import ElectricCar
my_beetle = Car('volkswagen', 'beetle', 2016) print(my_beetle.get_descriptive_name())
my_tesla = ElectricCar('tesla', 'roadster', 2016)
print(my_tesla.get_descriptive_name())
 
At  we import Car from its module, and ElectricCar from its module. We then create one regular car and one electric car. Both kinds of cars are created correctly:
 
2016 Volkswagen Beetle 
2016 Tesla Roadster
 
Finding Your Own Workflow
As you can see, Python gives you many options for how to structure code in a large project. It’s important to know all these possibilities so you can determine the best ways to organize your projects as well as understand other people’s projects.
When you’re starting out, keep your code structure simple. Try doing everything in one file and moving your classes to separate modules once everything is working. If you like how modules and files interact, try storing your classes in modules when you start a project. Find an approach that lets you write code that works, and go from there.
