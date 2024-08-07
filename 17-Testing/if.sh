045

!/bin/bash

filename="example.tfvars"

if [ ! -f "$filename" ]; then
    echo "File '$filename' does not exist."
else
    echo "File '$filename' exists."
fi

while IFS= read -r line; do

if [[ "$line" =~ ^\# ]]; then
    continue

while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    # Commands to process non-empty, non-comment lines
    echo "Processing: $line"
done < example.tfvars

!/bin/bash

filename="example.tfvars"

while IFS= read -r line; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^\# ]] || [[ -z "$line" ]]; then
        continue
    fi

    # Extract key and value
    key=$(echo "$line" | cut -d '=' -f 1 | xargs)
    value=$(echo "$line" | cut -d '=' -f 2 | xargs)

    # Output the key-value pair
    echo " $key: $value"

done < "$filename"