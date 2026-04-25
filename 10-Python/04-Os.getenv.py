use of os.getenv() method
# Python program to explain os.getenv() method 
    
# importing os module 
import os
  
# Get the value of 'HOME'
# environment variable
key = 'HOME'
value = os.getenv(key)
  
# Print the value of 'HOME'
# environment variable
print("Value of 'HOME' environment variable :", value) 
  
# Get the value of 'JAVA_HOME'
# environment variable
key = 'JAVA_HOME'
value = os.getenv(key)
  
# Print the value of 'JAVA_HOME'
# environment variable
print("Value of 'JAVA_HOME' environment variable :", value) 
Output:


Value of 'HOME' environment variable : /home/ihritik
Value of 'JAVA_HOME' environment variable : /opt/jdk-10.0.1