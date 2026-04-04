# Terraform Module - Publish to the Terraform Public Registry

## Step-01: Introduction

This section covers the full workflow for publishing a reusable Terraform module to the Terraform Public Registry and consuming it in a root module.

- Create and version a GitHub repository for Terraform modules
- Publish a module to the Terraform Public Registry
- Construct a root module that consumes a module from the Terraform Public Registry
- Understand Terraform module versioning

## Step-02: Create a New GitHub Repository for the Azure Static Website Terraform Module

- **URL:** [github.com](https://github.com)
- Click on **Create a new repository**
- Follow the naming convention for modules: `terraform-PROVIDER-MODULE_NAME`
  - **Example:** `terraform-azurerm-staticwebsitepublic`
- **Repository Name:** `terraform-azurerm-staticwebsitepublic`
- **Description:** Terraform Modules to be shared in Terraform Public Registry
- **Repo Type:** Public
- **Initialize this repository with:**
  - **Uncheck** - Add a README file
  - **Check** - Add `.gitignore`
  - **Select .gitignore Template:** Terraform
  - **Check** - Choose a license
  - **Select License:** Apache 2.0 License (Optional)
- Click on **Create repository**

## Step-03: Clone the GitHub Repository to Your Local Desktop

```bash
# Clone GitHub repo
git clone https://github.com/<YOUR_GITHUB_ID>/<YOUR_REPO>.git
git clone https://github.com/stacksimplify/terraform-azurerm-staticwebsitepublic.git
```

## Step-04: Copy Files from terraform-manifests to the Local Repo and Check In Code

- **Source Location (from this section):** `terraform-azure-static-website-module-manifests`
- **Destination Location:** The newly cloned GitHub repository folder on your local desktop — `terraform-azurerm-staticwebsitepublic`
- Check in code to the remote repository

```bash
# Git status
git status

# Git local commit
git add .
git commit -am "TF Module Files First Commit"

# Push to remote repository
git push

# Verify on the remote repository
# https://github.com/stacksimplify/terraform-azurerm-staticwebsitepublic.git
```

## Step-05: Create New Release Tag 1.0.0 in the Repo

- Go to Right Navigation on the GitHub repo -> **Releases** -> **Create a new release**
- **Tag Version:** `1.0.0`
- **Release Title:** Release-1 terraform-azurerm-staticwebsitepublic
- **Write:** Terraform Module for Public Registry - terraform-azurerm-staticwebsitepublic
- Click on **Publish Release**

## Step-06: Publish Module to the Public Terraform Registry

- Access the registry at [https://registry.terraform.io/](https://registry.terraform.io/)
- Sign in using your GitHub account
- Authorize the Terraform Registry when prompted
- Go to **Publish** -> **Modules**
- **Select Repository on GitHub:** `terraform-azurerm-staticwebsitepublic`
- Check `I agree to the Terms of Use`
- Click on **Publish Module**

## Step-07: Review the Newly Published Module

- **URL:** [https://registry.terraform.io/modules/stacksimplify/staticwebsitepublic/azurerm/latest](https://registry.terraform.io/modules/stacksimplify/staticwebsitepublic/azurerm/latest)
- Review the module tabs on Terraform Registry:
  1. Readme
  2. Inputs
  3. Outputs
  4. Dependencies
  5. Resources
- Also review:
  1. Versions
  2. Provision Instructions

## Step-08: Review Root Module Terraform Configs

- The `terraform-manifests` folder was copied from the previous section `51-Terraform-Modules-Build-Local-Module`.
- Here, instead of using a local reusable module, the module source is pulled from the Terraform Public Registry.
- In `c3-static-website.tf`:
  - The local `source` reference is commented out
  - A new `source` and `version` from the Terraform Public Registry are added

```hcl
# Call our custom Terraform module which was built earlier
module "azure_static_website" {
  #source = "./modules/azure-static-website"
  source  = "stacksimplify/staticwebsitepublic/azurerm"
  version = "1.0.0"

  # Resource Group
  location            = "eastus"
  resource_group_name = "myrg1"

  # Storage Account
  storage_account_name               = "staticwebsite"
  storage_account_tier               = "Standard"
  storage_account_replication_type   = "LRS"
  storage_account_kind               = "StorageV2"
  static_website_index_document      = "index.html"
  static_website_error_404_document  = "error.html"
}
```

## Step-09: Execute Terraform Commands

```bash
# Terraform initialize
terraform init
# Observation:
# 1. Should pass and download modules and providers
#
# Sample output:
# Initializing modules...
# Downloading stacksimplify/staticwebsitepublic/azurerm 1.0.0 for azure_static_website...
# - azure_static_website in .terraform/modules/azure_static_website

# Terraform validate
terraform validate

# Terraform format
terraform fmt

# Terraform plan
terraform plan

# Terraform apply
terraform apply -auto-approve

# Upload static content
# 1. Go to Storage Accounts -> staticwebsitexxxxxx -> Containers -> $web
# 2. Upload files from the "static-content" folder

# Verify
# 1. Azure Storage Account created
# 2. Static Website Setting enabled
# 3. Verify the static content upload was successful
# 4. Access Static Website: https://staticwebsitek123.z13.web.core.windows.net/
```

## Step-10: Destroy and Clean Up

```bash
# Terraform destroy
terraform destroy -auto-approve

# Delete Terraform files
rm -rf .terraform*
rm -rf terraform.tfstate*
```

## Step-11: Module Management on Terraform Public Registry

- URL: [https://registry.terraform.io/modules/stacksimplify/staticwebsitepublic/azurerm/latest](https://registry.terraform.io/modules/stacksimplify/staticwebsitepublic/azurerm/latest)
- You must be logged in to the Terraform Public Registry with the GitHub account used to publish the module.
  1. Resync Module
  2. Delete Module Version
  3. Delete Module Provider
  4. Delete Module

## Step-12: Module Versioning

To release a new version of the module:

1. Make changes to your module code and push them to the Git repo
2. Create a new release tag on the Git repo (for example: `2.0.0`)
3. Verify the new version appears in the Terraform Registry

```bash
# Make a change in the local Git repo
# Edit README.md and add the line: - Version 2.0.0

# Git commands
git status
git commit -am "2.0.0 Commit"
git push

# Draft a new release
# 1. Go to Right Navigation on the GitHub repo -> Releases -> Draft a new release
# 2. Tag Version: 2.0.0
# 3. Release Title: Release-2 terraform-azurerm-staticwebsitepublic
# 4. Write: Terraform Module for Public Registry - terraform-azurerm-staticwebsitepublic Release-2
# 5. Click on "Publish Release"

# Verify the new version appears in the registry:
# https://registry.terraform.io/modules/stacksimplify/staticwebsitepublic/azurerm/latest
# In the Versions drop-down, you should see both 1.0.0 and 2.0.0 (latest)

# Update your module version tag in c3-static-website.tf:
# Old: version = "1.0.0"
# New: version = "2.0.0"
```
