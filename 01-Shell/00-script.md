```bash
script: |
    # Path to the .tfvars file
    TF_VARS_FILE="$(Build.SourcesDirectory)/path/to/your/terraform.tfvars"

    # Check if file exists
    if [ ! -f "$TF_VARS_FILE" ]; then
    echo "TFVars file does not exist: $TF_VARS_FILE"
    exit 1
    fi

    # Read each line from the .tfvars file
    while IFS= read -r line; do
    # Ignore lines that start with '#' (comments)
    if [[ "$line" =~ ^\# ]]; then
        continue
    fi
    # Extract the key and value
    key=$(echo "$line" | cut -d '=' -f 1 | xargs)
    value=$(echo "$line" | cut -d '=' -f 2 | xargs)

    # Use Azure DevOps logging command to set variable for the entire pipeline
    echo "##vso[task.setvariable variable=$key;isOutput=true]$value"
    done < "$TF_VARS_FILE"
```


```bash
# Check if file exists
if [ ! -f "$TF_VARS_FILE" ]; then
echo "TFVars file does not exist: $TF_VARS_FILE"
exit 1
fi 
```
#### Components of the Code
1) **if**: This introduces the conditional statement. 

2) **[ ! -f "$TF_VARS_FILE" ]:**

- [ ]: These square brackets denote a test (or conditional expression) in Bash. They are used to evaluate a condition.
-  "**!**"This is a logical NOT operator. It negates the result of the test expression that follows it. So if the test expression evaluates to true, ! changes it to false, and vice versa.
-  "**-f**" **"TF_VARS_FILE"** This tests if the path specified by the variable TF_VARS_FILE is a file.
   -  **-f**: This is a file test operator that checks if a specified file exists and is a regular file (not a directory or a device)
   -  **"TF_VARS_FILE"**: This is the path to the file being checked. It is a variable that should contain the full path or relative path to the file. The quotes around the variable are used to handle any spaces or special characters in the filename or path correctly.
#### Explanation of the Logic
 The conditional expression **[ ! -f "$TF_VARS_FILE" ]** checks:

- Whether the file specified by **TF_VARS_FILE does not exist**.
- If the file does not exist ****(-f "$TF_VARS_FILE" returns false)****, the **!** operator negates this to true, causing the **if** statement to execute the enclosed block of commands.

##### Extended Example
Here’s a more complete example using this condition:

```bash
if [ ! -f "$TF_VARS_FILE" ]; then
    echo "Error: Configuration file not found at $TF_VARS_FILE."
    exit 1  # Exit the script with a status of 1 (indicates an error)
else
    echo "Processing configuration file: $TF_VARS_FILE."
    # Proceed with processing the file
fi
```
In this example:

- If the file does not exist, an error message is printed, and the script exits with a status code of 1, which generally signifies an error.
- If the file exists, it prints a confirmation message, and the script would continue to process the file as intended.
This type of conditional is essential in scripts to ensure robust error handling and to prevent runtime errors due to missing files.


## Reading the File Line by Line
```bash
# Read each line from the .tfvars file
while IFS= read -r line; do
```

##### while IFS= read -r line; do: This line initiates a loop that reads the .tfvars file line by line.

- **IFS**=: Sets the Internal Field Separator to an empty value, ensuring that leading and trailing whitespace are preserved in each line
- **Line**: In Bash scripting, the term **line** typically refers to a variable used to store a single line of text, often from a file or input stream
- **read -r line**: Reads a line into the variable **line**. 
- The **-r** flag prevents backslashes from escaping any characters, preserving the input line as is.

### Ignoring Comment Lines
```bash
# Ignore lines that start with '#' (comments)
if [[ "$line" =~ ^\# ]]; then
    continue
fi
```
- **"$line"**: This is a variable that typically holds a line of text, often obtained from a file or input stream (e.g., from a **while** loop reading a file line by line).

- **=~:** This operator is used for regex matching in Bash. It checks whether the string on the left matches the pattern on the right.

- **^:** In regular expressions, ^ denotes the start of a string. Thus, **^#** matches any string starting with a **#**.

