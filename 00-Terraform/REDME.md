Practice Test 3

**Sentinel** is a policy-as-code framework integrated with the HashiCorp Enterprise products. Sentinel policies are checked during plan stage. 

Terraform Cloud always **encrypts the state** at rest and protects it with TLS in transit.

The S3 backend supports encryption at rest when the encrypt option is enabled.

Provisioning infrastructure across multiple clouds increases fault tolerance, allowing for more graceful recovery from cloud provider outages. 

The **required_version setting** accepts a version constraint string, which specifies which versions of Terraform can be used with your configuration.

The **local-exec** provisioner invokes a local executable after a resource is created. This invokes a process on the machine running Terraform, not on the resource.

**Non-idempotent vs Idempoten**t: Non-idempotent is when a change is made to IaC extra resource is created, for example, a change to a VM whereas  Idempotent, the number of resources remains the same.  

If you don’t specify a backend configuration for your terraform state, this will be created by default on the directory you are working on.  

**Remote-exec** is the provider defined to execute a script after the resource is created. 

Terraform by default sets parallel execution to 10 

 Terraform allows us to define multi-cloud infrastructure resources in a single file, But we need to define and initialize all cloud provisions 

Terraform relies on plugins called **“providers”** to interact with remote systems. 

The **Terraform import** command is used to import existing resources into Terraform. 

Terraform workspace for local backend can handle different environments.

Terraform has no direct integration with vault provider for securely storing sensitive data 

Practise 2

**Provisioners** can only execute at create or destroy phase

By default per-working-directory data is written into a terraform subdirectory of the current directory The TF_DATA_DIR changes the path.

**local-exec**: to run command on the machine where terraform is running 2) use the invoke script locally  

terraform login command can be used to automatically obtain and save an API token. 

Never hardcode secrets like access keys, and passwords. Avoid saving the hardcoded secrets in the state file or configuration file. Make sure when committing to git don’t add the files where the secrets are stored. 

Terraform’s backends are divided into two main types, according to how they handle state. Enhanced backends can both store state and perform operations. There are only two enhanced backends local and remote. Standard backends only store state and reply on local backends for performing operations.

Terraform Cloud's private registry works similarly to the public Terraform Registry and helps you share Terraform providers and Terraform modules across your organization. 

Implicit and explicit dependencies data is stored in the state file.  

A single workspace can only be configured to a single version control system (git) but multiple workspaces can use the same repository 

**SSH and winrm** are supported connections types in remote-exec provisioners but not SMB and RDP

**Postgresql** is the backend database  used by Terraform Enterprise 

Terraform block is used to configure the terraform-related configuration and settings 

To access Terraform cloud API tokens is needed 

TF_LOG_PATH is used to set the log to the desired path 

Practise 4

Terraform is not meant to replicate data.

Multi-cloud deployment is to run our terraform code using multiple providers like AWS, GCP, Azure and deployed the infrasture into multiple clouds in a single terraform deployment.

To push state files from local states to backend: terraform state push “local_state”

Import: Write the code about the resource you want to import on the terraform configuration file then you can run an import of the resource.

To recreate resource example aws_security 1) terraform taint aws_security or 2) terrafrom -replace= “aws_security”

You can’t delete the default workspace 

Terraform loads the variables in the following 1) Environment variables, .tfvars, etc 

At this moment google cloud and AWS code commit don’t have integration with Terraform cloud 

All hard-mandatory policies must be passed in order to apply the Terraform configuration 

To authenticate using the cli → terraform login then a n

terraform state push “local_state” to push state files from local states to the backend configuration. 

Practice Test1 

whenever terraform is initialized all the plugin-related files are stopped and downloaded under .terrafrom/plugins 


**terraform destroy and terraform state rm** used to delete all the resources 

We can create multiple resources for the same provider, but we can’t create multiple resources for different providers without the alias command 

Whenever terraform destroys commands is issued it will empty the resource from state files and destroy the correspondence  infrastructure as well  


By default, Terraform uses a backend called local.

