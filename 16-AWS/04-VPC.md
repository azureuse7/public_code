# VPC

https://aws.plainenglish.io/aws-vpc-refresher-40ac90196ea8

- If someone wants to access an application in VPC from the Internet, examplew he wants to tecah 172.2.16.1

- VPC will have a network range

- Within VPC there will be a subnet

- Traffic will need to pass via internet gateway

- Internet --> Public subnet ->> Load balancer.
  
- How will LB know where to go --> Route tables define the path.

- Security Group sets before the subnet, it can block or accept the request




To connect your VPC to the internet or other networks, you can set up gateways or routers. These act as entry and exit points for traffic going in and out of your VPC.


![image](https://github.com/iam-veeramalla/aws-devops-zero-to-hero/assets/43399466/12cc10b6-724c-42c9-b07b-d8a7ce124e24)

By default, when you create an AWS account, AWS will create a default VPC for you but this default VPC is just to get started with AWS. You should create VPCs for applications or projects. 

## VPC components 

The following features help you configure a VPC to provide the connectivity that your applications need:

Virtual private clouds (VPC)

    A VPC is a virtual network that closely resembles a traditional network that you'd operate in your own data center. After you create a VPC, you can add subnets.
Subnets

    A subnet is a range of IP addresses in your VPC. A subnet must reside in a single Availability Zone. After you add subnets, you can deploy AWS resources in your VPC.
IP addressing

    You can assign IP addresses, both IPv4 and IPv6, to your VPCs and subnets. You can also bring your public IPv4 and IPv6 GUA addresses to AWS and allocate them to resources in your VPC, such as EC2 instances, NAT gateways, and Network Load Balancers.

Network Access Control List (NACL)

    A Network Access Control List is a stateless firewall that controls inbound and outbound traffic at the subnet level. It operates at the IP address level and can allow or deny traffic based on rules that you define. NACLs provide an additional layer of network security for your VPC.
   
Security Group

    A security group acts as a virtual firewall for instances (EC2 instances or other resources) within a VPC. It controls inbound and outbound traffic at the instance level. Security groups allow you to define rules that permit or restrict traffic based on protocols, ports, and IP addresses.  

Routing

    Use route tables to determine where network traffic from your subnet or gateway is directed.
Gateways and endpoints

    A gateway connects your VPC to another network. For example, use an internet gateway to connect your VPC to the internet. Use a VPC endpoint to connect to AWS services privately, without the use of an internet gateway or NAT device.
Peering connections

    Use a VPC peering connection to route traffic between the resources in two VPCs.
Traffic Mirroring

    Copy network traffic from network interfaces and send it to security and monitoring appliances for deep packet inspection.
Transit gateways

    Use a transit gateway, which acts as a central hub, to route traffic between your VPCs, VPN connections, and AWS Direct Connect connections.
VPC Flow Logs

    A flow log captures information about the IP traffic going to and from network interfaces in your VPC.
VPN connections

    Connect your VPCs to your on-premises networks using AWS Virtual Private Network (AWS VPN).


## Resources 

VPC with servers in private subnets and NAT

https://docs.aws.amazon.com/vpc/latest/userguide/vpc-example-private-subnets-nat.html

![image](https://github.com/iam-veeramalla/aws-devops-zero-to-hero/assets/43399466/89d8316e-7b70-4821-a6bf-67d1dcc4d2fb)

<img src="images/3.png">


https://varunmanik1.medium.com/how-to-create-aws-vpc-in-10-steps-less-than-5-min-a49ac12064aa