- **\#:** The # character is escaped with a backslash (\) because it is a special character in Bash that denotes the start of a comment. Escaping it ensures it is treated literally in the regex pattern.

- **continue**: This command is used to skip the rest of the commands in the current loop iteration and proceed with the next iteration. In this context, it effectively skips processing lines that start with #.

#### Context
- This pattern is commonly used in scripts that process configuration files, scripts, or data files where lines starting with # are comments. 
- Here’s a full example of how it might be used in a script:

### Example: Skipping Comment Lines
```bash
#!/bin/bash

# This script reads a file line by line and skips lines starting with '#'

filename="config.txt"

while IFS= read -r line; do
    # Skip lines starting with '#'
    if [[ "$line" =~ ^\# ]]; then
        continue
    fi

    # Process the non-comment line
    echo "Processing: $line"

done < "$filename"
```
#### How It Works
**1)Reading the File**: The script reads config.txt line by line using a while loop.

**02)Checking for Comments**: Each line is checked to see if it begins with # using the regex ^#.

**03)Skipping Comments**: If the line starts with #, the continue command skips the rest of the loop body for that iteration and moves to the next line.

**04)Processing Lines**: Lines that do not start with # are processed (in this example, simply printed).

- This pattern is useful for handling input files with comments or for selectively processing certain lines based on a pattern.
-  It helps keep scripts clean and focused on relevant data by ignoring comments or unwanted lines.


## Extracting Keys and Values
```bash
key=$(echo "$line" | cut -d '=' -f 1 | xargs)
value=$(echo "$line" | cut -d '=' -f 2 | xargs)
```

- **echo "line"**: This command outputs the contents of the variable line. It acts as a way to pipe the line to subsequent commands. Here, **"$line"** is a string variable that typically holds a line of text from a configuration file or similar input.

- **cut -d '=' -f 1**: This command is used to extract a specific field from a line of text. Let's break it down further:

- **-d '='**: Specifies the delimiter character that separates fields, which is **=** in this case. This means the text is split wherever an = character is found.
- **-f 1**: Specifies that the first field should be extracted. For a line like key=value, this extracts key.
- **cut -d '=' -f 2**: Similarly, this command extracts the second field from the line of text, which would be the value in a key=value pair.

- **xargs**: This command trims leading and trailing whitespace from its input. When used in this context, it ensures that any extra spaces around the key or value are removed. This is especially useful if the input might contain spaces around the = or at the start/end of the line.

#### Explanation with Example
  
- Suppose you have a line like this:

```bash
line="  key = value  "
```
Here's what each part of the command does:

1) echo "$line": Outputs key = value .

2) #### Extracting Key:

```bash
key=$(echo "$line" | cut -d '=' -f 1 | xargs)
```
- **cut -d '=' -f 1**: Splits the line into **key** (before =).
- **xargs**: Trims whitespace, resulting in **key**.
3) #### Extracting Value:

```bash
value=$(echo "$line" | cut -d '=' -f 2 | xargs)
```
- **cut -d '=' -f 2**: Splits the line into value (after =).
- **xargs**: Trims whitespace, resulting in value.
#### Use in a Script
- Here is an example of how these commands might be used in a script to parse a configuration file:


```bash
#!/bin/bash

filename="config.txt"

while IFS= read -r line; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^\# ]] || [[ -z "$line" ]]; then
        continue
    fi

    # Extract key and value
    key=$(echo "$line" | cut -d '=' -f 1 | xargs)
    value=$(echo "$line" | cut -d '=' -f 2 | xargs)

    # Output the key-value pair
    echo "Key: $key, Value: $value"

done < "$filename"
```
- **Key Extraction: key=$(echo "$line" | cut -d '=' -f 1 | xargs)** extracts the part before the = and trims whitespace.
- **Value Extraction: value=$(echo "$line" | cut -d '=' -f 2 | xargs)** extracts the part after the = and trims whitespace.
  
- These commands are useful for parsing configuration files or any data structured as key-value pairs, ensuring clean and whitespace-free output.