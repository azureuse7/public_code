# Custom Resource Definitions (CRDs) in Kubernetes

Reference video: [Custom Resource Definitions in Kubernetes](https://www.youtube.com/watch?v=u1X5Rf7fWwM)

## What is a Resource in Kubernetes?

A resource is an endpoint in the Kubernetes API that stores a collection of API objects. You can list all available resources with:

```bash
kubectl api-resources
```

This is how commands like `kubectl apply` work — they hit a registered API endpoint from this list.

## What is a Custom Resource?

Custom Resources are extensions of the Kubernetes API. They allow you to define your own resource types beyond the built-in ones.

For example, if you try to get a resource that does not exist:

```bash
kubectl get greeting
```

You will receive an error because `greeting` is not a registered API resource.

## What is a Definition?

A definition is a command sent to the API server in the form of a YAML construct. You can view the definition of any existing object with:

```bash
kubectl get pod <pod-name> -o yaml
```

## How CRDs Work in Kubernetes

A Custom Resource Definition (CRD) tells the Kubernetes API server about a new resource type. Once a CRD is registered, you can create, list, and manage custom objects of that type using standard `kubectl` commands — just as you would with built-in resources like pods or deployments.
