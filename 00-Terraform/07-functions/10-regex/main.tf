# Go to Terraform Console
# terraform console

# Test regex() function
# Template: regex(pattern, string)
### TRUE CASES


# regex("india$", "westindia")
# india 

# regex("india$", "southindia")

# can(regex("india$", "westindia"))
# true 

# can(regex("india$", "southindia"))

### FAILURE CASES
# regex("india$", "eastus")
# can(regex("india$", "eastus"))