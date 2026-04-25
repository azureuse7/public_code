# Create and connect to AKS cluster
az group create --name "rg-aks-storage-blob" --location westeurope

az aks create --name "gagan-aks" --resource-group "rg-aks-storage-blob" --node-count 3 --zones 1 2 3 --kubernetes-version "1.25.2" --network-plugin azure  --enable-blob-driver

az aks get-credentials -n "gagan-aks" -g "rg-aks-storage-blob" --overwrite-existing


