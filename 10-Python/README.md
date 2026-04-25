# Python

> Python fundamentals and practical scripts — covering environment setup, core language constructs, and a real-world Flask microservices project deployed on Kubernetes.

---

## Contents

### Language Fundamentals

| File | Topic |
|------|-------|
| [00.md](00.md) | Setting up a virtual environment (`venv`) |
| [02-Assert.py](02-Assert.py) | Assertions for testing assumptions |
| [03-Def.py](03-Def.py) | Defining and calling functions |
| [04-Os.getenv.py](04-Os.getenv.py) | Reading environment variables with `os.getenv` |
| [05-if.md](05-if.md) | If / elif / else conditionals |
| [06-function.md](06-function.md) | Function definitions and return values |
| [07-While-Loops.py](07-While-Loops.py) | While loops |
| [08-In.py](08-In.py) | Membership testing with the `in` operator |
| [09-Conditional.py](09-Conditional.py) | Conditional expressions (ternary) |
| [10-ClassesAnsObjectes.py](10-ClassesAnsObjectes.py) | Classes and objects |
| [10-classes.md](10-classes.md) | Classes explained with examples |
| [11-For-in-Python.md](11-For-in-Python.md) | For loops and iteration |
| [12-entry point check.md](12-entry%20point%20check.md) | `if __name__ == "__main__"` explained |
| [13-list.md](13-list.md) | List operations and methods |
| [14-Mix -python.py](14-Mix%20-python.py) | Mixed practical examples |

### Cloud Integration
| File | Topic |
|------|-------|
| [01-Access-AKS.py](01-Access-AKS.py) | Connect to an AKS cluster using the Kubernetes Python client |

### Project
| Directory | Topic |
|-----------|-------|
| [Project/](Project/) | Flask microservices app with Docker, Kubernetes, and Helm |

---

## Quick Start

### Create and activate a virtual environment
```bash
# Create
python3 -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Deactivate
deactivate
```

### Key patterns

```python
# Read an environment variable (with default)
import os
value = os.getenv("MY_VAR", "default")

# Entry point check
if __name__ == "__main__":
    main()

# List operations
items = [1, 2, 3]
items.append(4)
filtered = [x for x in items if x > 2]

# Class definition
class Dog:
    def __init__(self, name):
        self.name = name
    def bark(self):
        return f"{self.name} says woof!"
```
