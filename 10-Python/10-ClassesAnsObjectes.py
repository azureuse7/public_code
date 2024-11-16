# Robert is the class
# With Three Attribute name, colour and weight
# function introduce_self


class Robot:
    def introduce_self(self):
        print("My name is " + self.name)

# Out of the class with have two objects r1 and r and with below Attribute
r1 = Robot()
r1.name = "Tom"
r1.color = "red"
r1.weight = 30

r2 = Robot()
r2.name = "Jerry"
r2.color = "blue"

r1.introduce_self()
r2.introduce_self()
# output "My name is Tom"
# output "My name is Jerry"

####################################### 


class Robot:
    def __init__(self, name1, color, weight):
        self.name = name1
        self.color = color
        self.weight = weight

    def introduce_self(self):
        print("My name is " + self.name)

r1 = Robot("Tom", "red", 30)
r2 = Robot("Jerry", "blue", 40)


r1.introduce_self()
r2.introduce_self()

####################################### 
# Robert is the class
# With Three Attribute name, colour and weight
# function introduce_self


class Robot:
    def __init__(self, n, c, w):
        self.name = n
        self.color = c
        self.weight = w

    def introduce_self(self):
        print("My name is " + self.name)


class Person:
    def __init__(self, n, p, i):
        self.name = n
        self.personality = p
        self.isSitting = i

    def sit_down(self):
        print("My name is " + self.name)


r1 = Robot("Tom", "red", 30)
r2 = Robot("Jerry", "blue", 40)

p1 = Person("Alice", "aggressive", False)
p2 = Person("Becky", "aggressive", True)

p1.robot_owned = r2
p2.robot_owned = r1


p1.robot_owned.introduce_self()


####################################### 
class Person:
    def __init__(self, name, age):
        self.name = name  # Instance attribute
        self.age = age    # Instance attribute

    def greet(self):
        return f"Hello, my name is {self.name}." 


person1 = Person("Alice", 30)
print(person1.greet())  # Output: Hello, my name is Alice.


####################################### 

#### Inheritance

# - Inheritance allows a new class to inherit attributes and methods from an existing class.


class Animal:
    def eat(self):
        return "This animal is eating."

class Dog(Animal):  # Dog inherits from Animal
    def bark(self):
        return "Woof!"

dog = Dog()
print(dog.eat())   # Output: This animal is eating.
print(dog.bark())  # Output: Woof!


#### Encapsulation

# - Encapsulation restricts access to methods and variables to prevent data from direct modification.



class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Private attribute

    def deposit(self, amount):
        self.__balance += amount

    def get_balance(self):
        return self.__balance

account = BankAccount(1000)
account.deposit(500)
print(account.get_balance())  # Output: 1500

#### Polymorphism

#  Polymorphism allows methods to use objects of different types.


class Cat:
    def speak(self):
        return "Meow!"

class Dog:
    def speak(self):
        return "Woof!"

def make_sound(animal):
    print(animal.speak())

cat = Cat()
dog = Dog()

make_sound(cat)  # Output: Meow!
make_sound(dog)  # Output: Woof!


#### Special Methods (Magic Methods)

# - Special methods allow you to define how objects of your class behave with built-in functions and operators.

# Common Special Methods:
# __str__(self): Defines behavior for str() and print().
# __len__(self): Defines behavior for len().
# __add__(self, other): Defines behavior for the + operator.

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(2, 4)
v2 = Vector(3, -1)
v3 = v1 + v2
print(v3)  # Output: Vector(5, 3)

#### Class vs. Instance Attributes

# Class Attributes: Shared by all instances of the class.
# Instance Attributes: Unique to each instance.


class Car:
    wheels = 4  # Class attribute

    def __init__(self, color):
        self.color = color  # Instance attribute

car1 = Car("red")
car2 = Car("blue")

print(car1.wheels)  # Output: 4
print(car2.wheels)  # Output: 4
print(car1.color)   # Output: red
print(car2.color)   # Output: blue
# Access Modifiers in Python
# ```

# While Python doesn't enforce access modifiers, naming conventions indicate the intended level of access:

# Public: No underscores (e.g., name)
# Protected: Single underscore prefix (e.g., _name)
# Private: Double underscore prefix (e.g., __name)
# Static Methods and Class Methods

# Static Methods: Defined using @staticmethod. They don't access instance (self) or class (cls) variables.
# Class Methods: Defined using @classmethod. They receive the class (cls) as the first argument instead of the instance.


class MathOperations:
    @staticmethod
    def add(a, b):
        return a + b

    @classmethod
    def info(cls):
        return f"This is a {cls.__name__} class."

print(MathOperations.add(5, 7))   # Output: 12
print(MathOperations.info())      # Output: This is a MathOperations 

#### Summary

# Classes: Templates for creating objects.
# Objects: Instances of classes.
# Attributes: Variables that hold data.
# Methods: Functions that perform actions.
# Inheritance: Mechanism to create a new class using details of an existing class.
# Encapsulation: Restricting access to methods and variables.
# Polymorphism: Ability to use a common interface for multiple forms (data types).
# Further Resources

# Official Python Documentation on Classes
# Python OOP Tutorial
# Learn Python Classes and Objects
# By understanding and utilizing classes in Python, you can write code that is more modular, reusable, and easier to maintain.











