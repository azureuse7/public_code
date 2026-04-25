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
 
