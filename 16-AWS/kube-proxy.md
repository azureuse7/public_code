

**What Is kube-proxy on Amazon EKS?**

-   **Network proxy DaemonSet**\
    On each EC2 node in your EKS cluster, Amazon deploys a
    **kube-proxy** pod (as a DaemonSet in the kube-system namespace).
    It's *not* deployed to Fargate nodes by default. Its job is to
    reflect every Kubernetes Service and Endpoint into host-level
    networking rules so that ServiceIP:port and NodePort traffic gets
    forwarded to the right Pods
    ([[docs.aws.amazon.com]{.underline}](https://docs.aws.amazon.com/eks/latest/userguide/managing-kube-proxy.html?utm_source=chatgpt.com)).

-   **EKS Add-on**\
    Starting with recent EKS versions you can install and manage
    kube-proxy using the Amazon EKS **add-on** framework. That ensures
    you get AWS-curated, security-patched builds (based on the minimal
    EKS Distro image) and automatic compatibility with your cluster's
    Kubernetes version
    ([[docs.aws.amazon.com]{.underline}](https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html?utm_source=chatgpt.com)).

-   **iptables (default) vs. IPVS mode**\
    By default kube-proxy programs Linux iptables rules. In very large
    clusters, you can switch to IPVS mode to avoid per-packet rule
    scans---IPVS offers lower latency when you have thousands of
    Services
    ([[docs.aws.amazon.com]{.underline}](https://docs.aws.amazon.com/eks/latest/best-practices/ipvs.html?utm_source=chatgpt.com)).

**How kube-proxy Actually Works**

1.  **Watches the API server**\
    It keeps open watches on Service and Endpoints objects.

2.  **Calculates desired rules**

    -   For each Service it creates chains in the nat table
        (KUBE-SERVICES, KUBE-NODEPORTS, etc.).

    -   For each Endpoint it updates KUBE-SEP-\<hash\> chains pointing
        to Pod IPs.

3.  **Programs the kernel**

    -   **iptables mode**: inserts DNAT rules so packets sent to a
        Service IP get rewritten and sent to one of the healthy Pod IPs.

    -   **IPVS mode**: adds virtual server entries so that the kernel's
        IPVS module load-balances in-kernel.

4.  **Keeps them in sync**\
    Whenever a Pod comes up or dies, kube-proxy atomically updates the
    chains so that traffic shifts without a hitch.

**End-to-End Example**

Let's deploy a simple **nginx** app and expose it via a Kubernetes
Service. Then we'll see how kube-proxy on each node makes it reachable.

**1. Create Deployment and Service**
```
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
spec:
  replicas: 2
  selector:
    matchLabels: { app: nginx }
  template:
    metadata:
      labels: { app: nginx }
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        ports:
        - containerPort: 80
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  type: NodePort        # could also use LoadBalancer for an AWS NLB
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080     # fixed NodePort for clarity

```
```
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```
**2. Inspect Endpoints**
```
kubectl get endpoints nginx-svc -o wide
```
You'll see the two Pod IPs backing nginx-svc.

**3. Show iptables Rules (on any node)**
```
\# List the Service chain entries in nat table

iptables -t nat -L KUBE-SERVICES -n \--line-numbers
```
Typical output:
```
Chain KUBE-SERVICES (2 references)

num target prot opt source destination

1 KUBE-SEP-ABCDEF78 tcp \-- 0.0.0.0/0 10.100.243.12:80

2 KUBE-SEP-12345678 tcp \-- 0.0.0.0/0 10.100.243.34:80

3 KUBE-MARK-MASQ all \-- 0.0.0.0/0 10.100.243.0/24

4 KUBE-MARK-DROP all \-- 0.0.0.0/0 10.100.243.0/24
```
And the NodePort chain:
```
iptables -t nat -L KUBE-NODEPORTS -n \--line-numbers
```
```
Chain KUBE-NODEPORTS (1 references)

num target prot opt source destination

1 DNAT tcp \-- 0.0.0.0/0 0.0.0.0/0 tcp dpt:30080 to:10.100.243.12:80
```
Here kube-proxy has set up a DNAT so that any packet hitting
**NodeIP:30080** is forwarded to one of the nginx Pod IPs
([gallery.ecr.aws]{.underline}).

**4. Test Reachability**

From your laptop or another machine, hit the Node's IP:
```
curl http://\<any-NodeIP\>:30080
```
You should get the default nginx welcome page---traffic went:
```
Client → Node's TCP:30080 (iptables DNAT) → Pod's TCP:80 → Pod responds
via SNAT back to client
```
**Advanced Tips**

-   **Switch to IPVS**\
    For clusters with thousands of Services, edit the kube-proxy
    ConfigMap:
```
 kubectl -n kube-system edit configmap kube-proxy
  \# set mode: \"IPVS\"
```
> Then restart the DaemonSet. You'll see ipvsadm -L -n show virtual
> servers instead of iptables chains
> ([[docs.aws.amazon.com]{.underline}](https://docs.aws.amazon.com/eks/latest/best-practices/ipvs.html?utm_source=chatgpt.com)).

-   **Version management**\
    Use eksctl or the AWS CLI to upgrade the kube-proxy add-on and keep
    parity with your cluster's control plane version:
```
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name kube-proxy \
  --addon-version v1.33.0-eksbuild.2

```
-   **Monitoring**\
    kube-proxy exposes metrics
    (kubeproxy_iptables_sync_duration_seconds, etc.) that you can scrape
    via Prometheus or send to CloudWatch as custom metrics.

By running kube-proxy as a managed add-on and leveraging either iptables
or IPVS, Amazon EKS ensures your Service networking is resilient,
performant, and in lockstep with upstream Kubernetes.
