# function a collection of instructions or collection of code

def function1():    #define a function we called it function1
    print("ahhhh")
    print("ahhhhh 2")
print("this is outside the function")


function1() #call the function 

#################################################################
# Mapping input or an argument

def function2(x):   # define a function called function 2 which will take an agrugmnet
                    # called x,  when when in  return 
    return 2 * x    # return 2 times x

a = function2(3)  # to call this funaction
    # return value or output

print(a)  # we see 6

#################################################################

def function3(x, y):    # define a funcation i.e 3 this functaion will take two
                        # two arugmnets x y
    return x + y        # return x and y

e = function3(1, 2)
print(e)  # 3

#################################################################

def function4(x):
    print(x)
    print("still in this function")

    return 3*x

f = function4(4)

#################################################################	
	
	
def function5(some_argument):
    print(some_argument)
    print("weeee")

function5(4)
	
#################################################################    


#   BMI calculator
name1 = "YK"
height_m1 = 2
weight_kg1 = 90

name2 = "YK's sister"
height_m2 = 1.8
weight_kg2 = 70

name3 = "YK's brother"
height_m3 = 2.5
weight_kg3 = 160


def bmi_calculator(name, height_m, weight_kg):
    bmi = weight_kg / (height_m ** 2)
    print("bmi: ")
    print(bmi)
    if bmi < 25:
        return name + " is not overweight"
    else:
        return name + " is overweight"
result1 = bmi_calculator(name1, height_m1, weight_kg1)
result2 = bmi_calculator(name2, height_m2, weight_kg2)
result3 = bmi_calculator(name3, height_m3, weight_kg3)
print(result1)
print(result2)
print(result3)

#################################################################	

# The following function converts miles to kilometers.
# km = 1.6 * miles
def convert(miles):
    return 1.6 * miles

print(convert(1))  #1.6
print(convert(2)) #3.2

Lists 
	
a = [3, 10, -1]
print(a)

a.append(1)
print(a)

#[3, 10, -1, 1]

a = [3, 10, -1]
print(a)

a.append(1)
print(a)

#[3, 10, -1, 1]

a.append("hello")
print(a)

print(a[0])

#######################################################