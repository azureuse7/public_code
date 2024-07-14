# Kubernetes Service Account

## Introduction

Kubernetes exposes a REST API to manage its objects like pods, deployments, services, secrets, ingress, etc.
It uses the RBAC model to create and assign roles to users, groups and service accounts.

<img src="images/architecture.png"/>



## 1. Creating role to only get/list pods

Create namespace for testing

```powershell
kubectl create namespace my-namespace
```

Create role for pod reader

```powershell
kubectl create role sa-pod-reader-role --verb=get --verb=list --verb=watch --resource=pods --namespace my-namespace -o yaml --dry-run=client > sa-pod-reader-role.yaml

cat sa-pod-reader-role.yaml
# apiVersion: rbac.authorization.k8s.io/v1
# kind: Role
# metadata:
#   name: sa-pod-reader-role
#   namespace: my-namespace
# rules:
# - apiGroups:
#   - ""
#   resources:
#   - pods
#   verbs:
#   - get
#   - list
#   - watch

kubectl apply -f sa-pod-reader-role.yaml
# role.rbac.authorization.k8s.io/sa-pod-reader-role created
```

## 2. Creating Service Account

```powershell
kubectl create serviceaccount my-service-account --namespace my-namespace -o yaml --dry-run=client > my-service-account.yaml

cat my-service-account.yaml
# apiVersion: v1
# kind: ServiceAccount
# metadata:
#   name: my-service-account

kubectl apply -f my-service-account.yaml
# serviceaccount/my-service-account created

kubectl get serviceaccount -n my-namespace
# NAME                 SECRETS   AGE
# default              0         11m
# my-service-account   0         23s
```

## 3. Assign role to service account using rolebinding object

```powershell
kubectl create rolebinding sa-pod-reader-binding --role=sa-pod-reader-role --serviceaccount=my-namespace:my-service-account --namespace my-namespace -o yaml --dry-run=client > sa-pod-reader-binding.yaml

cat sa-pod-reader-binding.yaml
# apiVersion: rbac.authorization.k8s.io/v1
# kind: RoleBinding
# metadata:
#   name: sa-pod-reader-binding
#   namespace: my-namespace
# roleRef:
#   apiGroup: rbac.authorization.k8s.io
#   kind: Role
#   name: pod-reader-role
# subjects:
# - kind: ServiceAccount
#   name: my-service-account
#   namespace: my-namespace

kubectl apply -f sa-pod-reader-binding.yaml
# rolebinding.rbac.authorization.k8s.io/sa-pod-reader-binding created
```

## 5. Verifying access to API Server resources using impersonation

Verify with all satisfied constraints: service account, namespace, resource, action

```powershell
kubectl auth can-i get pods --namespace my-namespace --as system:serviceaccount:my-namespace:my-service-account
# yes

kubectl create deployment nginx --image=nginx -n my-namespace --replicas=2 # as myself
# deployment.apps/nginx created

kubectl get pods --namespace my-namespace --as system:serviceaccount:my-namespace:my-service-account
# NAME                    READY   STATUS    RESTARTS   AGE
# nginx-76d6c9b8c-6jwrn   1/1     Running   0          21s
# nginx-76d6c9b8c-cfrfw   1/1     Running   0          21s
```

Verify with not allowed namespace

```powershell
kubectl auth can-i get pods --namespace default --as system:serviceaccount:my-namespace:my-service-account
# no
```

Verify with not allowed resource

```powershell
kubectl get secrets --namespace my-namespace --as system:serviceaccount:my-namespace:my-service-account
# Error from server (Forbidden): secrets is forbidden: User "system:serviceaccount:my-namespace:my-service-account" cannot list resource "secrets" in API group "" in the namespace "default"
```

## 6. Accessing the API Server REST API from a Pod

Assign the Service Account to Deployment; add: serviceAccountName: my-service-account

