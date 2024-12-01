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

## Reading the File Line by Line
```bash
while IFS= read -r line; do
    # Commands to process each line
    echo "$line"
done < input_file.txt
```
1) #### IFS=:
- **IFS** stands for "Internal Field Separator". In a shell script, it is a variable that determines how Bash recognizes word boundaries (i.e., how it splits input into separate words or fields).
-  By setting **IFS**= with no value, you are temporarily disabling any field splitting. This ensures that the read command treats the entire input line as a single entity, preserving any whitespace (spaces, tabs) or special characters in the line.
2) ####  read -r line
- **read**: This is a built-in Bash command used to read a line of input from a file or standard input.
- **-r**: This option tells read to treat backslashes literally, rather than as escape characters. This is important if the input may contain backslashes that should not be interpreted as escape sequences.
- **line**: This is the variable name where the input line will be stored. Each time through the loop, the read command reads a new line and assigns it to line.
3) #### while IFS= read -r line; do:
- **while ... do:** This starts a loop that will execute a series of commands for each line of input.
- The loop will continue to iterate for each line read by the **read** command until there are no more lines to read.


##### How It Works
- **Reading** **Input**: The loop reads from the file input_file.txt (or any input source redirected to the loop). Each line is read in full, without splitting on spaces or tabs, and backslashes are not treated as escape characters.

- **Processing** **Lines**: Inside the loop, you can perform any operations on the variable line. In the example above, it simply echoes each line back to the terminal.

- **Loop** **Continuation**: The loop automatically continues to the next line after processing the current line until it reaches the end of the file or input stream.

```bash
while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    # Commands to process non-empty, non-comment lines
    echo "Processing: $line"
done < input_file.txt
```
#### Components Explained

1) ##### [ ... ] 

- This is a conditional expression used in Bash to evaluate test conditions. It is more flexible and powerful than the [ ... ] (single bracket) test command.
- It allows for pattern matching, regular expressions, and logical operators within its syntax.
2) ##### -z "$line":

- **-z**: This test checks if the string is empty.
- "**line**": This is the variable holding the current line of text being processed in the loop.
- So, -z "$line" evaluates to true if the variable line is empty.
3) #### ||:

- This is a logical OR operator. The expression evaluates to true if either the condition before or after it is true.
4) #### "$line" =~ ^#:

- **=~**: This is the regular expression matching operator in Bash.
- **^#**: This is a regular expression that matches a # character at the start of a string (the ^ character denotes the start of the line).
- So, **"$line" =~ ^#** evaluates to true if the line starts with a #, which is typically used to denote a comment line in many configuration files and scripts.
5) ##### && continue:

- **&&**: This is a logical AND operator. It means "execute the following command if the preceding condition is true."
- **continue**: This command causes the loop to skip the rest of its current iteration and proceed with the next iteration.
  
##### How It Works Together
The entire expression **[[ -z "$line" || "$line" =~ ^# ]] &&** continue is used to skip over lines that are either empty or start with a #. Here's how it functions in a loop:

- **Empty Line Check: -z "$line"** checks if the line is empty. If true, the whole expression becomes true because of the OR operator.

- **Comment Line Check: "$line" =~ ^#** checks if the line starts with a #. If true, the whole expression also becomes true.

- **Skipping Lines**: If either condition is true (the line is empty or a comment), && continue is executed, causing the loop to skip to the next line.



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

## Extracting Keys and Values
```bash
key=$(echo "$line" | cut -d '=' -f 1 | xargs)
value=$(echo "$line" | cut -d '=' -f 2 | xargs)
```
- These two lines of Bash code are used to extract and clean key-value pairs from a string formatted as **key=value**
- Each line performs a series of operations to extract either the key or the value from the string, removing any surrounding whitespace.

1) #### Input Variable line:

- Assume **line** contains a string formatted as **key**=**value**, like **username**=**admin** or **path**=**/usr/local/bin.**
2) #### Key Extraction:

```bash
key=$(echo "$line" | cut -d '=' -f 1 | xargs)
```
- **echo "$line"**: Prints the value of line. The quotes ensure that any special characters or spaces in the line are preserved as a single string.
- **cut -d '=' -f 1:**
  - **-d '='**: Specifies = as the delimiter. cut splits the string into fields based on this delimiter.
  - **-f 1**: Extracts the first field (i.e., the part before =). For **username=admin**, this would extract **username**.
- **xargs**: Removes any leading or trailing whitespace from the extracted key. This is important for clean, whitespace-free variable values.
  
3) #### Value Extraction:

```bash
value=$(echo "$line" | cut -d '=' -f 2 | xargs)
```
- **echo "$line":** Prints the line again, just as before.
- **cut -d '=' -f 2:**
  - **-d '='**: Uses the same delimiter =.
  - **-f 2:** Extracts the second field (i.e., the part after =). For username=admin, this would extract admin.
- **xargs**: Removes any leading or trailing whitespace from the extracted value.
#### Why Use xargs?
The xargs command is used here to trim whitespace. While its primary function is to build and execute command lines from standard input, when used without additional arguments, it simply trims whitespace from its input. This ensures that any spaces accidentally included around the = or in the input line do not end up in the final key or value.

#### Example in a Script
Here’s how these commands might be used in a practical script:

```bash
#!/bin/bash

filename="settings.conf"

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
```
#### Example Input File (settings.conf)
```bash
# Sample configuration file
username= admin
path= /usr/local/bin 
log_level = debug
# comment line
```
#### Output
The script processes each line, skipping comments and empty lines, and outputs cleaned key-value pairs:

```bash
Key: username, Value: admin
Key: path, Value: /usr/local/bin
Key: log_level, Value: debug
```


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




# echo "##vso[task.setvariable variable=$key]$value"


- The command echo **"##vso[task.setvariable variable=$key]$value"** is used within Azure DevOps pipelines, specifically in scripting environments where tasks communicate and control the Azure DevOps environment using logging commands. 
- These commands are parsed by the system and can alter the environment or control pipeline behavior.

#### Here’s a breakdown of the components of the command:

1) #### echo: 
   This is a standard command used in many shell environments to output the following string to the standard output (stdout).

2) #### ##vso[task.setvariable variable=$key]$value:

- **##vso** is a prefix used to indicate that the text following it is a special command, not just plain text. Azure DevOps recognizes these as "**logging commands**."
- **[task.setvariable]** is a specific command that sets a variable in the Azure DevOps pipeline.
- **variable=$key** inside the brackets sets the name of the variable to whatever is stored in the shell variable $key.
- **$value** following the closing bracket sets the value of the variable. This value is taken from the shell variable $value.



#### Example
Suppose you have a pipeline where you need to set a variable named deploymentEnvironment to production based on some condition evaluated within a Bash script. You would use:

```bash
key="deploymentEnvironment"
value="production"
echo "##vso[task.setvariable variable=$key]$value"
```
After this command is executed, the variable deploymentEnvironment in the Azure DevOps pipeline environment would be set to production, and subsequent tasks in the pipeline can use this variable.

This allows for very dynamic and flexible pipeline configurations, where outputs from one task can influence the behavior of later tasks.



Accessing Output Variables Correctly
$[ stageDependencies.{StageName}.{JobName}.outputs['{TaskName}.{VariableName}'] ]

