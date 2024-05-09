### Create a Pod
- Create a Pod
```
# Template
kubectl run <desired-pod-name> --image <Container-Image> 

# Replace Pod Name, Container Image
kubectl run my-first-pod --image stacksimplify/kubenginx:1.0.0
```  

### List Pods
- Get the list of pods
```
# List Pods
kubectl get pods

# Alias name for pods is po
kubectl get po
```

### List Pods with wide option
- List pods with wide option which also provide Node information on which Pod is running
```
kubectl get pods -o wide
```

# To get list of pod names
kubectl get pods

# Describe the Pod
kubectl describe pod <Pod-Name>
kubectl describe pod my-first-pod 
```

### Access Application
- Currently we can access this application only inside worker nodes. 
- To access it externally, we need to create a **NodePort or Load Balancer Service**. 
- **Services** is one very very important concept in Kubernetes. 

### Delete Pod
```
# To get list of pod names
kubectl get pods

# Delete Pod
kubectl delete pod <Pod-Name>
kubectl delete pod my-first-pod
```


## Step-04: Demo - Expose Pod with a Service
- Expose pod with a service (Load Balancer Service) to access the application externally (from internet)
- **Ports**
  - **port:** Port on which node port service listens in Kubernetes cluster internally
  - **targetPort:** We define container port here on which our application is running.
- Verify the following before LB Service creation
  - Azure Standard Load Balancer created for Azure AKS Cluster
    - Frontend IP Configuration
    - Load Balancing Rules
  - Azure Public IP 
```
# Create  a Pod
kubectl run <desired-pod-name> --image <Container-Image> 
kubectl run my-first-pod --image stacksimplify/kubenginx:1.0.0 

# Expose Pod as a Service
kubectl expose pod <Pod-Name>  --type=LoadBalancer --port=80 --name=<Service-Name>
kubectl expose pod my-first-pod  --type=LoadBalancer --port=80 --name=my-first-service

# Get Service Info
kubectl get service
kubectl get svc

# Describe Service
kubectl describe service my-first-service

# Access Application
http://<External-IP-from-get-service-output>
```
- Verify the following after LB Service creation
  - Azure Standard Load Balancer created for Azure AKS Cluster
    - Frontend IP Configuration
    - Load Balancing Rules
  - Azure Public IP
- View the resources in Azure AKS Cluster - Resources section from Azure Portal Management Console  



## Step-05: Interact with a Pod

### Verify Pod Logs
```
# Get Pod Name
kubectl get po

# Dump Pod logs
kubectl logs <pod-name>
kubectl logs my-first-pod

# Stream pod logs with -f option and access application to see logs
kubectl logs <pod-name>
kubectl logs -f my-first-pod
```
- **Important Notes**
  - Refer below link and search for **Interacting with running Pods** for additional log options
  - Troubleshooting skills are very important. So please go through all logging options available and master them.
  - **Reference:** https://kubernetes.io/docs/reference/kubectl/cheatsheet/

### Connect to Container in a POD
- **Connect to a Container in POD and execute commands**
```
# Connect to Nginx Container in a POD
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it my-first-pod -- /bin/bash

# Execute some commands in Nginx container
ls
cd /usr/share/nginx/html
cat index.html
exit
```

- **Running individual commands in a Container**
```
kubectl exec -it <pod-name> -- env

# Sample Commands
kubectl exec -it my-first-pod -- env
kubectl exec -it my-first-pod -- ls
kubectl exec -it my-first-pod -- cat /usr/share/nginx/html/index.html
```
## Step-06: Get YAML Output of Pod & Service
### Get YAML Output
```
# Get pod definition YAML output
kubectl get pod my-first-pod -o yaml   

# Get service definition YAML output
kubectl get service my-first-service -o yaml   
```

## Step-07: Clean-Up
```
# Get all Objects in default namespace
kubectl get all

# Delete Services
kubectl delete svc my-first-service

# Delete Pod
kubectl delete pod my-first-pod

# Get all Objects in default namespace
kubectl get all
```