```powershell
kubectl create deployment nginx-sa --image=nginx --replicas=2 -n my-namespace --dry-run=client -o yaml > deployment.yaml

cat deployment.yaml
# apiVersion: apps/v1
# kind: Deployment
# metadata:
#   labels:
#     app: nginx-sa
#   name: nginx-sa
#   namespace: my-namespace
# spec:
#   replicas: 2
#   selector:
#     matchLabels:
#       app: nginx-sa
#   template:
#     metadata:
#       labels:
#         app: nginx-sa
#     spec:
#       serviceAccountName: my-service-account
#       containers:
#       - image: nginx
#         name: nginx

kubectl apply -f deployment.yaml
# deployment.apps/nginx-sa created

kubectl get pods -n my-namespace
# NAME                        READY   STATUS    RESTARTS   AGE
# nginx-76d6c9b8c-6jwrn       1/1     Running   0          9m15s
# nginx-76d6c9b8c-cfrfw       1/1     Running   0          9m15s
# nginx-sa-8595cf7d74-9pxfp   1/1     Running   0          49s
# nginx-sa-8595cf7d74-xckmk   1/1     Running   0          49s
```

Get the pods using '-v 6' to show the REST API endpoint

```powershell
kubectl get pods -n my-namespace -v 6
# I0102 14:00:00.646208   18948 loader.go:373] Config loaded from file:  C:\Users\hodellai\.kube\config
# I0102 14:00:00.777184   18948 round_trippers.go:553] GET https://aks-cluste-rg-aks-serviceac-82f6d7-886ac5f4.hcp.westeurope.azmk8s.io:443/api/v1/namespaces/my-namespace/pods?limit=500 200 OK in 94 milliseconds
# NAME                        READY   STATUS    RESTARTS   AGE
# nginx-76d6c9b8c-6jwrn       1/1     Running   0          9m17s
# nginx-76d6c9b8c-cfrfw       1/1     Running   0          9m17s
# nginx-sa-8595cf7d74-9pxfp   1/1     Running   0          51s
# nginx-sa-8595cf7d74-xckmk   1/1     Running   0          51s
```

Get a pod that uses my-service-account and exec into it

```powershell
$POD_NAME=$(kubectl get pods -l app=nginx-sa -n my-namespace -o jsonpath='{.items[0].metadata.name}')
echo $POD_NAME
# nginx-sa-8595cf7d74-9pxfp

kubectl exec -it $POD_NAME -n my-namespace -- bash
# root@nginx-sa-8595cf7d74-9pxfp:/#
```

From inside this pod, we want to access the REST API to retrieve Pods in the namespace my-namespace

Run the following commands inside the pod shell

```powershell
# root@nginx-sa-8595cf7d74-9pxfp:/#
# Path to ServiceAccount token
ls /var/run/secrets/kubernetes.io/serviceaccount
# ca.crt  namespace  token

# Read this Pod's namespace
NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
echo $NAMESPACE
# my-namespace

# Read the ServiceAccount bearer token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
echo $TOKEN
# eyJhbGciOiJSUzI1NiIsImtpZCI6InFCVUNMNVBvNjF3S3pnbVJmV1dyN2ppby00ZXplV1l0WjJxbnlaWXJzeHcifQ.
# eyJhdWQiOlsiaHR0cHM6Ly9ha3MtY2x1c3RlLXJnLWFrcy1zZXJ2aWNlYWMtODJmNmQ3LTg4NmFjNWY0LmhjcC53ZXN
# 0ZXVyb3BlLmF6bWs4cy5pbyIsIlwiYWtzLWNsdXN0ZS1yZy1ha3Mtc2VydmljZWFjLTgyZjZkNy04ODZhYzVmNC5oY3
# ...

# Reference the internal certificate authority (CA)
CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
cat $CACERT
# -----BEGIN CERTIFICATE-----
# MIIE6TCCAtGgAwIBAgIRAJUcpg7ynio1WdNBogeik7UwDQYJKoZIhvcNAQELBQAw
# DTELMAkGA1UEAxMCY2EwIBcNMjMwMTAyMDcwNTI3WhgPMjA1MzAxMDIwNzE1Mjda
# ...
# keTSrxyM9+/0YFvlvw==
# -----END CERTIFICATE-----

# Explore the API with TOKEN
curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET https://kubernetes.default.svc/api
# {
#     "kind": "APIVersions",
#     "versions": [
#       "v1"
#     ],
#     "serverAddressByClientCIDRs": [
#       {
#         "clientCIDR": "0.0.0.0/0",
#         "serverAddress": "aks-cluste-rg-aks-serviceac-82f6d7-886ac5f4.hcp.westeurope.azmk8s.io:443"
#       }
#     ]
# }

# Get the pods from API Server REST endpoint 
curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET https://kubernetes.default.svc/api/v1/namespaces/my-namespace/pods
# {
#     "kind": "PodList",
#     "apiVersion": "v1",
#     "metadata": {
#       "resourceVersion": "85783",
#       "continue": "eyJ2IjoibWV0YS5rOHMuaW8vdjEiLCJydiI6ODU3ODMsInN0YXJ0IjoibmdpbngtNzZkNmM5YjhjLTZqd3JuXHUwMDAwIn0",
#       "remainingItemCount": 3
#     },
#     "items": [
#       {
#         "metadata": {
#           "name": "nginx-76d6c9b8c-6jwrn",
#           "generateName": "nginx-76d6c9b8c-",
#           "namespace": "my-namespace",
#           "uid": "4c91aa88-26c5-4463-874f-d9453ad4ba5a",
#           "resourceVersion": "77577",
#           "creationTimestamp": "2023-01-02T12:50:42Z",
#           "labels": {
#             "app": "nginx",
#             "pod-template-hash": "76d6c9b8c"
#           },
# ...
```

