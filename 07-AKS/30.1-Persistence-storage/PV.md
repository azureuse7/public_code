**Introduction**
- In Kubernetes, **Persistent Volumes (PVs)** and **Persistent Volume Claims (PVCs)** are used together to provide a durable storage mechanism for your workloads. 
- They allow containers to store data that outlives the lifecycle of individual Pods. This is crucial for stateful applications (e.g., databases, message queues) that require data persistence.

-----
**Persistent Volumes (PV)**

1. **Definition**:
   A Persistent Volume is a piece of storage in the cluster that has been provisioned (either statically by an administrator or dynamically by a storage class). It represents **actual physical storage** — which could be anything like local disk, NFS, an iSCSI target, a cloud storage volume, etc.
1. **Cluster Resource**:
   A PV is a **cluster-wide resource**, much like a node is a cluster resource. It is **not** tied to a specific namespace; it can be used by any namespace.
1. **Life Cycle**:
   1. **Provisioning**: A PV can be created **statically** by an admin (e.g., creating a YAML definition pointing to a specific NFS path) or **dynamically** by Kubernetes using a StorageClass (in which case Kubernetes talks to a provisioner that automatically creates volumes, for example, on AWS EBS, GCP Persistent Disks, or any supported storage backend).
   1. **Binding**: Once a PV is created, it can be bound to a PVC (we’ll see how in a moment).
   1. **Reclaim Policy**: Each PV has a “reclaim policy” which determines what happens to the underlying data once the volume is released. Possible reclaim policies are **Retain**, **Recycle**, or **Delete**.
1. **Attributes**:
   1. **Capacity**: Defines the storage capacity, such as 10Gi.
   1. **Access Modes**: Defines how the volume can be mounted (ReadWriteOnce, ReadOnlyMany, ReadWriteMany).
   1. **StorageClass**: If the volume was provisioned dynamically, it references a StorageClass (e.g., storageClassName: standard).
-----
**Persistent Volume Claims (PVC)**

1. **Definition**:
   A Persistent Volume Claim is essentially a **request** for storage by a user or a Pod. Instead of talking directly to a specific PV, a Pod says “I need X amount of storage with these capabilities,” and the PVC handles figuring out which PV to bind to.
1. **Namespace-Scoped**:
   PVCs live in a specific namespace. This means a PVC is only accessible within the namespace where it is created.
1. **Binding to a PV**:
   1. A PVC will match against available PVs in the cluster. Kubernetes looks at **capacity** and **access modes** to see if there’s a suitable PV.
   1. When a suitable PV is found, the PVC “binds” to that PV. This binding is **one-to-one**, meaning once a PV is bound to a PVC, it can’t be used by another PVC (unless it’s released and reclaimed in a subsequent process).
   1. If you use **dynamic provisioning**, the binding process automatically creates a new PV that matches the PVC’s requirements behind the scenes.
1. **Usage in Pods**:
   1. A Pod references a PVC in its volumes section (e.g., persistentVolumeClaim), and Kubernetes automatically handles attaching the correct underlying PV.
   1. The Pod then mounts the volume at a specified directory. Any data saved to that path remains on the PV, persisting even if the Pod is deleted or restarted.
-----
**How They Work Together**

1. **PVC → PV Binding**
   1. The user/application asks for storage via a PVC (specifying size, access modes, and optionally storage class).
   1. Kubernetes checks existing PVs or instructs a provisioner (via StorageClass) to create a new PV automatically (if dynamic provisioning is used).
   1. Once matched, they become **bound**.
1. **Pod Mounts PVC**
   1. In the Pod’s YAML, you add a volume entry that references the PVC name.
   1. This volume is mounted to the Pod’s filesystem at the specified mount path.
1. **Lifecycle and Reclaim**
   1. When a Pod no longer needs the volume and the PVC is deleted, the PV enters the “released” phase.
   1. Depending on the **reclaim policy** of that PV, Kubernetes may either keep the data around (Retain) or delete the data (Delete).
-----
**Example Workflow**

1. **Create a PVC**

   yaml

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard

```
1. **Kubernetes Finds or Creates a PV**
   1. If there’s already a PV with at least 10Gi capacity and ReadWriteOnce access mode, Kubernetes will bind my-pvc to that PV.
   1. Otherwise, if you have a StorageClass named “standard” configured, Kubernetes will dynamically provision a new PV for it.
1. **Use the PVC in a Pod**

   yaml

```
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: my-container
      image: nginx
      volumeMounts:
        - name: data-volume
          mountPath: /usr/share/nginx/html
  volumes:
    - name: data-volume
      persistentVolumeClaim:
        claimName: my-pvc

```
   1. The volume data-volume references the PVC my-pvc.
   1. Files stored at /usr/share/nginx/html will now persist in the underlying PV.
-----
**Key Benefits**

1. **Decoupling of Storage and Consumption**:
   PVs are cluster-level storage definitions, while PVCs are how the user or application *requests* storage. This separation simplifies multi-tenant scenarios and centralized storage management.
1. **Persistence Across Pod Lifecycles**:
   Data stored in a PV remains even when the Pod is destroyed. You can safely update or redeploy Pods without losing important data.
1. **Dynamic Provisioning**:
   By using StorageClasses, you don’t have to pre-create PVs. Kubernetes can create them on-demand, saving administrative overhead and providing more efficient resource usage.
1. **Reusability and Flexibility**:
   Different deployments (like Dev, Staging, Production) can use the same mechanism for requesting storage without worrying about *where* or *how* the underlying storage is physically provisioned.
-----
**Conclusion**

In summary, **Persistent Volumes (PVs)** in Kubernetes represent a cluster-level storage resource, while **Persistent Volume Claims (PVCs)** are the way applications request and use that storage. This design allows for a clean abstraction between actual storage provisioning and usage, ensuring your containerized workloads can rely on durable, stable, and portable storage across their lifecycle.

