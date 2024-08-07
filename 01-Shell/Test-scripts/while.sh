# !/bin/bash

# filename="example.tfvars"

# if [ ! -f "$filename" ]; then
#     echo "File '$filename' does not exist."
# else
#     echo "File '$filename' exists."
# fi

############################################

# while IFS= read -r line; do
#     # Commands to process each line
#     echo "$line"
# done < a.tfvars

######################################

# while IFS=, read -r line; do
#     [[ -z "$line" || "$line" =~ ^#  ]] && continue
#     # Commands to process non-empty, non-comment lines
#     echo  $line
# done <  a.tfvars

###############################
!/bin/bash

filename="a.tfvars"

while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^\# ]]; then
        continue
    fi

    # Extract key and value
    key=$(echo "$line" | cut -d '=' -f 1 | xargs)
    value=$(echo "$line" | cut -d '=' -f 2 | xargs)

    # Print or use the key-value pair
    echo "Key: $key, Value: $value"
    # Example usage: export the variable
    export "$key"="$value"
done < "$filename"


# echo "##vso[task.setvariable variable=$key]$value"