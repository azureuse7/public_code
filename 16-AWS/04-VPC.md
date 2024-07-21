Amazon Virtual Private Cloud (Amazon VPC) is a service that allows you to launch AWS resources into a logically isolated virtual network that you define. You have complete control over your virtual networking environment, including the selection of your own IP address range, creation of subnets, and configuration of route tables and network gateways.

#### Key Features of Amazon VPC
##### 1) Network Isolation:

- Create a logically isolated network within the AWS cloud.
- Define your own IP address range using CIDR notation (e.g., 10.0.0.0/16).
##### 2) Subnets:

- Divide your VPC into subnets, each of which resides in a single Availability Zone.
- Public Subnets: Subnets that have direct access to the internet via an Internet Gateway.
- Private Subnets: Subnets that do not have direct internet access and are often used for backend resources.
##### 3) Routing and Gateways:

- **Route Tables**: Control the routing of traffic within your VPC.
- **Internet Gateway**: Provides internet access to instances in public subnets.
- **NAT Gateway/Instance**: Allows instances in private subnets to access the internet without exposing them to incoming traffic from the internet.
- **Virtual Private Gateway**: Connects your VPC to your on-premises network using a VPN connection.
##### 4) Security:

- **Security Groups**: Act as virtual firewalls for your instances to control inbound and outbound traffic.
- **Network Access Control Lists (NACLs)**: Provide an additional layer of security by controlling traffic to and from subnets.
- **Flow Logs**: Capture and log information about the IP traffic going to and from network interfaces in your VPC.
##### 5) Elastic IP Addresses:

- Static, public IP addresses designed for dynamic cloud computing.
##### 6) Peering Connections:

- **VPC Peering**: Connect your VPC with another VPC to enable routing of traffic between them using private IP addresses.
- **Transit Gateway**: A central hub that can connect multiple VPCs and on-premises networks.
##### 7) Interface Endpoints and Gateway Endpoints:

- **Interface Endpoints**: Enable private connectivity between your VPC and supported AWS services without requiring an internet gateway, NAT device, VPN connection, or AWS Direct Connect.
- **Gateway Endpoints**: Provide a private route to specific AWS services like S3 and DynamoDB.
#### Common Use Cases
##### 1) Hosting Web Applications:

- Host public-facing applications in public subnets and backend databases or services in private subnets for enhanced security.
##### 2) Hybrid Cloud Architectures:

- Extend your on-premises network into the AWS cloud using VPN or AWS Direct Connect.
##### 3) Data Processing and Analytics:

- Process and analyze data using EC2 instances, EMR clusters, and other AWS services in a secure, isolated environment.
##### 4) Disaster Recovery:

- Use VPCs to create backup and recovery solutions that replicate your on-premises environment in the cloud.
### Example: Creating a Simple VPC
- Here is a step-by-step example of creating a simple VPC using the AWS Management Console and AWS CLI.

##### Using AWS Management Console
##### 1) Create a VPC:

- Open the Amazon VPC console.
- Click on "Your VPCs" and then "Create VPC."
- Enter the VPC details such as name, CIDR block (e.g., 10.0.0.0/16), and other optional settings.
- Click "Create VPC."
##### 2) Create Subnets:

- Navigate to "Subnets" in the VPC console.
- Click "Create Subnet."
- Choose the VPC you just created.
- Specify the subnet details such as name, Availability Zone, and -  CIDR block (e.g., 10.0.1.0/24 for public, 10.0.2.0/24 for private).
- Click "Create."
##### 3) Create an Internet Gateway:

- Navigate to "Internet Gateways" in the VPC console.
- Click "Create Internet Gateway."
- Attach the internet gateway to your VPC.
##### 4) Update Route Tables:

- Navigate to "Route Tables" in the VPC console.
- Select the route table associated with your VPC.
- Edit the route table to add a route to the internet gateway (0.0.0.0/0 -> igw-id).
##### 5) Set Up Security Groups:

- Navigate to "Security Groups" in the VPC console.
- Create and configure security groups to control inbound and outbound traffic for your instances.
#### Using AWS CLI
##### 1) Create a VPC:
sh
```
aws ec2 create-vpc --cidr-block 10.0.0.0/16
```
##### 2) Create Subnets:
sh
```
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.1.0/24 --availability-zone us-west-2a
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.2.0/24 --availability-zone us-west-2b
```
##### 3) Create an Internet Gateway:
sh
```
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-12345678 --internet-gateway-id igw-12345678
```
##### 4) Update Route Tables:
sh
```
aws ec2 create-route --route-table-id rtb-12345678 --destination-cidr-block 0.0.0.0/0 --gateway-id igw-12345678
```
##### 5) Set Up Security Groups:
sh
```
aws ec2 create-security-group --group-name my-sg --description "My security group" --vpc-id vpc-12345678
aws ec2 authorize-security-group-ingress --group-id sg-12345678 --protocol tcp --port 22 --cidr 0.0.0.0/0
```
##### Conclusion
Amazon VPC provides a flexible and secure way to manage your network infrastructure in the AWS cloud. With features like custom IP address ranges, subnets, routing, security groups, and various connectivity options, you can design and operate a network that meets your specific requirements. Whether you are hosting a web application, running data processing jobs, or extending your on-premises network to the cloud, VPC offers the tools and flexibility needed to create a robust and secure networking environment.




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