=====================================================

- In Kubernetes, a **Service Account** provides an identity for processes that run in a Pod. When you (a human) interact with Kubernetes, you typically use a user account. Similarly, processes in containers inside pods can also contact the Kubernetes API and they authenticate with the API server as a service account.

##### Why Use Service Accounts?
Service accounts are used to provide specific identities to applications running in your pods, separate from user accounts. This is useful for several reasons:

1) **Scoped Permissions**: Each service account can have specific permissions governing what actions it can and cannot perform on the Kubernetes API, defined through roles and role bindings. This follows the principle of least privilege, limiting access rights for pod applications to the minimum necessary to perform their job.

2) **Automatic API Token Mounting:** Kubernetes automatically mounts service account tokens in the pods using that service account, facilitating secure communication with the Kubernetes API without manual token management.

3) **Default Accounts**: Kubernetes automatically creates a default service account in each namespace. If a pod does not explicitly specify a service account, it is assigned the default service account in its namespace.

##### Creating a Service Account
- You can create a service account using a YAML file or via the kubectl command. Here's how to do it using kubectl:

```
kubectl create serviceaccount my-service-account
```
- This command creates a new service account named my-service-account in the current namespace.

##### Using a Service Account with a Pod
- To use a specific service account in a pod, specify the service account name in the pod's YAML definition:

```
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account
  containers:
  - name: my-container
    image: my-image
```
##### Assigning Permissions to a Service Account
Permissions are assigned to service accounts through **Roles** and **RoleBindings** (or ClusterRoles and ClusterRoleBindings for cluster-wide permissions):

1)**Role**: Defines permissions to perform certain sets of actions on a set of resources within a namespace.

2)**RoleBinding**: Grants the permissions defined in a Role to a user, group, or service account in the same namespace.

- Here’s an example of creating a role and a role binding for a service account:

Role YAML Definition (role.yaml):
```
yaml
Copy code
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
RoleBinding YAML Definition (rolebinding.yaml):
```
```
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
 ``` 
Apply these with kubectl:

```
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml
```
##### These configurations allow the my-service-account to perform "get", "watch", and "list" actions on pods within the "default" namespace.

- Best Practices
Do not use the default service account unnecessarily, as it can have broader permissions than required for your applications.
- Regularly review and tighten permissions for service accounts to ensure they only have access necessary for their function.
- Service accounts are a fundamental aspect of security in Kubernetes, helping to manage and restrict how internal processes interact with the Kubernetes API.