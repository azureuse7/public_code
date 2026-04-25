# Azure AKS - Cluster Autoscaler


- The Kubernetes Cluster Autoscaler automatically adjusts the number of nodes in your cluster when pods fail to launch due to lack of resources.

This excerise we will deploy a application and set cpu 250m then scale up the pods to 20, (change the repliac to 20)
now depending on the node we have (B1, D1,) that many pods will be created and then it will spin up more nodes so 20 pods can be created. 

- Horizontal would increase number of pods.

[![Image](https://stacksimplify.com/course-images/azure-kubernetes-service-autoscaling-ca.png "Azure AKS Kubernetes - Masterclass")](https://stacksimplify.com/course-images/azure-kubernetes-service-autoscaling-ca.png)


## Step-02: Create Cluster with Cluster Autoscaler Enabled
```
# Setup Environment Variables
export RESOURCE_GROUP=aks-rg1-autoscaling
export REGION=centralus
export AKS_CLUSTER=aks-autoscaling-demo
echo $RESOURCE_GROUP, $REGION, $AKS_CLUSTER

# Create Resource Group
az group create --location ${REGION} \
                --name ${RESOURCE_GROUP}

# Create AKS cluster and enable the cluster autoscaler
az aks create --resource-group ${RESOURCE_GROUP} \
              --name ${AKS_CLUSTER} \
              --enable-managed-identity \
              --generate-ssh-keys \
              --node-count 1 \
              --enable-cluster-autoscaler \
              --min-count 1 \
              --max-count 5 

# Configure Credentials
az aks get-credentials --name ${AKS_CLUSTER}  --resource-group ${RESOURCE_GROUP} 

# List Nodes
kubectl get nodes
kubectl get nodes -o wide

# Cluster Info
kubectl cluster-info

# kubectl Config Current Context
kubectl config current-context
```

## Step-03: Compare & Observe aksdemo2 and aks-autoscaling-demo cluster nodepools
### Cluster: aksdemo2
- Go to All Services -> Kubernetes Services -> aksdemo2 -> Settings -> Nodepools 
- Select Scale
- Compare the setting with aks-autoscaling-demo cluster
- Scale Method: Manual (Observe the setting)
- We can even enable autoscaling from here on Portal Management console 
### Cluster: aks-autoscaling-demo
- Go to All Services -> Kubernetes Services -> aksdemo2 -> Settings -> Nodepools 
- Select Scale
- Scale Method: Automatic (Nothing but --enable-cluster-autoscaler)
- Node Count Rage: 1 to 5 (Nothing but what we defined in Min and Max)
- Current Node Count: 1 (Nothing but what we defined in Node Count)

## Step-04: Review & Deploy Sample Application
```
# Deploy Application
kubectl apply -f kube-manifests/

# List Pods
kubectl get pods

# Access Application
kubectl get svc
http://<PublicIP-from-get-svc-output>/hello
curl -w "\n" http://52.154.217.196/hello
```

## Step-05: Scale our application to 20 pods
- In 2 to 3 minutes, one after the other new nodes will added and pods will be scheduled on them. 
- Our max number of nodes will be 5 which we provided during cluster creation.
```
# Scale UP the demo application to 20 pods
kubectl get pods
kubectl get nodes 
kubectl scale --replicas=20 deploy cluster-autoscaler-demoapp-deployment
kubectl get pods

# Verify nodes
kubectl get nodes -o wide

# Access Application
kubectl get svc
http://<PublicIP-from-get-svc-output>/hello
curl -w "\n" http://52.154.217.196/hello
```
## Step-06: Cluster Scale DOWN: Scale our application to 1 pod
- It might take 5 to 20 minutes to cool down and come down to minimum nodes which will be 2 which we configured during nodegroup creation
```
# Scale down the demo application to 1 pod
kubectl scale --replicas=1 deploy cluster-autoscaler-demoapp-deployment

# Verify nodes
kubectl get nodes -o wide
```

## Step-07: Clean-Up 
- We will leave cluster autoscaler and undeploy only application
```
# Delete Apps
kubectl delete -f kube-manifests/

```


## References
- [Azure AKS Cluster Autoscaler](https://docs.microsoft.com/en-us/azure/aks/cluster-autoscaler)