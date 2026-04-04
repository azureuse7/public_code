#!/bin/bash

filename="a.tfvars"

while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^\# ]]; then
        continue
    fi

    # Extract key and value
    key=$(echo "$line" | cut -d '=' -f 1 | xargs)
    value=$(echo "$line" | cut -d '=' -f 2 | xargs)

    echo "Key: $key, Value: $value"
    export "$key"="$value"
done < "$filename"
