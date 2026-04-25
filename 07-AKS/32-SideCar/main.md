https://www.youtube.com/watch?v=MDVEoGLDOh8&list=WL&index=35&t=4s

#### Fisrt we create a pod and test it 

```  
apiVersion: v1
kind: Pod
metadata:
  name: demo-sidecar
  containers:
  - name: main-container
    image: iam7hills/dockerdemo:nginxdemos
    ports:
      - containerPort: 8080
```  
- Add the rest of code and now it could ick file from side container 

- Create another conatiner 


```  
apiVersion: v1
kind: Pod
metadata:
  name: demo-sidecar
  containers:
  - name: main-container
    image: iam7hills/dockerdemo:nginxdemos
    ports:
      - containerPort: 8080
  - name: sidecar-container
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo 'index.html generated from sidecar' > /usr/share/nginx/html/index.html; sleep 30; done"]
```  

- But nothing work, bevuas we need to mount a vilume
at prset we onlu jhae two conatine in a pod

```  
k exec -it <pod> --conatiner<name>
/bin/sh
```  
- look for the file ls -lrt //usr/share/nginx/html/index.html
- cat /proc/mount
- cat /proc/mount | nginix
its not there becuase we need to mount a vilume

  volumes:
  - name: shared-html name of volume
    emptyDir: {}  This is the deafult volume by kubnernest


now e need to attcah them to the conatiners
```  
    volumeMounts:
    - name: shared-html
      mountPath: /usr/share/nginx/html
```  

apply and try now 
tyhe hmt should be different 


============================================================


- In Kubernetes, a **sidecar** container is a secondary container that runs alongside the primary application container within the same pod. The sidecar container extends or supports the functionality of the main container without being directly involved in the application's core function. This pattern is particularly useful for adding features such as monitoring, logging, configuration updates, or proxy functionality in a way that keeps these concerns separate from the main business logic of the application.

##### How Sidecars Work
- Sidecar containers share the same lifecycle as the main container: they are created and retired together with the primary container in a pod. They also share the same network space, meaning they can communicate with the main container over localhost, and they can optionally share volumes, which allows them to access the same files if needed.

##### Common Uses of Sidecar Containers
1)**Logging and Monitoring**: Sidecars can be used to collect logs from the main application, process them, and forward them to a central log store. They can also be used to gather metrics and push them to monitoring tools without modifying the application.

2)**Configuration**: Sidecars can dynamically fetch and update configuration files for a main application, especially useful in environments where applications need to be highly configurable without downtime.

3)**Networking**: Sidecars are often used to handle encryption and manage network communications, acting as proxies or gateways, particularly in service mesh architectures like Istio or Linkerd.

4)**Data Processing**: In scenarios where the main application generates data that needs to be processed (such as aggregating or filtering before sending it to a database), a sidecar container can handle these tasks.

##### Example: Using a Sidecar for Logging
Here’s an example of a Kubernetes pod configuration with a sidecar container that handles logging:

``` 
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: main-container
    image: main-app:1.0
    volumeMounts:
    - name: log-volume
      mountPath: /usr/src/app/logs

  - name: logger-sidecar
    image: logger-app:1.0
    volumeMounts:
    - name: log-volume
      mountPath: /logs

  volumes:
  - name: log-volume
    emptyDir: {}
```     
##### In this setup:

- The **main-container** runs the primary application, which outputs logs to /usr/src/app/logs.
- The **logger-sidecar**container shares the same volume and monitors the log directory at /logs, processing or forwarding the logs as needed.
- Both containers use a shared **emptyDir** volume, which is a temporary directory that exists as long as the pod exists.
  
##### Advantages of Using Sidecars
1)**Decoupling**: Sidecars help keep the primary application cleaner by decoupling auxiliary features like logging, monitoring, and network management.
2)**Scalability**: Each side of the application (main and sidecar) can be scaled independently if needed.
3)**Reusability**: The same sidecar container image can be used across multiple different applications, promoting reuse and standardization.
##### Considerations
- While sidecars offer numerous benefits, they also introduce additional complexity and resource overhead. It's important to weigh these factors against the benefits to determine if a sidecar is the right solution for your use case. In many modern cloud-native environments, especially those utilizing service meshes, sidecars are a standard pattern that effectively supports microservice architectures.