The **file provisioner** copies files or directories from the machine running Terraform to the newly created resource.

The **local-exec provisioner** invokes a local executable after a resource is created. This invokes a process on the machine running Terraform, not on the resource.

The **remote-exec provisione** invokes a script on a remote resource after it is created. This can be used to run a configuration management tool, bootstrap into a cluster, etc.

 
**Terraform Command Lines**
terraform -install-autocomplete #Setup tab auto-completion, requires logging back in
terraform validate -backend=false #validate code skip backend validation
Initialize your Terraform working directory
terraform init -get-plugins=false #initialize directory, do not download plugins
terraform init -verify-plugins=false #initialize directory, do not verify plugins for Hashicorp signature

**Plan, Deploy and Cleanup Infrastructure**
terraform plan -out plan.out #output the deployment plan to plan.out
terraform apply plan.out #use the plan.out plan file to deploy infrastructure
terraform plan -destroy #outputs a destroy plan
terraform apply -target=aws_instance.my_ec2 #only apply changes to the targeted resource
terraform apply -var my_region_variable=us-east-1 #pass a variable via command-line 
terraform apply -lock=true #lock the state file so it can’t be modified by any other Terraform apply 
terraform apply refresh=false # do not reconcile state file with real-world resources(helpful with large complex deployments for saving deployment time)
terraform apply --parallelism=5 #number of simultaneous resource operations
terraform refresh #reconcile the state in Terraform state file with real-world resources
terraform providers #get information about providers used in the current configuration

**Terraform Workspaces**
terraform workspace new mynewworkspace #create a new workspace
terraform workspace select default #change to the selected workspace
terraform workspace list #list out all workspaces

**Terraform State Manipulation**
terraform state show aws_instance.my_ec2 #show details stored in Terraform state for the resource
terraform state pull > terraform.tfstate #download and output terraform state to a file
terraform state mv aws_iam_role.my_ssm_role module.custom_module #move a resource tracked via state to different module
terraform state replace-provider hashicorp/aws registry.custom.com/aws #replace an existing provider with another
terraform state list #list out all the resources tracked via the current state file
terraform state rm  aws_instance.myinstace #unmanage a resource, delete it from Terraform state file

**Terraform Import And Outputs**
terraform import aws_instance.new_ec2_instance i-abcd1234 #import EC2 instance with id i-abcd1234 into the Terraform resource named “new_ec2_instance” of type “aws_instance”
terraform import 'aws_instance.new_ec2_instance[0]' i-abcd1234 #same as above, imports a real-world resource into an instance of Terraform resource
terraform output #list all outputs as stated in code
terraform output instance_public_ip # list out a specific declared output
terraform output -json #list all outputs in JSON format

**Terraform Miscelleneous commands**
terraform version #display Terraform binary version, also warns if version is old
terraform get -update=true #download and update modules in the “root” module.
Terraform Console(Test out Terraform interpolations)
echo 'join(",",["foo","bar"])' | terraform console #echo an expression into terraform console and see its expected result as output
echo '1 + 5' | terraform console #Terraform console also has an interactive CLI just enter “terraform console”
echo "aws_instance.my_ec2.public_ip" | terraform console #display the Public IP against the “my_ec2” Terraform resource as seen in the Terraform state file

**Terraform Graph(Dependency Graphing)**
terraform graph | dot -Tpng > graph.png #produce a PNG diagrams showing relationship and dependencies between Terraform resource in your configuration/code
Terraform Taint/Untaint(mark/unmark resource for recreation -> delete and then recreate)
terraform taint aws_instance.my_ec2 #taints resource to be recreated on next apply
terraform untaint aws_instance.my_ec2 #Remove taint from a resource
terraform force-unlock LOCK_ID #forcefully unlock a locked state file, LOCK_ID provided when locking the State file beforehand

**Terraform Cloud**
terraform login #obtain and save API token for Terraform cloud
terraform logout #Log out of Terraform Cloud, defaults to hostname app.terraform.io
terraform replace: to relace a resource 
