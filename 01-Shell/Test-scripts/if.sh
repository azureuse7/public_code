# !/bin/bash

# filename="example.tfvars"

# if [ -e "$filename" ]; then
#     echo "File '$filename' exists."
# else
#     echo "File '$filename' does not exist."
# fi

# !/bin/bash

filename="example.tfvars"

if [ ! -f "$filename" ]; then
    echo "File '$filename' does not exist."
else
    echo "File '$filename' exists."
fi
