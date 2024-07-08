

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

# answer 17

#################################################################


# what if there is no negative example 
given_list = [5, 4 , 4 , 4 , 3,]

total = 0

i = 0

while given_list[i] > 0:
    total += given_list[i]
    i += 1 # increment i with 1
    print(total)


# error 


#################################################################
# what if there is no negative example 


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
#

a = ["apple", "banana", "republic"]
for element in a:
    print(element)
	
# apple
# banana
# republic

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


# -7
# -12
# -15
# -17



#################################################################
# List

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles)

['trek', 'cannondale', 'redline', 'specialized'] 
bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0])


# ['trek', 'cannondale', 'redline', 'specialized']
# trek

#################################################################

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0].title())


# trek
 
################################################################# 

bicycles = ['trek', 'cannondale', 'redline', 'specialized']
print(bicycles[0].title())
print(bicycles[3])

# Trek
# specialized

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


# Inserting Elements into a List
# You can add a new element at any position in your list by using the insert() method. You do this by specifying the index of the new element and the value of the new item.

motorcycles = ['honda', 'yamaha', 'suzuki']
motorcycles.insert(0, 'ducati')
print(motorcycles)

##################################################################

# Removing Elements from a List

motorcycles = ['honda', 'yamaha', 'suzuki']
del motorcycles[0]
print(motorcycles)

# The code at  uses del to remove the first item, 'honda', from the list of motorcycles:
 
['honda', 'yamaha', 'suzuki']
['yamaha', 'suzuki'] 
 
##################################################################

# here’s how to remove the second item, 'yamaha', in the list:


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

 
# Alice, that was a great trick! 
# David, that was a great trick! 
# Carolina, that was a great trick!

##################################################################
 
magicians = ['alice', 'david', 'carolina']
for magician in magicians:
    print(magician.title() + ", that was a great trick!")
    print("I can't wait to see your next trick, " + magician.title() + ".\n")
 
 
# Alice, that was a great trick! 
# I can't wait to see your next trick, Alice. 
# David, that was a great trick! 
# I can't wait to see your next trick, David. 
# Carolina, that was a great trick! 
# I can't wait to see your next trick, Carolina.
 
###################################################################

magicians = ['alice', 'david', 'carolina']
for magician in magicians:
    print(magician.title() + ", that was a great trick!")
    print("I can't wait to see your next trick, " + magician.title() + ".\n")
    print("Thank you, everyone. That was a great magic show!")


 
# Alice, that was a great trick! 
# I can't wait to see your next trick, Alice. 
# David, that was a great trick! 
# I can't wait to see your next trick, David. 
# Carolina, that was a great trick! 
# I can't wait to see your next trick, Carolina. 
# Thank you, everyone. That was a great magic show!
 



##################################################################
 
# making numerical lists

# Using the range() Function
# Python’s range() function makes it easy to generate a series of numbers. For example, you can use the range() function to print a series of numbers like this:

for value in range(1,5):
    print(value)


 
# 1
# 2
# 3
# 4
 




# In this example, the range() function starts with the value 2 and then adds 2 to that value. It adds 2 repeatedly until it reaches or passes the end value, 11, and produces this result:
 

# Here’s how you might put the first 10 square numbers into a list:
 

squares = [] #1
for value in range(1,11): #2
    square = value ** 2 #3
    squares.append(square)#4
print(squares)#5

 
# We start with an empty list called squares at . At , we tell Python to loop through each value from 1 to 10 using the range() function. Inside the loop, the current value is raised to the second power and stored in the variable square at . At , each new value of square is appended to the list squares. Finally, when the loop has finished running, the list of squares is printed at :
 
# To write this code more concisely, omit the temporary variable square and append each new value directly to the list:
 
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

##################################################################

# My favorite foods are: 
# ['pizza', 'falafel', 'carrot cake'] 
# My friend's favorite foods are: 
# ['pizza', 'falafel', 'carrot cake'] 
 
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
 

# Audi 
# BMW 
# Subaru 
# Toyota
 
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

 
# Sorry, you are too young to vote.
# Please register to vote as soon as you turn 18!
 

##################################################################


age = 12
if age < 4:
    print("Your admission cost is $0.")
elif age < 18:
    print("Your admission cost is $5.")
else:
    print("Your admission cost is $10.")

##################################################################
 

age = 12
if age < 4:
    price = 0
elif age < 18:
    price = 5
else:
    price = 10
print("Your admission cost is $" + str(price) + ".")

# Your admission cost is $5.
# Using Multiple elif Blocks
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


# Omitting the else Block
# Python does not require an else block at the end of an if-elif chain. 

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

# Testing Multiple Conditions
# The if-elif-else chain is powerful, but it’s only appropriate to use when you just need one test to pass. As soon as Python finds one test that passes, it skips the rest of the tests. 

# However, sometimes it’s important to check all of the conditions of interest


requested_toppings = ['mushrooms', 'extra cheese']
if 'mushrooms' in requested_toppings:
    print("Adding mushrooms.")
if 'pepperoni' in requested_toppings:
    print("Adding pepperoni.")
if 'extra cheese' in requested_toppings:
    print("Adding extra cheese.")

print("\nFinished making your pizza!")


 
 
# Adding mushrooms.
# Adding extra cheese.
# Finished making your pizza!
 
# This code would not work properly if we used an if-elif-else block, because the code would stop running after only one test passes. Here’s what that would look like:

requested_toppings = ['mushrooms', 'extra cheese']

if 'mushrooms' in requested_toppings:
    print("Adding mushrooms.")
elif 'pepperoni' in requested_toppings:
    print("Adding pepperoni.")
elif 'extra cheese' in requested_toppings:
    print("Adding extra cheese.")
print("\nFinished making your pizza!")


 
# The test for 'mushrooms' is the first test to pass, so mushrooms are added to the pizza. However, the values 'extra cheese' and 'pepperoni' are never checked, because Python doesn’t run any tests beyond the first test that passes in an if-elif-else chain. The customer’s first topping will be added, but all of their other toppings will be missed:
 
# Adding mushrooms.
# Finished making your pizza!
 

# using if statements with lists


# The pizzeria displays a message whenever a topping is added to your pizza, as it’s being made. The code for this action can be written very efficiently by making a list of toppings the customer has requested and using a loop to announce each topping as it’s added to the pizza:
 
requested_toppings = ['mushrooms', 'green peppers', 'extra cheese']
for requested_topping in requested_toppings:
    print("Adding " + requested_topping + ".")
print("\nFinished making your pizza!")

# Adding mushrooms.
# Adding green peppers.
# Adding extra cheese.
# Finished making your pizza!

###################################################################
 
