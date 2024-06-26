There may be times when the nginx ingress external IP (load balancer) is needed while configuring deployments. Below is example code showing how to retrieve it using a terraform data call:


data "kubernetes_service" "example" {
  metadata {
    name = "ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
}

output "test" {
  value = data.kubernetes_service.example.status[0].load_balancer[0].ingress[0].ip
}

# Ingress - Basics

### Ingress Basic Architecture
[![Image](https://www.stacksimplify.com/course-images/azure-aks-ingress-basic.png "Azure AKS Kubernetes - Masterclass")](https://www.udemy.com/course/aws-eks-kubernetes-masterclass-devops-microservices/?referralCode=257C9AD5B5AF8D12D1E1)


## Step-02: Create Static Public IP
```t
# Get the resource group name of the AKS cluster 
az aks show --resource-group aks-rg1 --name aksdemo1 --query nodeResourceGroup -o tsv

# TEMPLATE - Create a public IP address with the static allocation
az network public-ip create --resource-group <REPLACE-OUTPUT-RG-FROM-PREVIOUS-COMMAND> --name myAKSPublicIPForIngress --sku Standard --allocation-method static --query publicIp.ipAddress -o tsv

# REPLACE - Create Public IP: Replace Resource Group value
az network public-ip create --resource-group MC_aks-rg1_aksdemo1_centralus --name myAKSPublicIPForIngress --sku Standard --allocation-method static --query publicIp.ipAddress -o tsv
```
- Make a note of Static IP which we will use in next step when installing Ingress Controller
```t
# Make a note of Public IP created for Ingress
52.154.156.139
```

## Step-03: Install Ingress Controller
```t
# Install Helm3 (if not installed)
brew install helm

# Create a namespace for your ingress resources
kubectl create namespace ingress-basic

# Add the official stable repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

#  Customizing the Chart Before Installing. 
helm show values ingress-nginx/ingress-nginx

# Use Helm to deploy an NGINX ingress controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-basic \
    --set controller.replicaCount=2 \
    --set controller.nodeSelector."kubernetes\.io/os"=linux \
    --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux \
    --set controller.service.externalTrafficPolicy=Local \
    --set controller.service.loadBalancerIP="REPLACE_STATIC_IP" 

# Replace Static IP captured in Step-02 (without beta for NodeSelectors)
helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-basic \
    --set controller.replicaCount=2 \
    --set controller.nodeSelector."kubernetes\.io/os"=linux \
    --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux \
    --set controller.service.externalTrafficPolicy=Local \
    --set controller.service.loadBalancerIP="52.154.156.139"     


# List Services with labels
kubectl get service -l app.kubernetes.io/name=ingress-nginx --namespace ingress-basic

# List Pods
kubectl get pods -n ingress-basic
kubectl get all -n ingress-basic


# Access Public IP
http://<Public-IP-created-for-Ingress>

# Output should be
404 Not Found from Nginx

# Verify Load Balancer on Azure Mgmt Console
Primarily refer Settings -> Frontend IP Configuration
```

## Step-05: Deploy Application k8s manifests and verify
```t
# Deploy
kubectl apply -f kube-manifests/

# List Pods
kubectl get pods

# List Services
kubectl get svc

# List Ingress
kubectl get ingress

# Access Application
http://<Public-IP-created-for-Ingress>/app1/index.html
http://<Public-IP-created-for-Ingress>

# Verify Ingress Controller Logs
kubectl get pods -n ingress-basic
kubectl logs -f <pod-name> -n ingress-basic
```

## Step-06: Clean-Up Apps
```t
# Delete Apps
kubectl delete -f kube-manifests/
```

Ingress:

So generally we have the below setup: 

<img src="images/1.png">



One is fine but what if we had more examples:
<img src="images/2.png">


This is not good. we can use Ingress
<img src="images/3.png">

<img src="images/4.png">

So how does it tie up:
<img src="images/5.png">


Deployment--> Label      → app -> app1-nginx 

Service.       --> Selector--> app → app1-nginx

Ingress: 

- Annotation:

- path:

- Service: Its tells which service to use i.e. app1-nginx-clusterip-service

So in short Ingress tell:

what my path here,  its /

Route  to service, here the service is  app1-nginx-clusterip-service

The service knows which deployment to go to:  here its app1-nginx 

We define an ingress rule that forwards the request based on one name and DNS maps name with IP 

This is how the Service will know where to forward the request to which pod

Now the question comes if  a Pod has two containers how does it know which port to forward 

<img src="images/6.png">



This is done using the Target port as below

<img src="images/7.png">



It will look at label and then the target port example 3000 here

As below:

path / goes to -->

path /track-joker goes to →

<img src="images/8.png">
<img src="images/9.png">