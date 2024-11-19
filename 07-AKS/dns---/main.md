#### You have three Kubernetes resource definitions:

- **Deployment**: Creates and manages multiple instances of a simple Python HTTP server.
- **Service**: Exposes the Deployment's Pods internally within the cluster for load balancing.
- **Pod**: Runs a **curl** command to test the Service by making an HTTP request.
  

These resources work together to deploy an application, expose it via a Service, and test the application's availability and functionality.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test-pod
  template:
    metadata:
      labels:
        app: test-pod
    spec:
      containers:
      - name: python-http-server
        image: python:2.7
        command: ["/bin/bash"]
        args: ["-c", "echo \" Hello from $(hostname)\" > index.html; python -m SimpleHTTPServer 80"]
        ports:
        - name: http
          containerPort: 80 
```



- **spec.selector.matchLabels.app: test-pod:** The Deployment uses this selector to identify the Pods it manages, targeting Pods with the label **app: test-pod**.

- **spec.template:**

  - **metadata.labels.app: test-pod:** Labels the Pods created by this Deployment with **app: test-pod.**

  - **spec.containers:**

      - **name**: python-http-server: Names the container **python-http-server.**

    - **image**: python:2.7: Uses the Python 2.7 Docker image.

    - **command** and args: Overrides the default command to:

      - **Create** an **index.html** file with the content Hello from $(hostname), where $(hostname) is the Pod's hostname.

      - **Start a simple HTTP server** using Python's SimpleHTTPServer module on port 80.

- **ports**:

    - **name**: http: Names the exposed port **http**.

    - **containerPort**: 80: Exposes port **80** from the container.

### Function
- **Deployment's Role**: Manages a set of identical Pods running the simple HTTP server.

##### Interlinking:

- The Pods are labeled **app: test-pod**, allowing the Service to select them.

- The exposed port **80** is named **http**, which will be referenced by the Service.

### Service Configuration
```yaml
kind: Service
apiVersion: v1
metadata:
  name: test-service
spec:
  selector:
    app: test-pod
  ports:
  - protocol: TCP
    port: 4000
    targetPort: http
```
### Explanation


- **spec**.selector.app: test-pod: The Service targets Pods with the label **app: test-pod.**

- **spec.ports:**

    - **protocol**: TCP: Specifies the TCP protocol.

    - `**port**: 4000: Exposes port **4000** within the cluster for accessing the Service.

    - **targetPort**: http: Routes incoming traffic to the Pods' container port named http (which maps to **containerPort: 80**).

### Function
- **Service's Role**: Provides a stable endpoint (**test-service:4000)** for accessing the Pods, handling load balancing among them.

- **Interlinking**:

  - The Service uses the label selector to discover and route traffic to the appropriate Pods.

  - The **targetPort** references the named port **http** in the Pods, ensuring traffic reaches the correct application port.

### Client Pod Configuration
```yaml
apiVersion: v1
kind: Pod 
metadata: 
  name: client-pod
spec:
  containers:
  - name: curl
    image: appropriate/curl
    command: ["/bin/sh"]
    args: ["-c", "curl test-service:4000"]
```
### Explanation


- **spec**.containers:

  - **name**: curl: Names the container **curl**.

  - **image**: appropriate/curl: Uses a minimal Docker image with **curl** installed.

  - **command** and args:

    - **Runs** **/bin/sh -c "curl test-service:4000".**

    - This sends an HTTP GET request to the Service **test-service** on port **4000**.

### Function
- **Client Pod's Role**: Acts as a test client to verify that the Service is correctly routing traffic to the Pods.

#### Interlinking:

  - The client Pod uses the internal DNS name test-service to resolve the Service's ClusterIP.

  - Demonstrates in-cluster communication and service discovery.

### Interconnection of Components
### 1. Labels and Selectors
####  Deployment and Service:

- The Deployment labels its Pods with **app: test-pod.**

- The Service selects Pods with **app: test-pod.**

