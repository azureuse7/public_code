####  Azure

- Connect-AzAccount
- az account list --all
- az account show
- Disconnect-AzAccount
- az account set --subscription 'Visual Studio Professional Subscription'**	


##############################################################


- Single Availability zone consist of more than one data centre 
- 
  
- NSG: must be in same region, but you can use across RG’s, VNETS
-
- Log analytics can be in any region 
- 
- Azure Application gateway is web traffic load balancer 
- 
- Network interface needs to be in the same region as VNET
- 
- Replication of storage can be changed if technique is LRS and GRS
  
- App service plan and web app must be in same region.
  
- . NET can run on both windows and Linux,  But ASP.NET =  only Windows

- Network interface can be moved to another resource group even if it is part of existing virtual network 
- 
- Fault domain set is 3 , update domain 20 
- 
- Gateway subnet is required for site to site VPN, not for peering  
- 
- You can change a subnet connected to a VM, but not the VNET 
- 
- Policy definition is used to enforce policy.
- 
- Az aks create to create AKS cluster and –enable-addons to enable monitoring 
- 
- To record connections 1) Microsoft insight 2) storage account 3) enable network watcher flow logs 
 
- Client certificate needs to be installed on every client computer; it can even be exported (Site to site VPN) 
- 
- Standard load balancer has 99% availability 
- 
- Connection monitor in network watcher if application is slow (also used in connection between two VM’s) 
- 
- IP flow verify checks if security rule is preventing  
- 

- Peering must be in both direction 

