- In Kubernetes, an init container is a specialized container that runs before the main application containers in a Pod. 
- Init containers can contain setup scripts or perform tasks that need to complete before the main application starts.

##### Step 1: Create a ConfigMap
- Create a ConfigMap if needed for your init container. For example:

``` 
apiVersion: v1
kind: ConfigMap
metadata:
  name: init-config
data:
  init-script.sh: |
    #!/bin/sh
    echo "Performing initialization tasks..."
    # Add your init tasks here
    touch /init-done
```     
``` 
kubectl apply -f configmap.yaml
``` 

##### Step 2: Create a Pod with an Init Container
- Create a Pod definition that includes both the init container and the main application container. 
- Save this definition in a file named pod-with-init.yaml:

``` 
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  initContainers:
  - name: init-myservice
    image: busybox
    command: ['sh', '-c', 'sh /etc/config/init-script.sh']
    volumeMounts:
    - name: config-volume    # name of the volume mount 
      mountPath: /etc/config # mount here 
  containers:
  - name: my-container
    image: nginx
    ports:
    - containerPort: 80
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: init-config  #name of the config 
``` 
``` 
kubectl apply -f pod-with-init.yaml
``` 
##### ConfigMap Definition

- The **configmap.yaml** file defines a ConfigMap named **init-config** with a shell script **init-script.sh** that performs initialization tasks.
#####  Pod Definition:

- The **pod-with-init.yaml** file defines a Pod named **my-pod** with an init container and a main application container.
  
- The init container named **init-myservice** uses the **busybox** image and runs the **init-script.sh** script from the ConfigMap.
  
- The main container named my-container uses the nginx image.
- Both the init container and the main container mount the ConfigMap as a volume at the **/etc/config** path.
  
##### Verifying the Configuration
To verify that the Pod has started correctly and the init container has run:

Check the Pod Status:
``` 
kubectl get pods

kubectl describe pod my-pod

kubectl logs my-pod -c init-myservice

kubectl exec -it my-pod -- /bin/sh
``` 
 
- Verify Init Tasks:
- Inside the Pod, check the results of the init tasks (e.g., the creation of the /init-done file):

``` 
ls /init-done
``` 
This setup ensures that the initialization script runs before the main application container starts. The init container will complete its tasks, and once finished, Kubernetes will start the main application container.