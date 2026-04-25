# Terraform Output Values with `count` and Splat Expressions

## Step-01: Introduction

When using the `count` meta-argument on a resource, Terraform creates multiple instances of that resource. Referencing those instances in output values requires special syntax.

- Understand how to define outputs when using the `count` meta-argument
- What is a [Splat Expression](https://www.terraform.io/docs/language/expressions/splat.html)?
- Why do we need to use splat expressions in outputs when using `count`?

A **splat expression** provides a more concise way to express a common operation that could otherwise be performed with a `for` expression. The special `[*]` symbol iterates over all elements of the list to its left and accesses the named attribute from each one.

```hcl
# With a for expression
[for o in var.list : o.id]

# With a splat expression [*]
var.list[*].id
```

## Step-02: `c4-virtual-network.tf`

Add the `count` meta-argument to the `azurerm_virtual_network` resource to create multiple instances.

```hcl
# Create Virtual Network
resource "azurerm_virtual_network" "myvnet" {
  count               = 4
  name                = "${var.business_unit}-${var.environment}-${var.virtual_network_name}-${count.index}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.myrg.location
  resource_group_name = azurerm_resource_group.myrg.name
}
```

## Step-03: Execute Terraform Commands - Validate (Expected Failure)

```bash
# Initialize Terraform
terraform init

# Validate Terraform configuration files
# Observation: This will fail because the output references a counted resource without an index
terraform validate
```

**Sample error output:**

```log
╷
│ Error: Missing resource instance key
│
│   on c5-outputs.tf line 16, in output "virtual_network_name":
│   16:   value = azurerm_virtual_network.myvnet.name
│
│ Because azurerm_virtual_network.myvnet has "count" set, its attributes must be
│ accessed on specific instances.
│
│ For example, to correlate with indices of a referring resource, use:
│     azurerm_virtual_network.myvnet[count.index]
╵
```

## Step-04: `c5-outputs.tf`

Update the `virtual_network_name` output to use a splat expression, which returns a list of all virtual network names.

```hcl
# Output Values - Virtual Network
output "virtual_network_name" {
  description = "Virtual Network Name"
  value       = azurerm_virtual_network.myvnet[*].name
}
```

## Step-06: Execute Terraform Commands

```bash
# Validate Terraform configuration files
# Observation: Should pass
terraform validate

# Format Terraform configuration files
terraform fmt

# Review the Terraform plan
# Observation: Should pass
terraform plan
```

**Sample plan output:**

```log
Plan: 5 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + resource_group_id    = (known after apply)
  + resource_group_name  = "it-dev-rg"
  + virtual_network_name = [
      + "it-dev-vnet-0",
      + "it-dev-vnet-1",
      + "it-dev-vnet-2",
      + "it-dev-vnet-3",
    ]
```

```bash
# Create resources (optional)
# Observation: All virtual network names will be returned as a list
terraform apply -auto-approve
```

## Step-07: Destroy Resources

```bash
# Destroy resources
terraform destroy -auto-approve

# Clean up local Terraform files
rm -rf .terraform*
rm -rf terraform.tfstate*
```

## References

- [Terraform Output Values](https://www.terraform.io/docs/language/values/outputs.html)
