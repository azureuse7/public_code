# High availability

- Create a AKS cluster with three nodes 
- access the cluster 

Clone the repo and cd into it 

cat ./values  → we have all the values 
```t
helm install vault1 . --version 0.20.0 -n testvault

 k get po -n testvault

 How to seal multiple cluster 

Login into one 

k exec 

When doing new installation delete pv pvc 
``` 