# Kubernetes Persistent Volumes, Claims, and Storage Classes

Kubernetes provides a rich storage model to support stateful applications. This document covers the core concepts: Volumes, PersistentVolumes, PersistentVolumeClaims, and StorageClasses.

## Volumes

Kubernetes uses the concept of volumes. At its core, a volume is a directory — possibly containing data — that is accessible to a pod. How that directory is created, the medium that backs it, and its contents are determined by the volume type used.

Kubernetes supports many storage types that can be mixed and matched within a pod. Storage in a pod can be consumed by any container in that pod. Storage survives pod restarts, but what happens after pod deletion depends on the specific storage type.

Common options for mounting file and block storage into a pod include:

- Public cloud storage services such as AWS EBS and `gcePersistentDisk`
- Infrastructure-backed types such as CephFS, Fibre Channel, iSCSI, NFS, and GlusterFS
- Special types such as `configMap` and `Secrets` (used for injecting Kubernetes-stored data into a pod) and `emptyDir` (used as scratch space)

## PersistentVolumes (PVs)

PersistentVolumes tie into an existing storage resource and are generally provisioned by an administrator. They are cluster-wide objects linked to the backing storage provider that make these resources available for consumption by pods.

## PersistentVolumeClaims (PVCs)

For each pod, a PersistentVolumeClaim makes a storage consumption request within a namespace. Depending on the current usage of the PV, it can have different phases or states:

- **Available** — not yet bound to a claim
- **Bound** — claimed and unavailable to others
- **Released** — the claim has been deleted, but the resource has not yet been reclaimed
- **Failed** — Kubernetes could not automatically reclaim the PV

## StorageClasses

StorageClasses are an abstraction layer used to differentiate the quality and characteristics of underlying storage (for example, performance tiers). They are similar to labels: operators use them to describe different types of storage so that storage can be dynamically provisioned based on incoming claims from pods.

StorageClasses are used in conjunction with PersistentVolumeClaims, which is how pods dynamically request new storage. This type of dynamic storage allocation is common where storage is offered as a service, such as with public cloud providers or storage systems like Ceph.
