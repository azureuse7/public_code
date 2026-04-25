# Terraform Command: `apply -refresh-only`

## Step-01: Introduction

The `terraform apply -refresh-only` command reconciles Terraform's state file with the real-world infrastructure. It is useful for detecting configuration drift without modifying any actual resources.

- Reference: [Terraform Refresh](https://www.terraform.io/docs/cli/commands/refresh.html)
- Understand `terraform apply -refresh-only` in detail

### Understanding `terraform apply -refresh-only`

- This command falls under **Terraform Inspecting State**
- The `terraform apply -refresh-only` command updates the state file to reflect the real resources in your cloud environment without making any infrastructure changes
- It can detect any drift from the last-known state and update the state file accordingly
- **Important:** This command modifies the state file but does NOT modify infrastructure. A changed state file may cause changes during the next `plan` or `apply`

Key concepts:

- **`terraform apply -refresh-only`:** Updates `terraform.tfstate` against real resources in the cloud
- **Desired State:** Local Terraform manifests (all `.tf` files)
- **Current State:** Real resources present in your cloud environment

## Step-02: Review Terraform Configs

- `c1-versions.tf`
- `c2-resource-group.tf`

## Step-03: Execute Terraform Commands

```bash
# Terraform initialize
terraform init

# Terraform validate
terraform validate

# Terraform plan
terraform plan

# Terraform apply
terraform apply -auto-approve
```

## Step-04: Add a New Tag to a Resource Using the Azure Management Console

Using the Azure portal, manually add the following tag to the resource group:

```hcl
"tag3" = "my-tag-3"
```

## Step-05: Execute `terraform plan`

Running `terraform plan` at this point performs the comparison in memory only and does NOT update the state file. The plan will show the difference (the new tag), but `terraform.tfstate` will not be modified.

```bash
# Execute Terraform plan
terraform plan

# Verify the Terraform state file timestamp (it should not change)
ls -lrta

# Review the Terraform state file
terraform show
```

## Step-06: Execute `terraform apply -refresh-only`

Running `terraform apply -refresh-only` updates the state file to include the manually added tag.

```bash
# Execute terraform plan -refresh-only (preview the refresh)
terraform plan -refresh-only

# Execute terraform apply -refresh-only (update the state file)
terraform apply -refresh-only

# Review the updated state file
# 1. Run: terraform show
# 2. Verify that the new tag is now present in the state file:
#    "tag3" = "my-tag-3"
```

## Step-07: Update TF Configs

Now that the manual change is captured in the state file, you also need to update your Terraform configuration (desired state) to officially manage this change.

- Update `c2-resource-group.tf`: add `tag3` to match the state file
- Uncomment `tag3` in the resource block

```bash
# Run Terraform plan
# Observation:
# 1. tag3 is present in the current state (Azure portal) and in the Terraform state file
#    but NOT in the TF configs (desired state).
# 2. terraform plan will propose removing that tag in the next apply.
# 3. Add tag3 to c2-resource-group.tf to reconcile all three states.
terraform plan
```

After adding `tag3` to `c2-resource-group.tf`:

```hcl
# Resource-1: Azure Resource Group
resource "azurerm_resource_group" "myrg" {
  name     = "myrg1"
  location = "eastus"
  tags = {
    "tag1" = "my-tag-1"
    "tag2" = "my-tag-2"
    "tag3" = "my-tag-3"
  }
}
```

```bash
# Run Terraform plan again
# Observation:
# - No infrastructure changes
# - TF configs (Desired State): matches
# - TF state file: matches
# - Azure portal (Current State): matches
terraform plan
```

## Step-08: Clean Up

```bash
# Destroy resources
terraform destroy -auto-approve

# Delete local files
rm -rf .terraform*
rm -rf terraform.tfstate*
```
