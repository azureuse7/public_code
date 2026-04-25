L7 (Layer 7) — Application-aware policies & routing

What it is: “Application layer” context (HTTP/1.1, HTTP/2, gRPC, Kafka, MySQL, DNS…). Goes beyond L3/L4 IPs/ports to understand methods, paths, headers, topics, etc.

L7, encryption, FQDN filtering, Hubble, Cilium mesh




In Kubernetes, "Host Identity" refers to the cryptographic identity of a node (a physical or virtual machine) within the cluster. It is not the human-readable hostname (e.g., node-1-vm), but a machine-verifiable credential, almost always an X.509 client certificate, that the node uses to authenticate itself to the Kubernetes API Server.

#### IPAM (IP Address Management)
In its essence, IPAM is a methodology and a set of tools for planning, tracking, and managing the IP address space on a network. Think of it as the "DNS, DHCP, and IP Address Directory" all rolled into one cohesive management system

##### Before we talk about Kubernetes, let's look at the core functions of a traditional IPAM system:

- Discovery and Inventory: Automatically finds all IP-enabled devices on the network and builds a database of what IP address is assigned to what device.

- DHCP Management: Centralizes the configuration and control of DHCP servers, which are responsible for dynamically assigning IP addresses to clients.

- DNS Management: Manages DNS records, ensuring that hostnames correctly resolve to their corresponding IP addresses.

- IP Address Space Management: Provides a single pane of glass to view all subnets, IP ranges, and the utilization within them (used vs. free addresses). This prevents IP conflicts.

##### In short, traditional IPAM ensures that every device gets a unique IP, can be found by name, and that network administrators don't run out of IPs or create conflicts.

##### How IPAM Works in Kubernetes
- Kubernetes is a highly dynamic environment. Pods (the smallest deployable units) are constantly being created, destroyed, and moved across nodes. A static, manual IP assignment process is impossible at this scale. Therefore, Kubernetes has a built-in, automated IPAM mechanism that is integral to its networking model.

##### The Core Kubernetes Networking Requirement
- First, recall the fundamental Kubernetes networking model: Every Pod gets its own unique IP address. This "IP-per-Pod" model simplifies application design because Pods can talk to each other directly without port conflicts or complex NAT rules, regardless of which node they are on.

- The Kubernetes IPAM system is the engine that fulfills this requirement.

##### The Key Components and The Flow
- Kubernetes itself doesn't handle the low-level IP assignment. It delegates this task to the Container Network Interface (CNI) plugin. 
- The IPAM logic is often a sub-component of the CNI plugin or a standalone IPAM plugin that the CNI plugin calls.

##### Here are the most common IPAM strategies in Kubernetes:

1. host-local IPAM (Most Common in On-Prem)

- This is the default IPAM plugin for many CNI plugins like Calico (in certain modes), Flannel, and Weave.

##### How it Works:

- Configuration: The cluster administrator defines a large IP address range (a CIDR block) for the entire cluster, e.g., 10.244.0.0/16.

- Node Subnets: This large range is automatically divided into smaller subnets assigned to each node. For example, Node1 gets 10.244.1.0/24, Node2 gets 10.244.2.0/24, and so on.

- Local Allocation: On each node, the CNI plugin (using the host-local IPAM) manages its own /24 subnet. It maintains a simple local file (e.g., in /var/lib/cni/) to keep track of which IPs in that segment have been assigned.

Pod Creation Flow:

The kubelet on a node decides to start a Pod.

It invokes the configured CNI plugin.

The CNI plugin calls its IPAM component (e.g., host-local).

The host-local IPAM checks its local file for the node's subnet, finds a free IP (e.g., 10.244.1.5), marks it as "used," and returns it to the CNI plugin.

The CNI plugin configures the Pod's network interface (veth pair) with this IP.

Advantage: Simple, efficient, and avoids the need for a central network server.

Disadvantage: Can lead to IP waste if nodes are assigned subnets but run very few pods.

2. Cloud Provider IPAM (AWS, Azure, GCP)

When Kubernetes runs on a major cloud platform, it leverages the cloud's own native IPAM.

#### How it Works:

- The cluster is deployed within a cloud VPC (Virtual Private Cloud), e.g., with CIDR 10.0.0.0/16.

- Each node (a VM) is assigned to a subnet within the VPC and gets a primary IP from that subnet.

- When a Pod is created, the CNI plugin (like the AWS VPC CNI or Azure CNI) calls the cloud provider's API.

- The cloud API allocates a secondary IP address from the node's VPC subnet and assigns it to the node's virtual network interface.

- The CNI plugin then places this IP inside the Pod's network namespace.

##### Advantage: Tight integration with the cloud platform. Pod IPs are first-class citizens in the VPC routing table, enabling direct communication between Pods and other cloud services (like databases) without leaving the VPC.

##### Disadvantage: You are limited by the cloud's quotas on IPs per network interface and per instance type.


#### A Practical Example Flow
#### Let's trace the journey of an IP address for a new Pod using host-local IPAM:

- User Command: kubectl apply -f my-pod.yaml

- kube-scheduler: Decides which node (e.g., node-01) will run the Pod and informs the kubelet on that node.

- kubelet: Sees a new Pod needs to be created. Before starting the containers, it needs to set up networking.

- CNI Plugin Invocation: The kubelet looks at its --cni-conf-dir and invokes the CNI plugin (e.g., calico or flannel) executable.

- CNI Calls IPAM: The CNI plugin reads its configuration, which specifies the IPAM type (e.g., "type": "host-local") and the pool it should use ("subnet": "10.244.1.0/24").

- host-local IPAM Action:

###### The host-local plugin checks its local state file for node-01 (e.g., /var/lib/cni/networks/mynet/).

###### It finds the next available IP, let's say 10.244.1.15.

###### It creates a file named 10.244.1.15 in that directory as a reservation.

###### It returns this IP to the CNI plugin.

- Network Setup: The CNI plugin now has the IP. It:

###### Creates a virtual Ethernet pair (veth).

###### Places one end inside the Pod's network namespace.

###### Assigns the IP 10.244.1.15 to it.

###### Configures routes and connects the other end to the node's bridge/cni0 interface.

- Pod Startup: The kubelet proceeds to start the containers in the Pod. The Pod now has a fully configured network stack with the IP 10.244.1.15.

##### When the Pod is deleted, this entire process reverses, and the host-local IPAM plugin deletes the reservation file, freeing the IP 10.244.1.15 for future use.