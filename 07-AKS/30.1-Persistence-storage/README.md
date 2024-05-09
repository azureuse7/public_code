https://jhooq.com/how-to-use-persistent-volume-and-persistent-claims-kubernetes/

# How can I retain the data after the end of pod life cycle?
How can I retain the data after the end of pod life cycle?


# What problems does it solve?
Containers running inside the pod can not share the files with each other.

All the files inside the container are temporary which means if you terminate the container you are going to lose all your files.
Secondly if in any case, your container crashes then there is no way to recover files.
Kuberenetes provides volume plugin as Persistent Volume to address the above problems.

The lifecycle of these volumes are independent of the lifecycle of pods.

So if PODs are terminated then volumes are unmounted and detached keeping the data intact.



# What is Persistent Volume(PV)?
In simple terms, it's storage available within your Kubernetes cluster. This storage can be provisioned by you or Kubernetes administrator.

It's basically a directory with some data in it and all the containers running inside the pods can access it. But Persistent Volumes are independent of the POD life cycle.

So if PODs live or die, persistent volume does get affected and it can be reused by some other PODs.

Kubernetes provides many volume plugins based on the cloud service provider you are using -

awsElasticBlockStore, azureDisk, azureFile, cephfs, cinder, configMap, csi, downwardAPI, emptyDir, fc (fibre channel), flexVolume, flocker, gcePersistentDisk, gitRepo (deprecated), glusterfs, hostPath, iscsi, local, nfs, persistentVolumeClaim, projected, portworxVolume, quobyte, rbd, scaleIO, secret, storageos, vsphereVolume



# AKS Storage -  Storage Classes, Persistent Volume Claims

- We are going to create a MySQL Database with persistence storage using **Azure Disks** 


## Step-02: Create following Kubernetes manifests
### Create Storage Class manifest
- https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode

If you create a conatiner and delete it the stoarge is lost.
To pressist data we can use volunes


### Create Persistent Volume Claims manifest
```
# Create Storage Class & PVC
kubectl apply -f kube-manifests/01-storage-class.yml
kubectl apply -f kube-manifests/02-persistent-volume-claim.yml

# List Storage Classes
kubectl get sc

# List PVC
kubectl get pvc 

# List PV
kubectl get pv
```


## Step-03: Create MySQL Database with all above manifests
```
# Create MySQL Database
kubectl apply -f kube-manifests/

# List Storage Classes
kubectl get sc

# List PVC
kubectl get pvc 

# List PV
kubectl get pv

# List pods
kubectl get pods 

# List pods based on  label name
kubectl get pods -l app=mysql
```

## Step-04: Connect to MySQL Database
```
# Connect to MYSQL Database
kubectl run -it --rm --image=mysql:5.6 --restart=Never mysql-client -- mysql -h mysql -pdbpassword11

# Verify usermgmt schema got created which we provided in ConfigMap
mysql> show schemas;
```



## Step-06: Delete PV exclusively - It exists due to retain policy
```
# List PV
kubect get pv

# Delete PV exclusively
kubectl get pv
kubectl delete pv <PV-NAME>

# Delete Azure Disks 
Go to All Services -> Disks -> Select and Delete the Disk
```


