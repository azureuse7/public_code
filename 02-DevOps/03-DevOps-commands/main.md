#### Logging commands

- Logging commands are how tasks and scripts communicate with the agent. They cover actions like creating new variables, marking a step as failed, and uploading artifacts.

#### To invoke a logging command, echo the command via standard output.
#!/bin/bash
echo "##vso[task.setvariable variable=testvar;]testvalue"

Powershell
Write-Host "##vso[task.setvariable variable=testvar;]testvalue"

https://learn.microsoft.com/en-us/azure/devops/pipelines/scripts/logging-commands?view=azure-devops&tabs=bash


