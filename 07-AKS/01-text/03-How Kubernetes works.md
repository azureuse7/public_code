# Kubernetes node

- A node in a Kubernetes cluster is where your compute workloads run. It would be a VM or VMSS

- Each node communicates with the control plane via the API server to inform it about state changes on the node.
  

# Master 

# 1 Kube-apiserver:
It acts as a front end for the Kubernetes control plane It exposes the Kubernetes API
CLI tools like kubectl, user and even master components like scheduler, control manager, etcd and worker nodes components like (Kubelet) everything talks to the API server
The API Server . It also acts as the gateway to the cluster, so the API server must be accessible by clients from outside the cluster.


# 2  Etcd:
Used as Kubernetes’s backing store for all cluster data
It stores all the master and worker node information

# 3. Kuber-scheduler:

The scheduler is responsible for distributing containers across multi nodes
It watches for newly created Pods with no assigned nodes and selects a node for them to run on.

# 4 Kuber-control-manager

Controllers are responsible for noticing and responding when nodes, container,s or endpoints go down, They make decisions to bring up new containers in such cases
- Node Controller: Responsible for noticing and responding when nodes go down
- Replication controller: Responsible for maintaining the correct number of pods for every replication controller object in the system
- Endpoint controller: Populates the endpoint object( thst is join services and pods)
- Service Account and token controller: Creates default accounts and API access for new namespaces


# 5 Cloud-controller-manager:

- A Kubernetes control plane component that embeds cloud-specific control logic
It only runs controllers that are specific to your cloud provider
- On- Premises Kubernetes cluster will not have this components
- Node controller: For checking the cloud provider to determine if a node has been deleted in the cloud after it stops responding
- Route Controller: For Setting up routes in the underlying cloud infrastructure
- Service Controller: For Creating, updating and deleting cloud provider load balancer  

 

# Worker Node

# 1 Container Runtime:
Is the underlying software where we run all these components
We are using docker. But we have other runtimes like rkt, container-d etc

# 2 Kubelet:
- Kuberlet is the agent that runs on every node in the cluster
- This agent is responsible for making sure that containers are running in a Pod on node.


# 3 Kube-proxy
It is a network proxy that runs on each node in your cluster
It maintains network rules on nodes
In short, these network rules allow network communication to    yor pods from network session inside or outside of your cluster         


# Kubernetes pods
- The workloads that you run on Kubernetes are containerized apps. Unlike in a Docker environment, you can't run containers directly on Kubernetes. You package the container into a Kubernetes object called a pod.
- A single pod can hold a group of one or more containers. However, a pod typically doesn't contain multiples of the same app.

# There are various types of pods:

- ReplicaSet, the default, is a relatively simple type. It ensures the specified number of pods are running A selector enables the replica set to identify all the pods running underneath it. Using this feature, you can manage pods labeled with the same value as the selector value, but not created with the replicated set.
- Deployment is a declarative way of managing pods via ReplicaSets. Includes rollback and rolling update mechanisms Deployments make use of YAML-based definition files, and make it easy to manage deployments
- Daemonset is a way of ensuring each node will run an instance of a pod. Used for cluster services, like health monitoring and log forwarding
- StatefulSet is tailored to managing pods that must persist or maintain state
- Job and CronJob run short-lived jobs as a one-off or on a schedule.



# Node pools
- You create node pools to group nodes in your AKS cluster. When you create a node pool, you specify the VM size and OS type (Linux or Windows) for each node in the node pool based on application requirement. To host user application pods, node pool Mode should be User otherwise System.

- By default, an AKS cluster will have a Linux node pool (System Mode) whether it's created through Azure portal or CLI. However, you'll always have an option to add Windows node pools along with default Linux node pools during the creation wizard in the portal, via CLI, or in ARM templates.

- Node pools use Virtual Machine Scale Sets as the underlying infrastructure to allow the cluster to scale the number of nodes in a node pool. New nodes created in the node pool will always be the same size as you specified when you created the node pool. 


# Kubernetes Networking

- Pod-to-Pod Communication within the Same Node: 
  When multiple pods are scheduled on the same node, they can communicate with each other directly using localhost or the loopback interface. This communication happens through the pod’s assigned IP address within the cluster, typically in the form of a Virtual Ethernet (veth) pair. The communication occurs at the network layer, enabling high-performance and low-latency interactions between pods on the same node.

- Pod-to-Pod Communication across Nodes:
    When pods need to communicate across different nodes in the cluster, Kubernetes employs various networking solutions, such as Container Network Interfaces (CNIs) and software-defined networking (SDN) technologies. These solutions create a virtual network overlay that spans the entire cluster, enabling pod-to-pod communication across nodes. Some popular CNIs include Calico, Flannel, Weave, and Cilium. These networking solutions ensure that the pod’s IP address remains reachable and provides transparent network connectivity regardless of the pod’s location within the cluster.

# Cluster-Internal Communication
    By default, pods within a Kubernetes cluster can communicate with each other using their internal IP addresses. This communication happens over a virtual network overlay provided by the underlying container runtime or network plugin. The internal IP addresses are assigned by the Kubernetes cluster networking solution and are routable only within the cluster.

# DNS-Based Service Discovery
Kubernetes provides a built-in DNS service for service discovery within the cluster. Services act as stable endpoints that abstract the underlying pods. Each service is assigned a DNS name, which resolves to the IP addresses of the pods backing that service. This DNS-based approach allows pods to communicate with each other using the service names rather than directly referencing the individual pod IP addresses.

# Service Load Balancing
When multiple pods are serving the same application, Kubernetes provides built-in load balancing capabilities for distributing traffic across those pods. By creating a service object and associating it with a set of pods, Kubernetes automatically load balances the incoming requests among the available pods. This load balancing mechanism ensures high availability and scalability of the application.

# Network Policies
Kubernetes offers network policies as a means to control traffic flow between pods. Network policies define rules that specify which pods can communicate with each other based on various parameters such as IP addresses, ports, and protocols. By enforcing network policies, you can segment your application’s network traffic and add an additional layer of security.

# External Communication
Pods often need to communicate with resources outside the Kubernetes cluster, such as external services or databases. Kubernetes provides several mechanisms to facilitate this external communication. One approach is to expose a pod or a set of pods using a service of type “LoadBalancer” or “NodePort,” allowing external clients to access the pods. Another option is to use an Ingress controller, which provides a way to route incoming traffic from outside the cluster to the appropriate pods based on defined rules.

# Service Mesh
For advanced networking scenarios, a service mesh can be employed to enhance pod-to-pod communication. A service mesh, such as Istio or Linkerd, sits as a layer on top of the Kubernetes cluster and provides features like traffic management, observability, and security. With a service mesh, you can control and monitor the communication between pods with advanced routing rules, circuit breaking, and distributed tracing.

