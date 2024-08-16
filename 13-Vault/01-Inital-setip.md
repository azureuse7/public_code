https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks
https://developer.hashicorp.com/vault/docs?product_intent=vault
## Initial setup 

- Create an AKS cluster and Connect it to the AKS cluster 


#### check helm if it's installed 
```
helm                                                  
```
#### check what charts we have 
```
helm list                                           
```
#### check what repo we have 
```
helm repo list                                     
```
#### Add a repo    
```                                      
helm repo add hashicorp https://helm.release.hasicorp.com
```
#### you can copy the URL and see what its using 

#### list the repo
```
helm repo list                                    
```
#### Updat the repo
```
helm repo update                             
```
#### check all version 
```
helm search repo vault --versions. → all the version  
```
#### Install vault
```
helm install vault5 hashicorp/vault  --set='ui.enabled=true' --set='ui.serviceType=LoadBalancer'
```
#### Check the pods
```
Kubectl get pods
```
#### The the IP of the service
```
Kubectl get service 
```
#### Copy the IP on the browser and add :8200
``` 

