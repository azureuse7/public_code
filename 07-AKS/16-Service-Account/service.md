# When you create any type of resource in Kubernetes, the resource is deployed with a service account inside of Kubernetes.


# What’s A Service Account?
A service account is how workloads in Kubernetes run. It contains RBAC permissions that give it the ability to deploy resources to a Kubernetes cluster. Service accounts are used to connect to the Kubernetes API server.

Service accounts can also give you the ability to connect to other services, for example, workloads running in GCP that a Kubernetes cluster may need access to. For example, a service account that can act as an IAM service account inside of GCP using Workload Identity.

# Why Create A Service Account?
By default, when you create a Pod, the default Kubernetes service account is used.

Let’s say you have a Pod running, you can run the following command and see the spec.ServiceAccountName field.
kubectl get pods -o yaml
Since there’s already a service account being used, you may be asking yourself why do I need to manually create a service account if it already exists? of which there’s one big reason - security.

The biggest reason is from a security perspective. If you’re using the same service account over and over again and that service account gets compromised, all of your applications are in big trouble. If a malicious entity obtains access to the default service account that’s deploying every workload inside of Kubernetes, that means it’ll ultimately have access to every Pod that’s running in the cluster. It’ll also allow any compromised Pod to run API calls against the cluster.

Another reason, although not as important as the security piece, is the cleanliness of the environment. Think about it like this - imagine every Sysadmin used the same email account for every single service that the infrastructure department uses or a developer generating and using the same API key for authentication across all applications. Not only is it a bad security practice, but it’s not a good practice in general.

# Creating A Service Account
Now that you know why you want to use a different service account other than the Kubernetes default, let’s learn how to set it up.

For the purposes of this blog post, you’ll create a service account that’s tied to a specific namespace.

First, you’ll need to create a namespace. The example below shows a namespace called levantest that you can create.

Save the Kubernetes Manifest namespace code below as namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: levantest
Create the namespace:
kubectl apply -f namespace.yaml
Next, you need to create the service account and give it certain permissions. You’ll need to create:

The service account
A Role for the service account
A RoleBinding to bind the Role so you can use it on the service account
The below YAML creates a service account called app1serviceaccount, gives it permissions to create, get, watch, and list, and binds it to the levantest namespace.

Save the Kubernetes Manifest below and call it serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app1serviceaccount
  namespace: levantest
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: levantest
  name: pod-creator
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-creator
  namespace: levantest
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-creator
subjects:
- kind: ServiceAccount
  name: app1serviceaccount
  namespace: levantest
Run the following command to create the resource:
kubectl apply -f serviceaccount.yaml
You should see an output similar to the screenshot below.

Image description

Next, let’s use the service account to create a Pod.

Using A Service Account
Now it’s time to create a Pod with the service account that you created.

The Kubernetes Manifest below creates a Pod resource that deploys a Pod running Nginx with no high-level controller (Deployment, DaemonSet, etc.) and utilizes the newly created service account.

Save the Kubernetes Manifest as pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginxpod
  namespace: levantest
spec:
  containers:
  - image: nginx:latest
    name: nginxpod
  serviceAccountName: app1serviceaccount
Run the following command to deploy the Pod.
kubectl apply -f pod.yaml
Once running, you can see the output of the Pod to confirm it’s using the appropriate service account.
kubectl get pods -n namespace_name -o yaml
You should see an output similar to the screenshot below, which under spec will show the service account.

Image description

Congrats! You have successfully created and used a new service account for Pod deployments

<!-- https://travis.media/kubernetes-service-accounts-complete-guide-for-beginners/ -->