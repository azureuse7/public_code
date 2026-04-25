#Azure provider
provider "azurerm" {
  features {}
}
# Terraform

variable "application_name" {
    type = string
    default = "gtr31@3"

    validation {
    # regex(...) fails if it cannot find a match
    condition     = can(regex("([0-9A-Za-z])", var.application_name))
    error_message = "For the application_name value only a-z, A-Z and 0-9 are allowed."
  }
}

# The ^ symbol matches only at the start of the given string.
# The $ symbol matches only at the end of the given string.
# The + operator allows the preceding pattern to appear one or more times.