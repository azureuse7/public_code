# Terraform Null Resource, Time Provider, and Triggers

## Step-01: Introduction

This section demonstrates how to use the `null_resource` with provisioners and the `time` provider to sync content to a VM after it is created. A `null_resource` with a `timestamp()` trigger is used to force re-execution on every `terraform apply`.

- Understand the [Null Provider](https://registry.terraform.io/providers/hashicorp/null/latest/docs)
- Understand the [Null Resource](https://www.terraform.io/docs/language/resources/provisioners/null_resource.html)
- Understand the [Time Provider](https://registry.terraform.io/providers/hashicorp/time/latest/docs)
- **Use case:** Force a resource to update based on a changed `null_resource`
- Create a `time_sleep` resource to wait 90 seconds after an Azure Linux VM instance is created
- Create a `null_resource` with the following provisioners:
  1. **File Provisioner:** Copy the `apps/app1` folder to `/tmp`
  2. **Remote-Exec Provisioner:** Copy the `app1` folder from `/tmp` to `/var/www/html`
- Topics covered:
  1. `null_resource`
  2. `time_sleep` resource
  3. How to force a resource to update based on a changed `null_resource` using the `timestamp()` function and `triggers`

## Step-02: Define the Null Provider in the Terraform Settings Block

Update the null provider info in `c1-versions.tf`:

```hcl
null = {
  source  = "hashicorp/null"
  version = ">= 3.0.0"
}
```

## Step-03: Define the Time Provider in the Terraform Settings Block

Update the time provider info in `c1-versions.tf`:

```hcl
time = {
  source  = "hashicorp/time"
  version = ">= 0.6.0"
}
```

## Step-04: Create/Review the `c8-null-resource.tf` Terraform Configuration

### Step-04-01: Create the Time Sleep Resource

This resource waits 90 seconds after the VM instance is created. The wait time allows the VM to finish provisioning the Apache web server and creating all its relevant folders. The static content folder `/var/www/html` must exist before it can be used as a copy destination.

```hcl
# Wait for 90 seconds after creating the Azure Virtual Machine instance
resource "time_sleep" "wait_90_seconds" {
  depends_on      = [azurerm_linux_virtual_machine.mylinuxvm]
  create_duration = "90s"
}
```

### Step-04-02: Create the Null Resource

- The `null_resource` uses a `triggers` block with `timestamp()`, which causes it to be replaced on every `terraform apply`.
- This allows static content to be synced to the VM instance whenever `terraform apply` is run.
- Key concepts:
  - `null_resource` and how it executes provisioners
  - `null_resource` triggers
  - How a trigger based on `timestamp()` works
  - Provisioners inside a `null_resource`

```hcl
# Terraform null_resource - sync app1 static content to webserver using provisioners
resource "null_resource" "sync_app1_static" {
  depends_on = [time_sleep.wait_90_seconds]

  triggers = {
    always-update = timestamp()
  }

  # Connection block for provisioners to connect to the Azure VM instance
  connection {
    type        = "ssh"
    host        = azurerm_linux_virtual_machine.mylinuxvm.public_ip_address
    user        = azurerm_linux_virtual_machine.mylinuxvm.admin_username
    private_key = file("${path.module}/ssh-keys/terraform-azure.pem")
  }

  # Copies the app1 folder to /tmp
  provisioner "file" {
    source      = "apps/app1"
    destination = "/tmp"
  }

  # Copies the /tmp/app1 folder to the Apache webserver /var/www/html directory
  provisioner "remote-exec" {
    inline = [
      "sudo cp -r /tmp/app1 /var/www/html"
    ]
  }
}
```

## Step-05: Execute Terraform Commands

```bash
# Terraform initialize
terraform init

# Terraform validate
terraform validate

# Terraform format
terraform fmt

# Terraform plan
terraform plan

# Terraform apply
terraform apply -auto-approve

# Verify files on the VM
ssh -i ssh-keys/terraform-azure.pem azureuser@<PUBLIC-IP>
ls -lrt /tmp
ls -lrt /tmp/app1
ls -lrt /var/www/html
ls -lrt /var/www/html/app1

# Verify web content (replace <public-ip> with the actual IP)
# http://<public-ip>/app1/app1-file1.html
# http://<public-ip>/app1/app1-file2.html
```

## Step-06: Create a New File Locally in the `app1` Folder

- Create a new file named `app1-file3.html`
- Update `app1-file1.html` with some additional content

**`file3.html`:**

```html
<h1>App1 File3</h1>
```

**`file1.html`:**

```html
<h1>App1 File1 - Updated</h1>
```

Sample `terraform plan` output showing the null resource will be replaced:

```log
Terraform used the selected providers to generate the following execution plan. Resource actions
are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # null_resource.sync_app1_static must be replaced
-/+ resource "null_resource" "sync_app1_static" {
      ~ id       = "256904776759333943" -> (known after apply)
      ~ triggers = {
          - "always-update" = "2021-06-14T05:44:33Z"
        } -> (known after apply) # forces replacement
    }

Plan: 1 to add, 0 to change, 1 to destroy.
```

## Step-07: Execute Terraform Plan and Apply Commands

```bash
# Terraform plan
# Observation: You should see changes for "null_resource.sync_app1_static" because
# the trigger will have a new timestamp value
terraform plan

# Terraform apply
terraform apply -auto-approve

# Verify files on the VM
ssh -i ssh-keys/terraform-azure.pem azureuser@<PUBLIC-IP>
ls -lrt /tmp
ls -lrt /tmp/app1
ls -lrt /var/www/html
ls -lrt /var/www/html/app1

# Verify web content (replace <public-ip> with the actual IP)
# http://<public-ip>/app1/app1-file1.html
# http://<public-ip>/app1/app1-file3.html
```

## Step-08: Clean Up Resources and Local Working Directory

```bash
# Terraform destroy
terraform destroy -auto-approve

# Delete Terraform files
rm -rf .terraform*
rm -rf terraform.tfstate*
```

## Step-09: Roll Back to Demo State

```bash
# Change-1: Delete app1-file3.html from the apps/app1 folder
# Change-2: Remove the updated text from app1-file1.html
```

## References

- [Resource: time_sleep](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep)
- [Time Provider](https://registry.terraform.io/providers/hashicorp/time/latest/docs)
