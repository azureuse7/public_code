# AWS Storage Services: S3, EBS, and EFS — Full End-to-End Guide for EKS

---

## Table of Contents

1. [Overview: The Three Storage Services](#1-overview)
2. [Amazon S3 — Simple Storage Service](#2-amazon-s3)
3. [Amazon EBS — Elastic Block Store](#3-amazon-ebs)
4. [Amazon EFS — Elastic File System](#4-amazon-efs)
5. [Comparison Table](#5-comparison-table)
6. [Storage in Kubernetes — Core Concepts](#6-storage-in-kubernetes)
7. [EBS in EKS — Deep Dive](#7-ebs-in-eks)
8. [EFS in EKS — Deep Dive](#8-efs-in-eks)
9. [S3 in EKS — Deep Dive](#9-s3-in-eks)
10. [Are They Required for EKS?](#10-are-they-required-for-eks)
11. [End-to-End Architecture Walkthrough](#11-end-to-end-architecture)
12. [Security Considerations](#12-security-considerations)
13. [Summary & Decision Tree](#13-summary--decision-tree)

---

## 1. Overview

AWS provides three primary storage services that are commonly used with EKS:

| Service | Type | Access Pattern | Analogy |
|---|---|---|---|
| **S3** | Object Storage | HTTP API (any number of clients) | A shared filing cabinet with infinite drawers |
| **EBS** | Block Storage | Mounted to a single EC2/node at a time | A hard drive attached to one machine |
| **EFS** | File Storage (NFS) | Shared across many EC2/nodes simultaneously | A network shared drive (like a NAS) |

All three serve **different purposes** and solve **different problems** within EKS workloads.

---

## 2. Amazon S3 — Simple Storage Service

### What is S3?

S3 is AWS's **object storage service**. It stores data as **objects** (files + metadata) inside **buckets** (logical containers). There is no concept of a traditional file system hierarchy — paths like `folder/subfolder/file.txt` are actually just a flat key with `/` characters in the name.

### Core S3 Concepts

| Concept | Description |
|---|---|
| **Bucket** | A globally-named container for objects. Tied to a region. |
| **Object** | The actual data (file) + metadata + a unique key (path) |
| **Key** | The "path" of the object, e.g., `logs/2025/01/app.log` |
| **Storage Classes** | Standard, Intelligent-Tiering, Glacier (cost vs. retrieval trade-offs) |
| **Versioning** | Keep multiple versions of the same object |
| **Lifecycle Policies** | Automatically move/delete objects based on age |
| **Presigned URLs** | Temporary, time-limited access URLs to private objects |
| **Access Control** | Bucket policies, IAM policies, ACLs, Block Public Access |

### How S3 Works Internally

```
Client (application / kubectl / AWS CLI)
        |
        | HTTPS (REST API)
        v
  S3 Service Endpoint (e.g., s3.eu-west-2.amazonaws.com)
        |
        v
  S3 Bucket: my-bucket
        |
        |-- object: logs/app.log       (key + data + metadata)
        |-- object: config/settings.json
        |-- object: images/logo.png
```

S3 is **not** a file system. You **cannot mount S3 natively** to a Linux server. You access it via:
- AWS SDK (boto3, AWS Java SDK, etc.)
- AWS CLI (`aws s3 cp`, `aws s3 sync`)
- S3-compatible FUSE mounts (e.g., `s3fs`, `mountpoint-s3`) — not recommended for high-performance I/O
- CSI Drivers (Mountpoint for S3 CSI driver — see EKS section)

### S3 Durability & Availability

- **11 nines of durability** (99.999999999%) — data is stored across **≥3 Availability Zones**
- **99.99% availability** SLA for Standard storage class
- Data is automatically replicated; no RAID or replication needed

### S3 Use Cases

- Application artefact storage (Docker images via ECR backed by S3, Helm chart repos)
- Log archival and centralised log storage
- Terraform state backend (with DynamoDB for locking)
- Static website hosting
- Data lake / analytics input/output
- ML model storage
- Backup targets

---

## 3. Amazon EBS — Elastic Block Store

### What is EBS?

EBS provides **block-level storage volumes** that behave like raw hard drives. You attach an EBS volume to an EC2 instance (or EKS node), format it with a filesystem (ext4, xfs), and mount it — just like a physical disk.

### Core EBS Concepts

| Concept | Description |
|---|---|
| **Volume** | A block device (like a virtual hard drive), defined by size and type |
| **Volume Types** | gp2/gp3 (general purpose SSD), io1/io2 (provisioned IOPS SSD), st1 (throughput HDD), sc1 (cold HDD) |
| **Snapshots** | Point-in-time backups stored in S3 (but not directly accessible as S3 objects) |
| **Availability Zone** | EBS volumes exist in a **single AZ** — critical limitation |
| **Attachment** | One volume → one EC2 instance at a time (with Multi-Attach for io1/io2 in limited scenarios) |
| **Encryption** | AES-256 encryption at rest using AWS KMS |

### EBS Volume Types Explained

| Type | Use Case | Max IOPS | Max Throughput |
|---|---|---|---|
| `gp3` | General purpose (default, recommended) | 16,000 | 1,000 MB/s |
| `gp2` | Legacy general purpose | 16,000 | 250 MB/s |
| `io2` | Databases requiring high IOPS (RDS, Cassandra) | 64,000 | 1,000 MB/s |
| `io1` | High IOPS workloads (legacy) | 64,000 | 1,000 MB/s |
| `st1` | Big data, log processing (sequential reads) | 500 | 500 MB/s |
| `sc1` | Cold data (infrequent access, cheapest) | 250 | 250 MB/s |

### Key EBS Limitation: AZ Binding

> ⚠️ **Critical:** An EBS volume is locked to the **Availability Zone** it was created in.

If your EBS volume is in `eu-west-2a` and the Pod is scheduled on a node in `eu-west-2b`, the mount **will fail**. This is the number one operational gotcha when using EBS with EKS.

### EBS Snapshots

- Snapshots are incremental backups of an EBS volume
- Stored in S3 (but opaque — you cannot browse them as S3 objects)
- Can be used to restore a volume or copy to another region
- AWS Backup and EKS VolumeSnapshotClass can automate snapshot lifecycle

---

## 4. Amazon EFS — Elastic File System

### What is EFS?

EFS is a **fully managed NFS (Network File System)** service. It presents a standard POSIX-compliant file system that multiple EC2 instances (or EKS nodes/pods) can **mount simultaneously** across multiple Availability Zones.

### Core EFS Concepts

| Concept | Description |
|---|---|
| **File System** | The top-level EFS resource — an NFS endpoint |
| **Mount Target** | An NFS endpoint created in each AZ's subnet — what nodes actually connect to |
| **Access Points** | Application-specific entry points with enforced UID/GID and directory paths |
| **Performance Modes** | General Purpose (default) or Max I/O (highly parallelised workloads) |
| **Throughput Modes** | Bursting (default), Provisioned, or Elastic (auto-scales, recommended) |
| **Storage Classes** | Standard (multi-AZ) and One Zone (single AZ, cheaper) |
| **Encryption** | At-rest (KMS) and in-transit (TLS) |

### How EFS Works Internally

```
       EFS File System (NFS)
       fs-0abc1234def56789
              |
    ┌─────────┼──────────┐
    │         │          │
Mount Target  Mount Target  Mount Target
(eu-west-2a)  (eu-west-2b)  (eu-west-2c)
    │         │          │
  Node A    Node B    Node C     <-- All EKS Worker Nodes
  Pod 1     Pod 2     Pod 3      <-- All pods mount SAME filesystem
    │         │          │
    └─────────┴──────────┘
        Shared /data volume
```

All pods, regardless of which node or AZ they are on, read/write to the **same shared file system** concurrently.

### EFS vs EBS — The Fundamental Difference

| Feature | EBS | EFS |
|---|---|---|
| Access | 1 node at a time | Many nodes simultaneously |
| AZ scope | Single AZ | Multi-AZ |
| File system | You manage (ext4, xfs) | Managed NFS (POSIX) |
| Performance | Very high IOPS possible | Lower IOPS, high throughput |
| Cost | Cheaper per GB | More expensive per GB |
| Kubernetes access mode | `ReadWriteOnce` | `ReadWriteMany` |

---

## 5. Comparison Table

| Feature | S3 | EBS | EFS |
|---|---|---|---|
| **Storage type** | Object | Block | File (NFS) |
| **Access method** | HTTP/SDK API | Block device (mount) | NFS mount |
| **Concurrent access** | Unlimited | 1 node (standard) | Unlimited |
| **AZ scope** | Regional (multi-AZ) | Single AZ | Regional (multi-AZ) |
| **POSIX compliant** | ❌ | ✅ | ✅ |
| **Mountable as filesystem** | Via FUSE/CSI only | ✅ natively | ✅ natively |
| **Kubernetes access mode** | N/A (not native PV) | ReadWriteOnce | ReadWriteMany |
| **Durability** | 11 nines | 99.999% | 11 nines |
| **Cost (approx.)** | ~$0.023/GB/month | ~$0.08/GB/month (gp3) | ~$0.30/GB/month |
| **Ideal for in EKS** | Artefacts, logs, backups | Databases, stateful apps | Shared config, ML models |

---

## 6. Storage in Kubernetes — Core Concepts

Before diving into EKS-specific integrations, it's essential to understand how Kubernetes models storage.

### PersistentVolume (PV)

A **PersistentVolume** is a cluster-level storage resource provisioned by an admin (or dynamically by a StorageClass). It has a lifecycle independent of any pod.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-ebs-pv
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: gp3
  awsElasticBlockStore:
    volumeID: vol-0abc123456789
    fsType: ext4
```

### PersistentVolumeClaim (PVC)

A **PVC** is a request for storage by a pod/workload. Kubernetes matches it to an available PV (or dynamically provisions one).

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-app-storage
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp3
  resources:
    requests:
      storage: 20Gi
```

### StorageClass

A **StorageClass** defines a "class" of storage and enables **dynamic provisioning** — Kubernetes creates the underlying volume (EBS, EFS) automatically when a PVC is created.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer   # <-- critical for EBS AZ binding
allowVolumeExpansion: true
```

### CSI (Container Storage Interface)

The **CSI** is the standard interface through which Kubernetes communicates with storage providers. AWS maintains two CSI drivers for EKS:

| CSI Driver | Manages |
|---|---|
| `ebs.csi.aws.com` | EBS volumes |
| `efs.csi.aws.com` | EFS file systems |
| `s3.csi.aws.com` (Mountpoint) | S3 buckets (via FUSE) |

### Access Modes

| Mode | Meaning | Typical Storage |
|---|---|---|
| `ReadWriteOnce` (RWO) | One node reads+writes | EBS |
| `ReadOnlyMany` (ROX) | Many nodes read | EBS (snapshot), EFS |
| `ReadWriteMany` (RWX) | Many nodes read+write | EFS |
| `ReadWriteOncePod` (RWOP) | One pod reads+writes | EBS (EKS 1.22+) |

---

## 7. EBS in EKS — Deep Dive

### How EBS integrates with EKS

EKS uses the **AWS EBS CSI Driver** (`aws-ebs-csi-driver`) to manage EBS volumes. This is an EKS **Add-on** that should be installed in every production cluster.

### Installation

```bash
# Via AWS CLI (recommended for EKS)
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name aws-ebs-csi-driver \
  --service-account-role-arn arn:aws:iam::ACCOUNT_ID:role/AmazonEKS_EBS_CSI_DriverRole

# Verify
kubectl get pods -n kube-system -l app=ebs-csi-controller
kubectl get pods -n kube-system -l app=ebs-csi-node
```

### Required IAM Permissions

The EBS CSI driver needs an **IRSA (IAM Roles for Service Accounts)** role with the following AWS-managed policy:

```
arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```

This policy permits: `ec2:CreateVolume`, `ec2:AttachVolume`, `ec2:DetachVolume`, `ec2:DeleteVolume`, `ec2:DescribeVolumes`, `ec2:CreateSnapshot`, etc.

### Terraform Example — EBS CSI Add-on

```hcl
resource "aws_eks_addon" "ebs_csi_driver" {
  cluster_name             = aws_eks_cluster.main.name
  addon_name               = "aws-ebs-csi-driver"
  service_account_role_arn = aws_iam_role.ebs_csi.arn
  resolve_conflicts        = "OVERWRITE"
}

resource "aws_iam_role" "ebs_csi" {
  name = "${var.cluster_name}-ebs-csi-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.eks.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${aws_iam_openid_connect_provider.eks.url}:sub" = 
            "system:serviceaccount:kube-system:ebs-csi-controller-sa"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ebs_csi" {
  role       = aws_iam_role.ebs_csi.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}
```

### Full EBS Workflow in EKS

```
1. Developer creates a PVC requesting 20Gi gp3 storage
        |
2. Kubernetes sees unbound PVC → triggers CSI dynamic provisioning
        |
3. EBS CSI Controller (running in kube-system) calls EC2 API:
   ec2:CreateVolume (in the correct AZ based on WaitForFirstConsumer)
        |
4. EBS volume (vol-0xyz) is created in eu-west-2a
        |
5. Pod is scheduled → node in eu-west-2a
        |
6. EBS CSI Node DaemonSet on that node calls:
   ec2:AttachVolume → /dev/xvdba appears on node
        |
7. kubelet formats the device (mkfs.ext4) and mounts it into pod
        |
8. Pod reads/writes /data as a normal directory
```

### StorageClass — gp3 Best Practice

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  kmsKeyId: arn:aws:kms:eu-west-2:ACCOUNT:key/KEY_ID
reclaimPolicy: Retain             # Don't auto-delete volumes on PVC deletion
volumeBindingMode: WaitForFirstConsumer  # Wait for pod scheduling to pick AZ
allowVolumeExpansion: true
```

### EBS PVC Example — Stateful App (e.g., PostgreSQL)

```yaml
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp3
  resources:
    requests:
      storage: 100Gi

---
# StatefulSet using the PVC
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    spec:
      containers:
        - name: postgres
          image: postgres:15
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: gp3
        resources:
          requests:
            storage: 100Gi
```

### EBS Snapshots in EKS (VolumeSnapshot)

```yaml
# VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ebs-vsc
driver: ebs.csi.aws.com
deletionPolicy: Retain

---
# Take a snapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snap-2025
spec:
  volumeSnapshotClassName: ebs-vsc
  source:
    persistentVolumeClaimName: postgres-data
```

### EBS Limitations in EKS

| Limitation | Impact |
|---|---|
| Single AZ only | Pod must be in same AZ as volume — use topology-aware scheduling |
| ReadWriteOnce | Only one pod can write at a time |
| Node detach/attach time | Volume reattachment on node failure takes ~1-2 minutes |
| Not suitable for shared storage | Multiple replicas cannot share one EBS volume |

---

## 8. EFS in EKS — Deep Dive

### How EFS integrates with EKS

EKS uses the **AWS EFS CSI Driver** (`aws-efs-csi-driver`) to mount EFS file systems into pods. Unlike EBS, EFS volumes are **not created dynamically per PVC by default** — you create one EFS file system and multiple pods share it.

### Installation

```bash
# Via EKS Add-on
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name aws-efs-csi-driver \
  --service-account-role-arn arn:aws:iam::ACCOUNT_ID:role/AmazonEKS_EFS_CSI_DriverRole
```

### Required IAM Permissions

```
arn:aws:iam::aws:policy/service-role/AmazonEFSCSIDriverPolicy
```

Allows: `elasticfilesystem:DescribeFileSystems`, `elasticfilesystem:DescribeMountTargets`, `elasticfilesystem:CreateAccessPoint`, `elasticfilesystem:DeleteAccessPoint`

### EFS File System Setup (Terraform)

```hcl
resource "aws_efs_file_system" "eks" {
  creation_token = "${var.cluster_name}-efs"
  encrypted      = true
  kms_key_id     = var.kms_key_arn

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = { Name = "${var.cluster_name}-efs" }
}

# Create a mount target in each AZ subnet
resource "aws_efs_mount_target" "eks" {
  for_each = toset(var.private_subnet_ids)

  file_system_id  = aws_efs_file_system.eks.id
  subnet_id       = each.value
  security_groups = [aws_security_group.efs.id]
}

# Security group: allow NFS (port 2049) from EKS nodes
resource "aws_security_group" "efs" {
  name   = "${var.cluster_name}-efs-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [var.node_security_group_id]
  }
}
```

### EFS StorageClass with Dynamic Provisioning

EFS CSI supports **dynamic provisioning** via Access Points — each PVC gets its own Access Point (a scoped directory path) in the same EFS file system.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap          # Use Access Points
  fileSystemId: fs-0abc1234def56789
  directoryPerms: "700"
  gidRangeStart: "1000"
  gidRangeEnd: "2000"
  basePath: "/dynamic_provisioning"
reclaimPolicy: Retain
volumeBindingMode: Immediate         # EFS is multi-AZ, no need to wait
```

### EFS PVC — ReadWriteMany (Shared Storage)

```yaml
# PVC — any number of pods can mount this
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-config
  namespace: production
spec:
  accessModes:
    - ReadWriteMany          # Key difference from EBS
  storageClassName: efs-sc
  resources:
    requests:
      storage: 5Gi

---
# Deployment — 5 replicas all sharing the same volume
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 5
  template:
    spec:
      containers:
        - name: app
          image: my-web-app:latest
          volumeMounts:
            - name: shared-data
              mountPath: /app/shared
      volumes:
        - name: shared-data
          persistentVolumeClaim:
            claimName: shared-config
```

### EFS Use Cases in EKS

| Use Case | Why EFS |
|---|---|
| ML model serving | Multiple inference pods share the same large model files |
| Shared configuration | Config files read by many replicas simultaneously |
| CI/CD build caches | Shared Maven/npm/pip cache across build pods |
| Content management | CMS platforms (WordPress) needing shared upload directories |
| Log aggregation staging | Multiple pods writing logs to a shared path |
| Jupyter notebooks | Shared notebook directories in data science clusters |

---

## 9. S3 in EKS — Deep Dive

### Native S3 Access (SDK — Most Common)

The most common way workloads in EKS use S3 is via the **AWS SDK** directly in application code. Pods assume an IAM role via **IRSA** and make S3 API calls.

```yaml
# ServiceAccount with IRSA annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/MyAppS3Role
```

```python
# Python application code (boto3)
import boto3

s3 = boto3.client('s3')   # Automatically uses IRSA credentials
s3.upload_file('output.csv', 'my-bucket', 'results/output.csv')
```

### Mountpoint for Amazon S3 CSI Driver

AWS provides a CSI driver that mounts S3 buckets as **FUSE-based filesystems** inside pods.

```bash
# Install via Helm
helm install aws-mountpoint-s3-csi-driver \
  aws-mountpoint-s3-csi-driver/aws-mountpoint-s3-csi-driver \
  --namespace kube-system
```

```yaml
# PersistentVolume for S3
apiVersion: v1
kind: PersistentVolume
metadata:
  name: s3-pv
spec:
  capacity:
    storage: 1200Gi
  accessModes:
    - ReadWriteMany
  mountOptions:
    - allow-delete
    - region eu-west-2
  csi:
    driver: s3.csi.aws.com
    volumeHandle: s3-csi-driver-volume
    volumeAttributes:
      bucketName: my-ml-model-bucket

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: s3-claim
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: ""
  resources:
    requests:
      storage: 1200Gi
  volumeName: s3-pv
```

### S3 Limitations When Mounted as Filesystem

> ⚠️ S3 is **not a real POSIX filesystem**. FUSE-based mounting has limitations:

- No atomic rename operations
- No hard links or symbolic links
- Sequential reads perform well; random I/O is poor
- Eventual consistency for concurrent writes
- **Not suitable for databases or anything requiring POSIX locks**

Use the SDK for proper S3 access in production workloads. Use Mountpoint only for read-heavy, large object scenarios (ML model loading, media files).

### Terraform State on S3 (Relevant to EKS Platform Teams)

```hcl
terraform {
  backend "s3" {
    bucket         = "gagan-terraform-state"
    key            = "eks/production/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:eu-west-2:ACCOUNT:key/KEY_ID"
    dynamodb_table = "terraform-state-lock"
  }
}
```

---

## 10. Are They Required for EKS?

### Short Answer

| Service | Required for EKS itself? | Required for typical workloads? |
|---|---|---|
| **EBS** | ✅ Effectively yes (default storage class) | ✅ Yes — stateful apps, databases |
| **EFS** | ❌ Not required | ✅ Yes — shared storage workloads |
| **S3** | ⚠️ Indirectly (EKS uses S3 internally) | ✅ Yes — most production apps |

### EBS and EKS

EKS uses EBS **internally** for several things:
- **etcd** (the control plane key-value store) runs on EBS volumes managed by AWS
- Worker node root volumes are EBS-backed
- The **default StorageClass** in most EKS clusters is `gp2` or `gp3` (EBS)

The **EBS CSI Driver** is required if you want any Kubernetes PersistentVolume backed by EBS. Without it, dynamic provisioning of EBS volumes is not available.

### EFS and EKS

EFS is **not required** for EKS to function. However, without it you cannot use `ReadWriteMany` volumes in EKS. If any of your workloads need shared persistent storage across pods, EFS is the natural answer on AWS.

### S3 and EKS

S3 is used by AWS EKS infrastructure:
- EKS API server audit logs → CloudWatch (backed by S3)
- EKS Add-on artefacts stored in S3
- Container images via ECR (internally backed by S3)

For **your workloads**, S3 is not required — but almost every production EKS environment uses S3 for logs, artefacts, backups, or state.

---

## 11. End-to-End Architecture Walkthrough

Here is a complete end-to-end picture of how all three services fit into a typical EKS production environment:

```
┌────────────────────────────────────────────────────────────────────┐
│                        AWS Region (eu-west-2)                      │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                     EKS Cluster                             │  │
│  │                                                             │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐               │  │
│  │  │  Node AZ-a│  │  Node AZ-b│  │  Node AZ-c│               │  │
│  │  │           │  │           │  │           │               │  │
│  │  │ ┌───────┐ │  │ ┌───────┐ │  │ ┌───────┐ │               │  │
│  │  │ │Pod DB │ │  │ │Pod API│ │  │ │Pod API│ │               │  │
│  │  │ │       │ │  │ │       │ │  │ │       │ │               │  │
│  │  │ └───┬───┘ │  │ └───┬───┘ │  │ └───┬───┘ │               │  │
│  │  └─────┼─────┘  └─────┼─────┘  └─────┼─────┘               │  │
│  │        │              │              │                       │  │
│  │        │ RWO          │ RWX          │ RWX                   │  │
│  │        │              │              │                       │  │
│  │    ┌───▼───┐     ┌────▼──────────────▼────┐                 │  │
│  │    │  EBS  │     │         EFS            │                 │  │
│  │    │(AZ-a) │     │  (Multi-AZ NFS share)  │                 │  │
│  │    │gp3 vol│     │  /shared/config        │                 │  │
│  │    │100 GB │     │  /shared/models        │                 │  │
│  │    └───────┘     └────────────────────────┘                 │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │ kube-system                                         │   │  │
│  │  │  - aws-ebs-csi-driver (controller + node daemonset) │   │  │
│  │  │  - aws-efs-csi-driver (controller + node daemonset) │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────┐                           │
│  │          Amazon S3                 │                           │
│  │  ┌──────────────────────────────┐  │                           │
│  │  │ my-app-logs/                 │  │ ← Application log output  │
│  │  │ terraform-state/             │  │ ← IaC state backend       │
│  │  │ helm-charts/                 │  │ ← Helm chart repository   │
│  │  │ backups/ebs-snapshots/       │  │ ← EBS snapshot exports    │
│  │  │ ml-models/                   │  │ ← Large model artefacts   │
│  │  └──────────────────────────────┘  │                           │
│  └────────────────────────────────────┘                           │
└────────────────────────────────────────────────────────────────────┘
```

### Data Flow — Stateful Database Pod (EBS)

```
1. Helm deploys PostgreSQL StatefulSet
2. StatefulSet creates PVC (storageClass: gp3, 100Gi, RWO)
3. EBS CSI controller provisions vol-0abc (eu-west-2a)
4. Pod scheduled to node in eu-west-2a
5. EBS CSI node DaemonSet attaches vol-0abc to node
6. kubelet mounts /dev/xvdba at /var/lib/postgresql/data
7. PostgreSQL writes data to /var/lib/postgresql/data
8. AWS Backup creates daily EBS snapshot → stored in S3 (opaque)
```

### Data Flow — Shared Config Volume (EFS)

```
1. Platform team creates EFS file system (fs-0xyz) via Terraform
2. Mount targets created in each AZ subnet
3. EFS StorageClass created pointing to fs-0xyz
4. App team creates PVC (storageClass: efs-sc, 5Gi, RWX)
5. EFS CSI creates an EFS Access Point scoped to /dynamic/pvc-uuid
6. All 5 replicas of the Deployment mount the same PVC
7. All pods read/write /app/shared concurrently via NFS
```

### Data Flow — S3 Object Storage (SDK)

```
1. Platform team creates IAM role with S3 permissions (Terraform)
2. IRSA annotation on ServiceAccount maps Pod identity to IAM role
3. Pod starts → AWS SDK auto-discovers credentials via metadata endpoint
4. Application code calls s3.put_object() / s3.get_object()
5. Data flows over HTTPS to S3 endpoint (VPC endpoint avoids internet)
6. S3 stores object across ≥3 AZs with 11 nines durability
```

---

## 12. Security Considerations

### EBS Security

| Control | Implementation |
|---|---|
| Encryption at rest | Set `encrypted: "true"` and `kmsKeyId` in StorageClass |
| Encryption in transit | Not applicable (traffic stays on AWS hypervisor fabric) |
| Access control | IAM + IRSA on EBS CSI driver role |
| Snapshot security | Snapshots inherit volume encryption; restrict cross-account sharing |
| Kyverno/Gatekeeper policy | Enforce encrypted StorageClasses only |

```yaml
# Kyverno policy — enforce EBS encryption
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-ebs-encryption
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-storageclass-encryption
      match:
        any:
          - resources:
              kinds: [StorageClass]
              selector:
                matchLabels:
                  provisioner: ebs.csi.aws.com
      validate:
        message: "EBS StorageClasses must have encryption enabled"
        pattern:
          parameters:
            encrypted: "true"
```

### EFS Security

| Control | Implementation |
|---|---|
| Encryption at rest | Enable on EFS creation (KMS) |
| Encryption in transit | TLS enabled on mount (enforced via EFS policy) |
| Network access | Security group allowing port 2049 from node SG only |
| Access Points | Use Access Points to scope per-app access within EFS |
| EFS Resource Policy | Deny access outside of VPC |

```json
// EFS Resource Policy — deny non-VPC access
{
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": { "AWS": "*" },
      "Action": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpc": "vpc-0abc12345"
        }
      }
    }
  ]
}
```

### S3 Security

| Control | Implementation |
|---|---|
| Encryption at rest | SSE-S3 or SSE-KMS (enforce via bucket policy) |
| Encryption in transit | Enforce HTTPS via bucket policy `aws:SecureTransport` |
| Access control | IAM policies + IRSA (no static credentials in pods) |
| Block public access | Enable all four Block Public Access settings |
| VPC Endpoint | Use S3 Gateway Endpoint to keep traffic off the internet |
| Bucket policy | Deny `s3:*` unless via VPC endpoint |

```json
// S3 Bucket Policy — enforce TLS and VPC endpoint
{
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Condition": {
        "Bool": { "aws:SecureTransport": "false" }
      }
    },
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Condition": {
        "StringNotEquals": {
          "aws:sourceVpce": "vpce-0abc1234"
        }
      }
    }
  ]
}
```

---

## 13. Summary & Decision Tree

### When to Use What

```
Your workload needs persistent storage in EKS
           │
           ▼
   Does only ONE pod need to write to it?
           │
     ┌─────┴──────┐
    YES            NO
     │              │
     ▼              ▼
   Use EBS      Do you need a real filesystem (POSIX)?
  (ReadWriteOnce)    │
                ┌────┴─────┐
               YES          NO
                │            │
                ▼            ▼
             Use EFS       Use S3
          (ReadWriteMany)  (SDK/API)
```

### Quick Reference

| Scenario | Service | Access Mode |
|---|---|---|
| PostgreSQL / MySQL database | EBS (gp3) | ReadWriteOnce |
| Redis single-node | EBS (gp3) | ReadWriteOnce |
| ML model inference (multi-replica) | EFS | ReadWriteMany |
| Shared build cache (CI/CD pods) | EFS | ReadWriteMany |
| Application logs → long-term retention | S3 (SDK) | N/A |
| Terraform state | S3 | N/A |
| Backup artefacts | S3 | N/A |
| Content/media files (multi-pod) | EFS or S3 | RWX / SDK |
| Large ML model loading (read-only) | S3 Mountpoint | ReadWriteMany |

### CSI Driver Summary

| Driver | Helm Chart | EKS Add-on Name |
|---|---|---|
| EBS CSI | `aws-ebs-csi-driver` | `aws-ebs-csi-driver` |
| EFS CSI | `aws-efs-csi-driver` | `aws-efs-csi-driver` |
| S3 Mountpoint | `aws-mountpoint-s3-csi-driver` | `aws-mountpoint-s3-csi-driver` |

