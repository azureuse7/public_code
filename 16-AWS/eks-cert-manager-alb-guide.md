# Cert-Manager with AWS Load Balancer Controller on EKS

For **EKS**, the resources you need are:

1. `cert-manager` installed  
2. a `ClusterIssuer` named `selfsigned-cluster-issuer`  
3. a `Certificate` named something like `cert-alb`  
4. your backend `Deployment` and `Service`  
5. an ALB-backed `Ingress` with `ingressClassName: alb`

Also, for EKS, the **AWS Load Balancer Controller** must already be installed. It creates the ALB when you create the Ingress.

A key distinction: the cert-manager `Secret` you create is a **Kubernetes secret** for in-cluster TLS. An ALB’s **frontend HTTPS certificate** is normally configured with `alb.ingress.kubernetes.io/certificate-arn` and comes from **AWS Certificate Manager**, not from a Kubernetes TLS secret. So your `traefik-sidecar-secret-tls` secret is most useful for **backend TLS** to a pod or sidecar.

Because your scenario is using a `selfsigned-cluster-issuer`, treat it as a **test-only** setup.

---

## 0) Install the controllers if they are not already there

### cert-manager


## 1) Pre-flight check for cert-manager

Your test logic is sound. Before creating the `Certificate`, check both:

- the CRD exists
- the `ClusterIssuer` exists

```bash
kubectl get crd clusterissuers.cert-manager.io
kubectl get clusterissuer selfsigned-cluster-issuer
```

If you want a stricter guard:

```bash
kubectl get crd clusterissuers.cert-manager.io >/dev/null 2>&1 && \
kubectl get clusterissuer selfsigned-cluster-issuer >/dev/null 2>&1
```

---

## 2) Create the namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bdd-namespace
```

Apply it:

```bash
kubectl apply -f namespace.yaml
```

---

## 3) Create `selfsigned-cluster-issuer`

This is the exact resource your test is looking for.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-cluster-issuer
spec:
  selfSigned: {}
```

Apply it:

```bash
kubectl apply -f clusterissuer-selfsigned.yaml
kubectl get clusterissuer selfsigned-cluster-issuer
```

---

## 4) Create the `Certificate` resource

This is your `cert_alb.yaml`. It tells cert-manager to create a private key and certificate, then store them in the named `Secret`.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-alb
  namespace: bdd-namespace
spec:
  secretName: traefik-sidecar-secret-tls
  commonName: ourservice.local
  dnsNames:
    - ourservice.local
  subject:
    organizations:
      - test
  privateKey:
    algorithm: RSA
    size: 2048
  issuerRef:
    name: selfsigned-cluster-issuer
    kind: ClusterIssuer
    group: cert-manager.io
```

Apply it:

```bash
kubectl apply -f cert_alb.yaml
kubectl get certificate -n bdd-namespace
kubectl describe certificate cert-alb -n bdd-namespace
kubectl get secret traefik-sidecar-secret-tls -n bdd-namespace
```

---

## 5) Validate the issued certificate

You said the test reads `tls.crt` from the secret and inspects the X.509 metadata. You can do the same manually:

```bash
kubectl get secret traefik-sidecar-secret-tls \
  -n bdd-namespace \
  -o jsonpath='{.data.tls\.crt}' | base64 -d > tls.crt

openssl x509 -in tls.crt -text -noout
openssl x509 -in tls.crt -text -noout | grep "Signature Algorithm"
```

---

## 6) Create the backend workload

You need something behind the ALB. There are two common patterns.

### Pattern A — easiest: ALB speaks HTTP to the pod

Use this when you only care that ALB routing works and the cert-manager test is separate.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ourservice
  namespace: bdd-namespace
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ourservice
  template:
    metadata:
      labels:
        app: ourservice
    spec:
      containers:
        - name: echo
          image: hashicorp/http-echo:1.0.0
          args:
            - "-text=hello from ourservice"
          ports:
            - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: ourservice
  namespace: bdd-namespace
spec:
  selector:
    app: ourservice
  ports:
    - name: http
      port: 80
      targetPort: 5678
  type: ClusterIP
```

### Pattern B — ALB speaks HTTPS to the pod or sidecar

Use this if your `traefik-sidecar-secret-tls` secret is meant to be mounted into a sidecar that terminates TLS.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ourservice
  namespace: bdd-namespace
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ourservice
  template:
    metadata:
      labels:
        app: ourservice
    spec:
      containers:
        - name: app
          image: nginxdemos/hello
          ports:
            - containerPort: 8443
          volumeMounts:
            - name: tls-cert
              mountPath: /tls
              readOnly: true
      volumes:
        - name: tls-cert
          secret:
            secretName: traefik-sidecar-secret-tls
---
apiVersion: v1
kind: Service
metadata:
  name: ourservice
  namespace: bdd-namespace
spec:
  selector:
    app: ourservice
  ports:
    - name: https
      port: 443
      targetPort: 8443
  type: ClusterIP
```

---

## 7) Create the ALB `Ingress`

### If backend is plain HTTP

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-alb-test-local
  namespace: bdd-namespace
  annotations:
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /
spec:
  ingressClassName: alb
  rules:
    - host: ourservice.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ourservice
                port:
                  number: 80
```

### If backend is HTTPS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-alb-test-local
  namespace: bdd-namespace
  annotations:
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/backend-protocol: HTTPS
    alb.ingress.kubernetes.io/healthcheck-protocol: HTTPS
    alb.ingress.kubernetes.io/healthcheck-path: /
spec:
  ingressClassName: alb
  rules:
    - host: ourservice.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ourservice
                port:
                  number: 443
```

Apply it:

```bash
kubectl apply -f ingress-alb.test.local.yaml
kubectl get ingress -n bdd-namespace
kubectl describe ingress ingress-alb-test-local -n bdd-namespace
```

---

## 8) Wait for the ALB DNS name

Your test polls `.status.loadBalancer.ingress[0].hostname`. You can do the same manually:

```bash
kubectl get ingress ingress-alb-test-local \
  -n bdd-namespace \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
echo
```

---

## 9) Test traffic through the ALB

Because your Ingress rule is host-based, pass the host header:

```bash
ALB_DNS=$(kubectl get ingress ingress-alb-test-local \
  -n bdd-namespace \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl -i -H "Host: ourservice.local" "http://${ALB_DNS}/"
```

If everything is correct, you should get `200 OK`.

---

## 10) Cleanup

```bash
kubectl delete certificate cert-alb -n bdd-namespace
kubectl delete ingress ingress-alb-test-local -n bdd-namespace
kubectl delete service ourservice -n bdd-namespace
kubectl delete deployment ourservice -n bdd-namespace
```

---

## Minimal file set

If you want the exact files to create, use these four:

- `namespace.yaml`
- `clusterissuer-selfsigned.yaml`
- `cert_alb.yaml`
- `ingress-alb.test.local.yaml`

And add one workload manifest:

- `app.yaml`

---

## Most important EKS caveat

If your real goal is **HTTPS from client → ALB**, then this cert-manager secret is not enough by itself. For ALB listener TLS, use:

```yaml
alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'
alb.ingress.kubernetes.io/ssl-redirect: '443'
```

That is the AWS-native way to terminate TLS at the ALB. The Kubernetes secret from cert-manager is for workload-side TLS, not ALB frontend TLS.
