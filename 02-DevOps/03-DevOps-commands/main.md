# Azure DevOps Logging Commands

Logging commands are how tasks and scripts communicate with the Azure Pipelines agent. They cover actions like creating new variables, marking a step as failed, and uploading artifacts.

Reference: [Azure DevOps Logging Commands Documentation](https://learn.microsoft.com/en-us/azure/devops/pipelines/scripts/logging-commands?view=azure-devops&tabs=bash)

## Invoking a Logging Command

To invoke a logging command, write the command to standard output using the `##vso[...]` syntax.

**Bash:**

```bash
#!/bin/bash
echo "##vso[task.setvariable variable=testvar;]testvalue"
```

**PowerShell:**

```powershell
Write-Host "##vso[task.setvariable variable=testvar;]testvalue"
```
