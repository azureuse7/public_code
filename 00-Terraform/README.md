# Terraform: Infrastructure as Code (Azure)

> Comprehensive Terraform reference covering the full lifecycle — from first `init` to production-grade patterns including modules, workspaces, remote state, dynamic blocks, and Azure authentication.

---

## Contents

| Directory | Topic |
|-----------|-------|
| [01-Qick-ref/](01-Qick-ref/) | Quick reference: most-used CLI commands |
| [02-init-plan-apply-destroy/](02-init-plan-apply-destroy/) | Core workflow — init, plan, apply, destroy |
| [03-terraform-state/](03-terraform-state/) | State file — local vs remote backends, state commands |
| [04-variables/](04-variables/) | Input variables — strings, lists, maps, objects, environment vars |
| [05-modules/](05-modules/) | Modules — writing, calling, publishing to the public registry |
| [06-Provider-Resource-Block-Basics/](06-Provider-Resource-Block-Basics/) | Provider and resource block fundamentals |
| [07-functions/](07-functions/) | Built-in functions: index, try, join, contains, lookup, merge, regex |
| [08-conditions/](08-conditions/) | Conditional expressions (`condition ? true : false`) |
| [09-for-expressions/](09-for-expressions/) | For expressions — transform lists and maps |
| [10-count/](10-count/) | `count` meta-argument — create multiple resources |
| [11-for-each/](11-for-each/) | `for_each` meta-argument — iterate over maps and sets |
| [12-depends_on/](12-depends_on/) | Explicit dependencies with `depends_on` |
| [13-dynamic-blocks/](13-dynamic-blocks/) | Dynamic blocks — generate repeated nested blocks |
| [14-taint-replace/](14-taint-replace/) | Taint and `-replace` flag — force resource recreation |
| [15-Debug/](15-Debug/) | Debugging with `TF_LOG` and plan analysis |
| [16-Provisioner-Null-Time-Trigger-Ramdom-File-Local/](16-Provisioner-Null-Time-Trigger-Ramdom-File-Local/) | Provisioners, null_resource, time_sleep, random |
| [17-Providers-Dependency-Lock-File/](17-Providers-Dependency-Lock-File/) | `.terraform.lock.hcl` — provider version pinning |
| [18-Refresh-only/](18-Refresh-only/) | `terraform plan -refresh-only` — sync state without changes |
| [19-workspace/](19-workspace/) | Workspaces — local and remote backends |
| [20-Manage-Providers/](20-Manage-Providers/) | Managing provider versions |
| [21-Override-Files/](21-Override-Files/) | Override files for temporary changes |
| [22-Environments/](22-Environments/) | Dev / test / prod environment patterns |
| [23-DataSource/](23-DataSource/) | Data sources — read existing infrastructure |
| [24-Import/](24-Import/) | `terraform import` — bring existing resources under management |
| [25-workspaces/](25-workspaces/) | Remote workspace patterns |
| [26-output and splat/](26-output%20and%20splat/) | Output values and splat expressions |
| [27-Jsonencode/](27-Jsonencode/) | `jsonencode()` — generate JSON from HCL |
| [28-Upgrading terraform lock files/](28-Upgrading%20terraform%20lock%20files/) | Upgrading provider lock files |
| [29-Import-Resource/](29-Import-Resource/) | `import` block (Terraform 1.5+) |
| [30-Authenticate-Terraform-to-Azure/](30-Authenticate-Terraform-to-Azure/) | Azure authentication: Service Principal, Managed Identity, CLI |
| [31-Error message/](31-Error%20message/) | Common error messages and fixes |
| [32-Remote-State-Datasource/](32-Remote-State-Datasource/) | `terraform_remote_state` data source |
| [REDME.md](REDME.md) | Practice test notes — Sentinel, state, backends |

---

## Core Workflow

```bash
# Initialise — download providers and modules
terraform init

# Validate configuration syntax
terraform validate

# Format all .tf files
terraform fmt

# Preview changes
terraform plan -out tfplan

# Apply the saved plan
terraform apply tfplan

# Destroy all resources
terraform destroy
```

## Passing Variables

```bash
# Inline variable
terraform plan -var="rg_name=my-rg" -var="location=westeurope"

# From a .tfvars file
terraform apply -var-file="production.tfvars"

# From environment variable (prefix TF_VAR_)
export TF_VAR_rg_name="my-rg"
```

## State Commands

```bash
terraform state list                    # list all managed resources
terraform state show <resource>         # inspect a specific resource
terraform state mv <old> <new>          # rename a resource in state
terraform state rm <resource>           # remove from state (no destroy)
```

## Debugging

```bash
export TF_LOG=DEBUG
terraform plan
```