#### Service and Client Pod:

The client Pod accesses the Service using its name **test**-**service**.
### 2. Port Configuration
#####  Pods' Exposed Port:

- The Pods expose port **80**, named **http**.
##### Service's Ports:

- Exposes port **4000** within the cluster.

- Forwards traffic to Pods' port named **http**.

### 3. Communication Flow
##### 1) Client Pod Initiates Request:

- The **curl** command in **client**-pod sends an HTTP request to **test-service:4000.**
##### 2)Service Receives Request:

- The Service **test**-**service** listens on port **4000**.

- Uses label selector **app**: **test**-pod to identify target Pods.

##### 3)Service Forwards Request to Pods:

- Routes the request to one of the Pods on their container port **80**.
##### 4)Pod Handles Request:

- The Python HTTP server in the Pod serves the **index**.**html** file.

- Response includes **Hello from <hostname>**, indicating which Pod served the request.

## Detailed Breakdown of Interactions
#### A. Deployment and Pods
- Replica Management:

- The Deployment ensures that three Pods are always running.
#### Pod Template:

- Each Pod runs the same container configuration.
##### Unique Hostnames:

- Each Pod's hostname is unique, which is reflected in the index.html content.
#### B. Service Functionality
##### Internal Load Balancing:

- The Service balances incoming requests across all available Pods.
##### Service Discovery:

- Kubernetes provides DNS resolution, allowing test-service to be resolved within the cluster.
#### C. Client Pod Testing
##### Verification:

- The client Pod tests the end-to-end functionality by making an HTTP request.
##### Result Observation:

You can retrieve the response by checking the logs of the client-pod:


### Potential Issues and Considerations
#### 1. Port Naming Consistency
##### Case Sensitivity:

- Kubernetes port names are case-sensitive.
#### Correct Port Name:

- Ensure **targetPort**: **http** in the Service matches the port name in the Pods (which is http).
##### 2. Python Version
#### Deprecation of Python 2.7:

- Python 2.7 is end-of-life; consider using Python 3.x.
#### Updating the Command:

- For Python 3.x, use:

```yaml
args: ["-c", "echo \" Hello from $(hostname)\" > index.html; python -m http.server 80"]
```
##### 3. Security
#### SimpleHTTPServer Limitations:

##### Not suitable for production use due to lack of security features.
#### Alternative Solutions:

- Use a more robust web server like Nginx or Apache for production environments.
#### Enhanced Configurations
##### Updated Deployment with Python 3
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test-pod
  template:
    metadata:
      labels:
        app: test-pod
    spec:
      containers:
      - name: python-http-server
        image: python:3.9
        command: ["/bin/bash"]
        args: ["-c", "echo \" Hello from $(hostname)\" > index.html; python -m http.server 80"]
        ports:
        - name: http
          containerPort: 80 
```
### Updated Service for Clarity
#### Using Port Numbers:

```yaml
targetPort: 80
```
#### Complete Service Configuration:

```yaml
kind: Service
apiVersion: v1
metadata:
  name: test-service
spec:
  selector:
    app: test-pod
  ports:
  - protocol: TCP
    port: 4000
    targetPort: 80
```
#### Testing and Validation
### Deploy the Resources
#### Apply the Deployment and Service:

```yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```
- Wait for Pods to be Ready:

```yaml
kubectl get pods -l app=test-pod
```
- Run the Client Pod
Apply the Client Pod Configuration:

```yaml
kubectl apply -f client-pod.yaml
```
- Check the Client Pod Logs
Retrieve the Output:

```yaml
kubectl logs client-pod
```
#### Expected Output:

- Should display Hello from <hostname> indicating successful communication.
### Cleanup
Delete Resources After Testing:

```yaml
kubectl delete deployment test-deployment
kubectl delete service test-service
kubectl delete pod client-pod
```

https://medium.com/kubernetes-tutorials/kubernetes-dns-for-services-and-pods-664804211501