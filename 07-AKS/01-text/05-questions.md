Unable to connect to the server: dial tcp: lookup <Server Location>: no such host

az aks command invoke \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --command "kubectl get pods -n kube-system"

az aks command invoke \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --command "kubectl apply -f deployment.yaml -n default" \
  --file deployment.yaml

https://learn.microsoft.com/en-gb/azure/aks/access-private-cluster?tabs=azure-cli

  
=========

