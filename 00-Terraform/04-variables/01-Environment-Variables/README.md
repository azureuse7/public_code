# Terraform Input Variables Using Environment Variables

## Step-01: Introduction

Terraform allows you to override default variable values by setting environment variables prefixed with `TF_VAR_`. This is useful for injecting values at runtime without modifying configuration files.

- Override default variable values using environment variables

## Step-02: Input Variables Override with Environment Variables

Set environment variables and execute `terraform plan` to verify that they override the default values.

```bash
# Sample pattern
export TF_VAR_variable_name=value

# Set environment variables
export TF_VAR_resoure_group_name=rgenv
export TF_VAR_resoure_group_location=westus2
export TF_VAR_virtual_network_name=vnetenv
export TF_VAR_subnet_name=subnetenv
echo $TF_VAR_resoure_group_name, $TF_VAR_resoure_group_location, $TF_VAR_virtual_network_name, $TF_VAR_subnet_name
```

## Step-03: Execute Terraform Commands

```bash
# Initialize Terraform
terraform init

# Validate Terraform configuration files
terraform validate

# Format Terraform configuration files
terraform fmt

# Review the Terraform plan
terraform plan

# Unset environment variables after demo
unset TF_VAR_resoure_group_name
unset TF_VAR_resoure_group_location
unset TF_VAR_virtual_network_name
unset TF_VAR_subnet_name
echo $TF_VAR_resoure_group_name, $TF_VAR_resoure_group_location, $TF_VAR_virtual_network_name, $TF_VAR_subnet_name
```
