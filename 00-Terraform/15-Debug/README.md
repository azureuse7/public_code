# Terraform Debug

## Step-01: Introduction

Terraform provides built-in logging that can be enabled via environment variables. This is useful for troubleshooting provider issues, unexpected plan output, or understanding what Terraform does internally.

- Learn about Terraform debug logging
- `TF_LOG` controls the log level; `TF_LOG_PATH` controls where logs are written
- **Allowed log levels for `TF_LOG`:**
  - **TRACE:** Very detailed verbosity; shows every step taken by Terraform and produces large outputs with internal logs
  - **DEBUG:** Describes what happens internally in a more concise way compared to TRACE
  - **ERROR:** Shows errors that prevent Terraform from continuing
  - **WARN:** Logs warnings that may indicate misconfiguration or mistakes, but are not critical to execution
  - **INFO:** Shows general, high-level messages about the execution process

## Step-02: Set Up TRACE Logging in Terraform

```bash
# Set Terraform trace log settings
export TF_LOG=TRACE
export TF_LOG_PATH="terraform-trace.log"
echo $TF_LOG
echo $TF_LOG_PATH

# Terraform initialize
terraform init

# Terraform validate
terraform validate

# Terraform plan
terraform plan

# Terraform apply
terraform apply -auto-approve

# Terraform destroy
terraform destroy -auto-approve

# Clean up
rm -rf .terraform*
rm -rf terraform.tfstate*
rm terraform-trace.log
```

## Step-03: Set Up These Environment Variables Permanently on Your Desktop

### Linux Bash

Open your `.bashrc` file, which is located in your home directory.

```bash
# Navigate to home directory
cd $HOME
vi .bashrc

# Add the following Terraform log settings
export TF_LOG=TRACE
export TF_LOG_PATH="terraform-trace.log"

# Verify after saving the file in a new terminal
$ echo $TF_LOG
TRACE
$ echo $TF_LOG_PATH
terraform-trace.log
```

### Windows PowerShell

Set up using the PowerShell profile. Open `$profile` in a PowerShell window, add the following lines, then close and reopen the console to verify.

```powershell
# Windows PowerShell - Terraform log settings
$env:TF_LOG="TRACE"
$env:TF_LOG_PATH="terraform.txt"

# Open a new PowerShell window and verify
echo $env:TF_LOG
echo $env:TF_LOG_PATH
```

### macOS

Update the values in `.bash_profile` at the end of the file.

```bash
# Navigate to home directory
cd $HOME
vi .bash_profile

# Add the following Terraform log settings
export TF_LOG=TRACE
export TF_LOG_PATH="terraform-trace.log"

# Verify after saving the file in a new terminal
$ echo $TF_LOG
TRACE
$ echo $TF_LOG_PATH
terraform-trace.log
```

## Step-04: Terraform Crash Log

If Terraform ever crashes (a "panic" in the Go runtime), it saves a log file with the debug logs from the session as well as the panic message and backtrace to `crash.log`.

- This log file is generally meant to be submitted to the Terraform developers via a GitHub issue.
- As a user, you are not required to dig into this file.
- Reference: [How to read a crash log](https://www.terraform.io/docs/internals/debugging.html#interpreting-a-crash-log)
