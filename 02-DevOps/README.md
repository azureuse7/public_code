# Azure DevOps

> Guides and pipeline configurations for Azure DevOps — covering GitHub authentication, service connections, pipeline YAML, and infrastructure provisioning with Terraform.

---

## Contents

| Directory | Topic |
|-----------|-------|
| [01Access-to-GitHub-repositories/](01Access-to-GitHub-repositories/) | Connecting Azure DevOps to GitHub (PAT, OAuth, App auth) |
| [02-Service-connection/](02-Service-connection/) | Creating Azure service connections for pipeline deployments |
| [03-DevOps-commands/](03-DevOps-commands/) | Useful Azure DevOps CLI and portal commands |
| [04-Pipelines/](04-Pipelines/) | Pipeline YAML examples |
| [01-PipelineToCreateVM/](01-PipelineToCreateVM/) | End-to-end pipeline that provisions Azure VMs with Terraform |

---

## GitHub Authentication Methods

Three ways to authenticate Azure DevOps to a GitHub repository:

| Method | File | Best For |
|--------|------|---------|
| Personal Access Token | [PAT_authentication.md](01Access-to-GitHub-repositories/PAT_authentication.md) | Quick setup, individual use |
| OAuth | [OAuth_authentication.md](01Access-to-GitHub-repositories/OAuth_authentication.md) | User-delegated access |
| GitHub App | [app_authentication_to github.md](01Access-to-GitHub-repositories/app_authentication_to%20github.md) | Org-wide, fine-grained permissions |

---

## Pipeline to Create a VM

The `01-PipelineToCreateVM/` directory contains a complete example:
- Azure DevOps pipeline YAML that triggers Terraform
- Terraform configuration to provision an Azure VM
- Variable management and tfvars handling

---

## Key DevOps Concepts

- **Service Connection**: An Azure DevOps resource that stores credentials for connecting to Azure, GitHub, or other services — referenced in pipeline YAML as `azureSubscription`.
- **Variable Groups**: Centrally managed variables that can be linked to pipelines and pulled into scripts.
- **Pipeline Stages**: `stages > jobs > steps` hierarchy — each stage can have approval gates and dependency conditions.
- **##vso logging commands**: Special `echo` strings (e.g. `##vso[task.setvariable]`) that communicate between pipeline tasks.
