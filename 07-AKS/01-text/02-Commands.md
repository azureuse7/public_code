### Configure Cluster Creds (kube config) for Azure AKS Clusters →
```t
az aks get-credentials --resource-group aks-rg1 --name aksdemo1 --overwrite-existing && kubelogin convert-kubeconfig
```
### Node Status →

```t
kubectl get nodes/   -o wide
```

### List Pods → 
```t                                          
kubectl get pods/ po  -n <namespace> / -o wide
```

### Describe the pod →  
```t                       
Kubectl describe pod <pod name> -n <namespace>
```
### Delete Pod →  
```t                                   
kubectl delete pod <Pod name> -n <namespace>
```
### Create a Pod →   
```t                               
kubectl run <desired-pod-name> --image <Container-Image> 
```
### Get Pods from Namespace → 
```t       
kubectl get pods -n <namespace> (kubectl get namespace/ns)
```
### Logs→   
```t                                                
k logs <pod-name> -n <namespace>
```
### Stream pod logs with -f-->      
```t        
k logs -f <pod-name>
```
# Services 

### Service Info →      
```t                                  
kubectl get service  -n <namespace>  /svc.    /-o wide
```
### Delete Service->   
```t                           
delete svc <YourServiceName>
```
### Verify if Service got deleted →     
```t   
kubectl get svc.   -n <namespace>
```
 
# Replicaset 

### Replicaset Info →       
```t                             
kubectl get replicaset /  rs
```
### Describe  ReplicaSet-> 
```t                     
kubectl describe rs/<replicaset-name>
```
### Delete ReplicaSet->    
```                         
kubectl delete rs <ReplicaSet-Name>
```

### Verify if ReplicaSet got deleted-> 
```   
kubectl get rs
``` 
# Namespace

### Namespace Info →    
```                                 
kubectl get namespace 
``` 
### Get all Objects in  namespace-->   
```      
kubectl get all. 
kubectl get all --namespace <external-dns>
``` 
### Create name space →     
```                        
kubectl create ns <name space>
``` 
# Deployment 

### Deployments->  
```                                     
kubectl get deployments --all-namespaces
``` 
###  Delete →   
```                                                     
kubectl delete -n NAMESPACE deployment DEPLOYMENT
``` 

### NetworkPolicies-->  
```                              
k get NetworkPolicies -n gatekeeper-system
k edit NetworkPolicies -n gatekeeper-system
k apply -f <file> -n <namespace>
``` 

###  rolebindings
``` 
kubectl get rolebindings,clusterrolebindings \
--all-namespaces  \
-o custom-columns='KIND:kind,NAMESPACE:metadata.namespace,NAME:metadata.name,SERVICE_ACCOUNTS:subjects[?(@.kind=="ServiceAccount")].name
``` 
``` 
kubectl get clusterroles
kubectl get clusterrolebindings
``` 
#### find your role name and then delete
``` 
kubectl delete clusterrolebinding name
kubectl delete clusterrole name
``` 

###  log into pod gagan
``` 
k  exec -it <pod> /bin/sh
``` 
### list the taints
```t
kubectl get nodes -o json | jq '.items[].spec'
kubectl get nodes -o json | jq '.items[].spec.taints'
```