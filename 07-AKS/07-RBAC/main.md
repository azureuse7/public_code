# RBAC with Azure AD Integration on AKS

This guide demonstrates how to set up Kubernetes RBAC integrated with Azure Active Directory (AD) groups and users on an AKS cluster.

## Step-01: Create Namespaces

```bash
kubectl create namespace dev
kubectl create namespace qa
```

## Step-02: Deploy Sample Application to Both Namespaces

```bash
kubectl apply -f kube-manifests/01-Sample-Application -n dev
kubectl apply -f kube-manifests/01-Sample-Application -n qa

kubectl get svc -n dev
# http://<public-ip>/app1/index.html

kubectl get svc -n qa
# http://<public-ip>/app1/index.html
```

## Step-03: Create AD Group, Role Assignment, and User for Dev

### Get the AKS Cluster ID

```bash
AKS_CLUSTER_ID=$(az aks show --resource-group aks-rg3 --name aksdemo3 --query id -o tsv)
echo $AKS_CLUSTER_ID
```

### Create an Azure AD Group

```bash
DEV_AKS_GROUP_ID=$(az ad group create --display-name devaksteam --mail-nickname devaksteam --query objectId -o tsv)
echo $DEV_AKS_GROUP_ID
```

### Create a Role Assignment

```bash
az role assignment create --assignee $DEV_AKS_GROUP_ID --role "Azure Kubernetes Service Cluster User Role" --scope $AKS_CLUSTER_ID
```

### Create a Dev User

```bash
DEV_AKS_USER_OBJECT_ID=$(az ad user create --display-name "AKS Dev1" --user-principal-name aksdev1@stacksimplifygmail.onmicrosoft.com --password @AKSDemo123 --query objectId -o tsv)
echo $DEV_AKS_USER_OBJECT_ID
```

### Associate the Dev User with the Dev AKS Group

```bash
az ad group member add --group devaksteam --member-id $DEV_AKS_USER_OBJECT_ID
```

### Get the Object ID for the AD Group `devaksteam`

```bash
az ad group show --group devaksteam --query objectId -o tsv
```

**Sample output:**

```
e6dcdae4-e9ff-4261-81e6-0d08537c4cf8
```

## Step-06: Create Kubernetes RBAC Role and RoleBinding for the Dev Namespace

### Authenticate as AKS Cluster Admin

```bash
az aks get-credentials --resource-group aks-rg3 --name aksdemo3 --admin
```

### Apply Role and RoleBinding Manifests

```bash
kubectl apply -f kube-manifests/02-Roles-and-RoleBindings
```

### Verify Role and RoleBinding

```bash
kubectl get role -n dev
kubectl get rolebinding -n dev
```

## Step-07: Access the Dev Namespace as the `aksdev1` AD User

### Overwrite kubectl Credentials

```bash
az aks get-credentials --resource-group aks-rg3 --name aksdemo3 --overwrite-existing
```

### List Pods in the Dev Namespace

```bash
kubectl get pods -n dev
```

When prompted, authenticate using:
- **URL:** `https://microsoft.com/devicelogin`
- **Code:** (shown in terminal, e.g., `GLUQPEQ2N`)
- **Username:** `aksdev1@stacksimplifygmail.onmicrosoft.com`
- **Password:** `@AKSDemo123`

### List Services from the Dev Namespace

```bash
kubectl get svc -n dev
```

### List Services from the QA Namespace (Expect a Forbidden Error)

```bash
kubectl get svc -n qa
```

Expected output:

```
Error from server (Forbidden): services is forbidden: User "aksdev1@stacksimplifygmail.onmicrosoft.com" cannot list resource "services" in API group "" in the namespace "qa"
```

This confirms that the RBAC policy is working — the dev user can only access the `dev` namespace.
