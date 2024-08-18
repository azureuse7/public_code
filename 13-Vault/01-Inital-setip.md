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

#### Login to the vault pod 
```
Kubectl exec -it vault5-0 /bin/sh
```
####  Notice its sealed
```
vault status  
```
####  Init the pod
```
vault operator init  
```
####  Copy the keys and token

####  Use the keys to unseal
```
vault operator unseal 
```
####  copy the keys and Repeat three times and Notice it would say sealed false 
####  Copy The Ip and test 


/ $ vault operator init
Unseal Key 1: 6SkvFikbcTdKiAee7HgdiCqjUcs8A4DBwczqW0QgcRTE
Unseal Key 2: MI6GzlPOYwJ20BpmPx1fhAQXR5Z3OBFjhnG34KZ2FqTU
Unseal Key 3: HerV9Ncdnv3XGOF0wMRXft1yWq0yeW7M37mGU3NLbKHg
Unseal Key 4: 6M9Q4HFK4GyIkrK/1wwviTns7VqycuXvrSh8xmavEric
Unseal Key 5: 7vZ8o1Qeb0L886tv0YlAV11d2EjkWb+sy4Qrz1G1gYNU

Initial Root Token: hvs.mK3lRHFHStyKCyPKgwEjkddV