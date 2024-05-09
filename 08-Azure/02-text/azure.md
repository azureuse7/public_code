# Azure

- Connect-AzAccount
- az account list --all
- az account show
- Disconnect-AzAccount
- az account set --subscription 'Visual Studio Professional Subscription'**	


nano ~/.zshrc
source ~/.bash_profile

- An SSH key consists of two components: a public key and a private key. These keys are generated using cryptographic algorithms, and they work together as a pair. 
The public key is meant to be shared with others, while the private key must be kept secret and protected. 
Therefore, the private key remains securely stored on the developer's local machine & the public key can be safely shared with GitHub.



- For planned maintenance: two update domains 
- AzCopy : copy blobs or file from storage account 
- Azure table storage support Persistent storage 
- Redeploy a VM moves the VM to a new node 
- Swap deployment slots: azure swaps the IP address of the source and destination 
- DNS : 53 
- Single Availability zone consist of more than one data centre 
- You can only add one cloud end point, but two server end point  
- NSG: must be in same region, but you can use across RG’s, VNETS
- Service Recovery vault should be in the same region of the VM and storage account 
- Log analytics can be in any region 
- Azure Application gateway is web traffic load balancer 
- Network interface needs to be in the same region as VNET
- Import job: Blobs and azure files. Export only Blobs 
- Replication of storage can be changed if technique is LRS and GRS
App service plan and web app must be in same region.
. NET can run on both windows and Linux,  But ASP.NET =  only Windows
Kubectl apply to deploy application.
Network interface can be moved to another resource group even if it is part of existing virtual network 
Fault domain set is 3 , update domain 20 
Gateway subnet is required for site to site VPN, not for peering  
You can change a subnet connected to a VM, but not the VNET 
Policy definition is used to enforce policy.
Az aks create to create AKS cluster and –enable-addons to enable monitoring 
To record connections 1) Microsoft insight 2) storage account 3) enable network watcher flow logs 
Backup/Restore standard app service plan 
Client certificate needs to be installed on every client computer; it can even be exported (Site to site VPN) 
Standard load balancer has 99% availability 
Connection monitor in network watcher if application is slow (also used in connection between two VM’s) 
IP flow verify checks if security rule is preventing  
Variable packet capture monitor for security check 
Scale -set: NO SLA 
Availability zone set & managed disks: SLA 99% up 
Peering must be in both direction 
Archie tier only in General Purpose V2 and Blob storage 
Port for file share from home: SMB 445
Replication types 
To modify retention data in storage account: Soft Delete 
Manage storage account: storage account contributor 
Manage container: storage blob data contributor 
Full access: storage blob data owner 
Stop the VM before back up 
Read roles: Microsoft. authorisation/*/read
To run a log query for errors: search in (Events) “errors”
To add/enable/disable device: Cloud device administrator 
Fraud alert: users can report fraudulent attempts 
Contributor role cannot assign roles.
security admin role only has privilege to work with security centre 
Scale set used to scale load for availability: availability   sets 
To access azure without verification code: use multi-factor authentication service settings 
UNC path: file explorer: storageaccountname. File.core.window.net\filesharename
Only one end point per sync group.
GRS: geo-redundant storage: data is in two regions 
Website control in firewall: Application collection rules 
Only one app service per resource 
If client is registered with private hosted zone: automatic registration of VM is possible 
Custom role: starts with get-azroleDefination, 
New-azroledefination 
To move a VM: move-AzResouces  
Change to the VPN: 1) Remove VPN connection 2) Modify the local gateway IP ) Recreate the VPN connection 
Staging mode must be disabled, if the azure AD connect server is in staging mode, password has synchronization is temporarily disabled  
Logic app contributor: manage, but you cannot change access to them
Logic app operator: read/enable/disable but cannot edit or update them   
Storage File Data SMB share reader: Read access in the storage over SMB
Contributor : read, write, delete 
Elevated contributor: read, write, delete, NTFS permission 
When running Json : group create, deployment and template-file 
For planned maintenance : two update domains 
Basic: Virtual machines in a single availability set or virtual machine scale set
Standard: any virtual machine or virtual machine scale set in a single virtual network
