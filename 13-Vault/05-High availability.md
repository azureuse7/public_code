# High Availability

This document covers setting up a highly available HashiCorp Vault deployment on a Kubernetes cluster.

## Setup Steps

- Create an AKS cluster with three nodes.
- Access the cluster.
- Clone the repo and `cd` into it.
- Review the values file: `cat ./values` — this file contains all the configuration values.

## Install Vault with Helm

```bash
helm install vault1 . --version 0.20.0 -n testvault
```

Check that the pods are running:

```bash
kubectl get po -n testvault
```

## How to Unseal Multiple Cluster Nodes

When running Vault in HA mode, each node must be individually unsealed after deployment or restart.

Log in to each pod:

```bash
kubectl exec -it <pod-name> -n testvault -- /bin/sh
```

## Note on New Installations

When doing a new installation, delete any existing PersistentVolumes (PV) and PersistentVolumeClaims (PVC) to avoid conflicts with leftover data:

```bash
kubectl delete pvc --all -n testvault
kubectl delete pv --all
```
