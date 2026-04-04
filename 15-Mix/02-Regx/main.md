# Regular Expressions (Regex)

> Regular expressions are patterns used to match, search, and manipulate text. They are supported in Bash, Python, PowerShell, JavaScript, and most modern languages.

**Interactive tester:** https://regex101.com/

---

## Syntax Cheat Sheet

### Anchors
| Pattern | Matches |
|---------|---------|
| `^` | Start of string / line |
| `$` | End of string / line |
| `\b` | Word boundary |

### Character Classes
| Pattern | Matches |
|---------|---------|
| `.` | Any character except newline |
| `\d` | Digit `[0-9]` |
| `\w` | Word character `[a-zA-Z0-9_]` |
| `\s` | Whitespace (space, tab, newline) |
| `[abc]` | Any of a, b, or c |
| `[^abc]` | Any character except a, b, or c |
| `[a-z]` | Any lowercase letter |

### Quantifiers
| Pattern | Matches |
|---------|---------|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 (optional) |
| `{3}` | Exactly 3 |
| `{2,5}` | Between 2 and 5 |

### Groups
| Pattern | Matches |
|---------|---------|
| `(abc)` | Capture group |
| `(?:abc)` | Non-capturing group |
| `a\|b` | a or b |

---

## Examples

### Validate an IP address
```
^(\d{1,3}\.){3}\d{1,3}$
```

### Match an email address
```
^[\w.-]+@[\w.-]+\.\w{2,}$
```

### Extract key=value pairs
```
^(\w+)\s*=\s*(.+)$
```

### Match a line starting with `#` (comment)
```
^\s*#
```

---

## Regex in Bash
```bash
# Test if a string matches a pattern
if [[ "$line" =~ ^[0-9]+$ ]]; then
    echo "Line is a number"
fi

# Extract a match with grep
echo "server: 192.168.1.10" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
```

## Regex in Python
```python
import re

text = "Order #1234 placed on 2024-03-15"

# Search for a pattern
match = re.search(r'\d{4}-\d{2}-\d{2}', text)
if match:
    print(match.group())  # 2024-03-15

# Find all matches
numbers = re.findall(r'\d+', text)
print(numbers)  # ['1234', '2024', '03', '15']
```

## Regex in PowerShell
```powershell
# Match test
"hello world" -match "^hello"   # True

# Extract a group
"version: 1.2.3" -match 'version: (\d+\.\d+\.\d+)'
$Matches[1]   # 1.2.3
```
