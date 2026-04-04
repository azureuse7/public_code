# Bash Shell Scripting

> A progressive reference covering the essential Bash scripting constructs — from reading files and manipulating text, to making API calls and integrating with Azure DevOps pipelines.

---

## Contents

| File | Topic |
|------|-------|
| [00-script.md](00-script.md) | Parsing `.tfvars` files and setting Azure DevOps pipeline variables |
| [01-awk.md](01-awk.md) | AWK — field extraction, pattern matching, and text processing |
| [02-case.md](02-case.md) | Case statements — multi-branch conditionals |
| [03-curl.md](03-curl.md) | curl — making HTTP API calls, passing auth headers, retrieving tokens |
| [04-sed.md](04-sed.md) | sed — stream editing, character trimming, substitutions |
| [05-if.md](05-if.md) | If statements — file tests, numeric and string comparisons |
| [06-while.md](06-while.md) | While loops — iterating over files, polling, line-by-line processing |

---

## Key Concepts

### Reading a file line by line
```bash
while IFS= read -r line; do
    echo "$line"
done < input_file.txt
```

### Skipping comments and blank lines
```bash
while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    echo "Processing: $line"
done < file.txt
```

### Extracting key=value pairs
```bash
key=$(echo "$line" | cut -d '=' -f 1 | xargs)
value=$(echo "$line" | cut -d '=' -f 2 | xargs)
```

### Setting an Azure DevOps pipeline variable from a script
```bash
echo "##vso[task.setvariable variable=$key;isOutput=true]$value"
```

### Quick reference
| Tool | Use for |
|------|---------|
| `awk` | Extracting columns, filtering rows |
| `sed` | In-place substitution, character trimming |
| `cut` | Splitting on a delimiter, picking a field |
| `xargs` | Trimming whitespace from piped strings |
| `curl` | HTTP requests, REST API calls |
