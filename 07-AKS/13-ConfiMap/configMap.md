-  To configure a Kubernetes Pod to use a ConfigMap both as environment variables and to mount it as a volume, you need to follow these steps:

##### Create a ConfigMap: 
- Define a ConfigMap YAML file that contains the key-value pairs of configuration data.
##### Create a Pod: 
- Define a Pod YAML file that references the ConfigMap for both environment variables and volume mounting.
  
##### Step 1: Create a ConfigMap
First, create a file named configmap.yaml with the following content:

``` 
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  database_url: "jdbc:mysql://localhost:3306/mydb"
  database_user: "root"
  database_password: "secret"
  log_level: "DEBUG"
  app.properties: |
    database_url=jdbc:mysql://localhost:3306/mydb
    database_user=root
    database_password=secret
    log_level=DEBUG
```     
``` 
kubectl apply -f configmap.yaml
``` 

##### Step 2: Create a Pod that Uses the ConfigMap
Next, create a file named pod.yaml with the following content:

``` 
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx
    env:
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: database_url
    - name: DATABASE_USER
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: database_user
    - name: DATABASE_PASSWORD
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: database_password
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: log_level
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: my-config
``` 
``` 
kubectl apply -f pod.yaml
``` 
#### Explanation
##### ConfigMap Definition:

- The **configmap.yaml** file defines a ConfigMap named **my-config** with several entries: 
- **database_url, database_user, database_password, log_level**, and a multiline string app.properties.
  
##### Pod Definition:

- The **pod.yaml** file defines a Pod named **my-pod** with a single container named **my-container** using the **nginx** image.
- The container has four environment variables **(DATABASE_URL, DATABASE_USER, DATABASE_PASSWORD, and LOG_LEVEL)** whose values are sourced from the corresponding keys in the **my-config** ConfigMap.

- The container also mounts the ConfigMap as a volume at the **/etc/config** path, making all ConfigMap entries available as files in this directory.

- To verify that the Pod has started correctly and is using the ConfigMap:

```
kubectl get pods

kubectl describe pod my-pod

kubectl exec -it my-pod -- /bin/sh
```
- Verify Environment Variables:
Inside the Pod, check the environment variables:

```
echo $DATABASE_URL
echo $DATABASE_USER
echo $DATABASE_PASSWORD
echo $LOG_LEVEL
```
- Verify Mounted ConfigMap:
Check the contents of the mounted volume:

```
cat /etc/config/app.properties
```
This should output the values specified in the ConfigMap, both as environment variables and as files in the mounted volume.