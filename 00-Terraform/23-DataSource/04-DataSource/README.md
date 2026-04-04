# Terraform External Provider and Datasource

## Step-01: Introduction

The Terraform external provider allows you to integrate arbitrary external programs as data sources. This is useful for generating dynamic values (such as SSH keys) that Terraform itself cannot produce natively.

- Reference: [Terraform External Provider and Datasource](https://registry.terraform.io/providers/hashicorp/external/latest)

## Step-02: Pre-requisite Installs

The following tools must be installed and available in your `PATH` before proceeding:

- `ssh-keygen`
- `jq`

```bash
# Verify ssh-keygen is available
which ssh-keygen

# Verify jq is available
which jq

# Install jq on macOS using Homebrew
brew install jq
```

## Step-03: `ssh_key_generator.sh`

This shell script generates an SSH key pair and returns the public key, private key, and private key file path as JSON output. It is designed to be called by the Terraform external datasource.

- **File location:** `terraform-manifests/shell-scripts/`

```bash
function error_exit() {
  echo "$1" 1>&2
  exit 1
}

function check_deps() {
  test -f $(which ssh-keygen) || error_exit "ssh-keygen command not found in path, please install it"
  test -f $(which jq) || error_exit "jq command not found in path, please install it"
}

function parse_input() {
  # jq reads from stdin so we don't have to set up any inputs, but let's validate the outputs
  eval "$(jq -r '@sh "export KEY_NAME=\(.key_name) KEY_ENVIRONMENT=\(.key_environment)"')"
  if [[ -z "${KEY_NAME}" ]]; then export KEY_NAME=none; fi
  if [[ -z "${KEY_ENVIRONMENT}" ]]; then export KEY_ENVIRONMENT=none; fi
}

function create_ssh_key() {
  script_dir=$(dirname $0)
  export ssh_key_file="${script_dir}/${KEY_NAME}-${KEY_ENVIRONMENT}"
  # echo "DEBUG: ssh_key_file = ${ssh_key_file}" 1>&2
  if [[ ! -f "${ssh_key_file}" ]]; then
    #ssh-keygen -m PEM -t rsa -b 4096 -N '' -f $ssh_key_file
    ssh-keygen -q -m PEM -t rsa -b 4096 -N '' -f $ssh_key_file
  fi
}

function produce_output() {
  public_key_contents=$(cat ${ssh_key_file}.pub)
  # echo "DEBUG: public_key_contents ${public_key_contents}" 1>&2
  private_key_contents=$(cat ${ssh_key_file} | awk '$1=$1' ORS='  \n')
  # echo "DEBUG: private_key_contents ${private_key_contents}" 1>&2
  # echo "DEBUG: private_key_file ${ssh_key_file}" 1>&2
  jq -n \
    --arg public_key "$public_key_contents" \
    --arg private_key "$private_key_contents" \
    --arg private_key_file "$ssh_key_file" \
    '{"public_key":$public_key,"private_key":$private_key,"private_key_file":$private_key_file}'
}

# main()
check_deps
# echo "DEBUG: received: $INPUT" 1>&2
parse_input
create_ssh_key
produce_output
```

## Step-04: Test the Shell Script

```bash
# Test the shell script directly
echo '{"key_name": "terraformdemo", "key_environment": "dev"}' | ./ssh_key_generator.sh

# Verify the files created in terraform-manifests/shell-scripts/
# 1. terraformdemodev       - Private key file
# 2. terraformdemodev.pub   - Public key file
```

## Step-05: `c1-versions.tf`

```hcl
# Terraform Block
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.0"
    }
    external = {
      source  = "hashicorp/external"
      version = ">= 2.0"
    }
  }
}

# Provider Block
provider "azurerm" {
  features {}
}
```

## Step-06: `c2-external-datasource.tf`

This data source calls the shell script and passes input parameters as a JSON query.

```hcl
# External datasource
data "external" "ssh_key_generator" {
  program = ["bash", "${path.module}/shell-scripts/ssh_key_generator.sh"]

  query = {
    key_name        = "terraformdemo"
    key_environment = "dev"
  }
}
```

## Step-07: `c2-external-datasource.tf` - Outputs

Define Terraform outputs to expose the results from the external datasource.

```hcl
# Outputs
output "public_key" {
  description = "public_key"
  value       = data.external.ssh_key_generator.result.public_key
}

output "private_key" {
  description = "private_key"
  value       = data.external.ssh_key_generator.result.private_key
}

output "private_key_file" {
  description = "private_key_file"
  value       = data.external.ssh_key_generator.result.private_key_file
}
```

## Step-08: Execute Terraform Commands

```bash
# Terraform initialize
terraform init

# Terraform validate
terraform validate

# Terraform plan
terraform plan
# Observation:
# Because this is just a datasource, the shell script "ssh_key_generator.sh" will be
# triggered during either plan or apply, and the public/private key pair will be generated.

# Terraform apply (optional)
terraform apply
```

## Step-09: Clean Up

```bash
# Destroy resources (optional, only if terraform apply was executed)
terraform destroy -auto-approve

# Delete local Terraform files
rm -rf .terraform*
rm -rf terraform.tfstate*
```
