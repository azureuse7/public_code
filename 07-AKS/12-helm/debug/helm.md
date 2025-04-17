**1. Scaffold a chart**

\# create a working directory and scaffold a chart called myapp
```yaml
mkdir helm-demo && cd helm-demo

helm create myapp
```
Helm generates this tree (paths trimmed):


```yaml
myapp/
├── .helmignore
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── hpa.yaml
    ├── ingress.yaml
    ├── tests/
    │   └── test-connection.yaml
    └── _helpers.tpl
```
-----
**2. Trim it down to a minimal example**

Delete everything **except** deployment.yaml, service.yaml, \_helpers.tpl, and tests/test-connection.yaml.
Then adjust the remaining files as follows.

**Chart.yaml**

```yaml
apiVersion: v2
name: myapp
description: Simple NGINX deployment demo
type: application
version: 0.1.0           # chart version
appVersion: "1.25.2"     # image tag (semver or SHA)
```
**values.yaml**
```yaml
image:
  repository: nginx
  tag: 1.25.2
service:
  type: ClusterIP
  port: 80

```
**templates/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ include "myapp.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "myapp.name" . }}
    spec:
      containers:
        - name: nginx
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: 80
```
**templates/service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "myapp.fullname" . }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 80
  selector:
    app: {{ include "myapp.name" . }}

```
**templates/tests/test-connection.yaml**

Helm automatically runs this Job when you execute helm test.
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "myapp.fullname" . }}-test"
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox:1.36
      command: ['sh', '-c', 'wget -qO- http://{{ include "myapp.fullname" . }}:{{ .Values.service.port }}']

```
-----
**3. Lint & render locally**

```yaml
helm lint myapp                  # static checks
helm template myapp ./myapp | tee rendered.yaml
```
*What you learn*:

- helm lint spots obvious mistakes (missing fields, bad syntax).
- helm template renders the YAML without touching the cluster—handy for PR reviews or diffs.
-----
**4. Install to the cluster**

```yaml
helm install myapp ./myapp --namespace demo --create-namespace
kubectl get all -n demo
```
Expected output (abridged):
```yaml
NAME                       READY   STATUS
pod/myapp-...              1/1     Running
service/myapp              ClusterIP   10.0.x.x   80/TCP
deployment.apps/myapp      1/1     1            1

```
**5. Verify manually**
```yaml
kubectl port-forward svc/myapp 8080:80 -n demo
```
\# In another shell:
```yaml
curl http://localhost:8080      # returns the NGINX welcome page HTML
```
-----
**6. Run the automated Helm test**

```yaml

helm test myapp -n demo         # executes the busybox wget pod

If the page is reachable, the Job exits 0 and Helm prints TEST SUITE PASSED.
```
-----
**7. Upgrade & rollback**

```yaml
\# simulate an image bump
helm upgrade myapp ./myapp --set image.tag=1.27.0 -n demo

\# accidentally broke something? rollback:
helm rollback myapp 1 -n demo   # roll back to revision 1
```
-----
**8. Clean up**
```yaml
helm uninstall myapp -n demo
kubectl delete namespace demo
```
**Key takeaways**

|**Step**|**Helm feature exercised**|
| :-: | :-: |
|helm create|scaffolds chart boilerplate|
|.Values.\* & Go templating|parameterise manifests|
|helm template|offline render for GitOps/diff|
|helm install / upgrade / rollback|release lifecycle|
|helm test|chartbundled smoke test|
|helm lint|static validation|

-----
**Next explorations**

- Add a **ServiceAccount** or **ConfigMap** template and reference it from the Deployment.
- Put the chart in a **Git repository**, render with **helm template** in CI, and use kubectl apply -f for GitOps.
- Package it (helm package) and push to your private OCI registry (helm push).

Let me know if you want deeper dives into helper templates (\_helpers.tpl), conditional logic ({{- if ... }}), or pipelinesafe YAML indenting.

