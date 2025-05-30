- **Private** **Endpoints** grant network access to specific resources behind a given service providing granular segmentation. Traffic can reach the service resource from on premises without using public endpoints.

- A **Service** **Endpoint** remains a publicly routable IP address. A Private Endpoint is a private IP in the address space of the virtual network where the private endpoint is configured.

- For simplicity, let's take the view of a VM in a VNET connecting to a storage account in the same subscription and same Azure region. There are three ways to connect.


<img src="images/2.png">

# Default

By default all traffic goes against the public endpoint of the storage account. Source IP of the traffic is the Public IP of the VM.


# Service Endpoints

Traffic is still directed against the public endpoint of the storage account but the source IP has changed to the private IP of the VM. In fact, the traffic is also using the VNET and Subnet as source in the network dataframe.

Create a subnet and enable service endpoint 
<img src="images/10.png">

Add that subnet to the stoarge account 
<img src="images/11.png">


- Now communication can be done from subnet to stoarge account with out goig ove the interent

# Private Endpoints
<img src="images/1.png">

The PaaS service now gets a virtual network interface inside the subnet and traffic from the VM to the storage account is now directed against the private IP address.



- Create  a private endpoint  
<img src="images/5.png">

- attach to stoarge account
<img src="images/15.png">

- Confirm its attached 
<img src="images/6.png">

- Check the VNET and its connectd
<img src="images/7.png">

- Confirm its the Network interface that is attached to stoarge account 
<img src="images/8.png">






https://learn.microsoft.com/en-us/azure/private-link/private-link-faq#what-is-the-difference-between-service-endpoints-and-private-endpoints-

https://www.youtube.com/watch?v=qkeZO0K58Po