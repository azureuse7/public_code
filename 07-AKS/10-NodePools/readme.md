Kubernetes Nodepools Explained

Tutorial available here:
https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/kubernetes-nodepools-explained/ba-p/2531581


- In a Kubernetes cluster, the containers are deployed as pods into VMs called worker nodes.

- These nodes are identical as they use the same VM size or SKU.

- This was just fine until we realized we might need nodes with different SKU for the following reasons:

 
Prefer to deploy Kubernetes system pods (like CoreDNS, metrics-server, Gatekeeper addon) and application pods on different dedicated nodes. 

This is to prevent misconfigured or rogue application pods to accidentally killing system pods.
Some pods requires either CPU or Memory intensive and optimized VMs.

Some pods/jobs want to leverage spot/preemptible VMs to reduce the cost.
Some pods running legacy Windows applications requires Windows Containers available with Windows VMs.
Some teams want to physically isolate their non-production environments (dev, test, QA, staging, etc.) within the same cluster. This is because it is relatively easier to manage less clusters.

These teams realized that logical isolation with namespaces is not enough. These reasons led to the creation of heterogeneous nodes within the cluster. To make it easier to manage these nodes, Kubernetes introduced the Nodepool. The nodepool is a group of nodes that share the same configuration (CPU, Memory, Networking, OS, maximum number of pods, etc.). By default, one single (system) nodepool is created within the cluster. However, we can add nodepools during or after cluster creation. We can also remove these nodepools at any time. There are 2 types of nodepools:

 

1. System nodepool: used to preferably deploy system pods. Kubernetes could have multiple system nodepools. At least one nodepool is required with at least one single node. System nodepools must run only on Linux due to the dependency to Linux components (no support for Windows).

2. User nodepool: used to preferably deploy application pods. Kubernetes could have multiple user nodepools or none. All user nodepools could scale down to zero nodes. A user nodepool could run on Linux or Windows nodes.

 

Nodepool might have some 'small' different configurations with different cloud providers. This article will focus on Azure Kubernetes Service (AKS). Let's see a demo on how that works with AKS.