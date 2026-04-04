# Setting Up Environment Variables on macOS

> Environment variables are key-value pairs that configure the shell environment and are accessible by any process. On macOS they are typically set in shell profile files.

---

## Shell Profile Files

| File | Shell | When loaded |
|------|-------|------------|
| `~/.zshrc` | Zsh (default on macOS 10.15+) | Every interactive shell session |
| `~/.bash_profile` | Bash | Login shell sessions |
| `~/.bashrc` | Bash | Interactive non-login shells |
| `~/.profile` | Any POSIX shell | Login shell (fallback) |

---

## Set a Temporary Variable (current session only)

```bash
export MY_VAR="hello"
echo $MY_VAR
```
The variable is lost when the terminal closes.

---

## Set a Permanent Variable

Add the `export` line to your shell profile:

```bash
# Open your profile in a text editor
nano ~/.zshrc

# Add this line
export MY_VAR="hello"

# Save, then reload the profile
source ~/.zshrc
```

---

## Common Use Cases

```bash
# Add a directory to PATH
export PATH="$PATH:/usr/local/myapp/bin"

# Set a default editor
export EDITOR="vim"

# Configure AWS CLI profile
export AWS_PROFILE="my-profile"
export AWS_DEFAULT_REGION="eu-west-1"

# Terraform Azure authentication
export ARM_SUBSCRIPTION_ID="..."
export ARM_CLIENT_ID="..."
export ARM_CLIENT_SECRET="..."
export ARM_TENANT_ID="..."
```

---

## List and Inspect Variables

```bash
# List all environment variables
env

# Print a specific variable
echo $MY_VAR

# Check if a variable is set
if [ -z "$MY_VAR" ]; then
    echo "MY_VAR is not set"
fi
```

---

## Remove a Variable

```bash
unset MY_VAR
```
