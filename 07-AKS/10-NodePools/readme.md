Kubernetes Nodepools Explained

Tutorial available here:
https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/kubernetes-nodepools-explained/ba-p/2531581


- In a Kubernetes cluster, the containers are deployed as pods into VMs called worker nodes.

- These nodes are identical as they use the same VM size or SKU.

- This was just fine until we realized we might need nodes with different SKU for the following reasons:

 
- Prefer to deploy Kubernetes system pods (like CoreDNS, metrics-server, Gatekeeper addon) and application pods on different dedicated nodes. 


 However, we can add nodepools during or after cluster creation. We can also remove these nodepools at any time. There are 2 types of nodepools:

 

##### 1. System nodepool:
   Used to preferably deploy system pods. Kubernetes could have multiple system nodepools. At least one nodepool is required with at least one single node. System nodepools must run only on Linux due to the dependency to Linux components (no support for Windows).

#### 2. User nodepool:
 used to preferably deploy application pods. Kubernetes could have multiple user nodepools or none. All user nodepools could scale down to zero nodes. A user nodepool could run on Linux or Windows nodes.

 

