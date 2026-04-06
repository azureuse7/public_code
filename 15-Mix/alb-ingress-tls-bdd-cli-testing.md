# BDD ALB Ingress TLS — End-to-End Test Scenario & CLI Equivalent

## Overview

This document describes a BDD (Behave) end-to-end test scenario that validates the full lifecycle of an ALB Ingress with TLS on an EKS cluster, and how to replicate each step manually from the command line.

---

## BDD Scenario Breakdown

### Step 1 — Pre-flight check for cert-manager

The test uses the Kubernetes `CustomObjectsApi` to query the cluster for ClusterIssuer CRDs — specifically looking for one named `selfsigned-cluster-issuer`. This is a guard rail: if cert-manager isn't installed (meaning the CRD doesn't exist) or that particular issuer hasn't been created, the test skips itself rather than failing. This makes the test portable across cluster types where cert-manager may or may not be present.

### Step 2 — Request a TLS certificate

The test applies `cert_alb.yaml`, which is a cert-manager Certificate custom resource. This CR tells cert-manager: "Please generate a self-signed TLS certificate for the common name `ourservice.local` and store the resulting key pair in a Kubernetes Secret called `traefik-sidecar-secret-tls`." Cert-manager's controller picks this up, generates the certificate using the `selfsigned-cluster-issuer`, and populates the Secret automatically.

### Step 3 — Validate the issued certificate

The test reads the `traefik-sidecar-secret-tls` Secret from `bdd-namespace`, extracts the `tls.crt` field (which is PEM-encoded), decodes it, and inspects the X.509 metadata — specifically the signature algorithm. This confirms that cert-manager didn't just create an empty Secret, but actually issued a cryptographically valid certificate. It's a sanity check that the cert-manager pipeline (`ClusterIssuer → Certificate CR → Secret`) is working end to end.

### Step 4 — Deploy the Ingress and backing resources

The test loads and applies a YAML manifest from `./resources/ingress-alb.test.local`. This likely contains an Ingress resource annotated for the AWS Load Balancer Controller (e.g., `kubernetes.io/ingress.class: alb` or `ingressClassName: alb`), and possibly a backend Service or other supporting objects. The AWS Load Balancer Controller watches for these Ingress objects and provisions a real ALB in AWS in response.

### Step 5 — Wait for the ALB DNS name to appear

After the Ingress is created, the AWS Load Balancer Controller needs time to provision the actual ALB in AWS. The test polls the Ingress object's `.status.loadBalancer.ingress[0].hostname` field up to 12 times at 10-second intervals (so up to 2 minutes). Once the hostname appears, it means the controller has successfully created the ALB and written its DNS name back into the Ingress status. The test stores this DNS name and the host from the Ingress rules for subsequent steps.

### Step 6 — Verify the ALB is active in AWS

This step crosses the boundary from Kubernetes into AWS itself. Using boto3's `elbv2` client, the test queries the AWS API directly to find a load balancer tagged with the EKS cluster name. It polls up to 15 times at 20-second intervals (up to 5 minutes) because ALBs can take a while to transition from provisioning to active. It then asserts two things: the ALB state is `active`, and its DNS name matches what Kubernetes reported in Step 5. This confirms the Kubernetes Ingress and the real AWS infrastructure are in sync.

### Step 7 — Send traffic through the ALB

The test issues a real HTTP GET request to the ALB's DNS name, setting the `Host` header to match the hostname defined in the Ingress rules (e.g., `ourservice.local`). The Host header is critical because the ALB uses it to route the request to the correct target group. This simulates what a real client would do if DNS resolved `ourservice.local` to the ALB.

### Step 8 — Assert a successful response

The test checks that the response status code is `200`, confirming the entire chain works: `client → ALB → target group → pod`. If this passes, you know the ALB was provisioned correctly, listener rules are configured, the backend pods are healthy, and traffic flows end to end.

### Steps 9 & 10 — Cleanup

The test tears down what it created in reverse order. First it deletes the cert-manager Certificate CR, which triggers cert-manager to garbage-collect the `traefik-sidecar-secret-tls` Secret (via owner references). Then it deletes all the Kubernetes resources loaded in Step 4 — the Ingress and any associated objects. Deleting the Ingress triggers the AWS Load Balancer Controller to deprovision the ALB in AWS, so no infrastructure is left behind.

**In summary**, this scenario validates the full integration between cert-manager (certificate issuance), the AWS Load Balancer Controller (ALB provisioning), and the Kubernetes data plane (traffic routing) — and then cleans up after itself so the cluster is left in its original state.

---

## Manual CLI Testing

Here's how you can replicate each step of that BDD scenario manually from the command line.

### Step 1 — Check cert-manager and the ClusterIssuer exist

```bash
# Verify cert-manager pods are running
kubectl get pods -n cert-manager

# Check the ClusterIssuer exists
kubectl get clusterissuer selfsigned-cluster-issuer
```

If either command fails, cert-manager isn't set up and you'd need to install it first.

### Step 2 — Create the TLS certificate

```bash
# Create the namespace if it doesn't exist
kubectl create namespace bdd-namespace --dry-run=client -o yaml | kubectl apply -f -

# Apply the Certificate CR
kubectl apply -f ./resources/cert_alb.yaml -n bdd-namespace
```

### Step 3 — Verify the certificate was issued

```bash
# Check the Certificate CR status
kubectl get certificate -n bdd-namespace
# Look for READY = True

# Get more detail if it's not ready
kubectl describe certificate <certificate-name> -n bdd-namespace

# Confirm the secret was created
kubectl get secret traefik-sidecar-secret-tls -n bdd-namespace

# Extract and inspect the actual certificate
kubectl get secret traefik-sidecar-secret-tls -n bdd-namespace \
  -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout
```

The `openssl` output will show you the subject (`ourservice.local`), the signature algorithm, validity dates, and the issuer — confirming cert-manager issued it properly.

### Step 4 — Deploy the Ingress resources

```bash
kubectl apply -f ./resources/ingress-alb.test.local -n bdd-namespace

# Verify what was created
kubectl get ingress,svc,deployment,pods -n bdd-namespace
```

### Step 5 — Wait for the Ingress to get an ALB address

```bash
# Poll until the ADDRESS column is populated
kubectl get ingress ingress-alb -n bdd-namespace -w

# Or use a loop that mimics the BDD 12x10s polling
for i in $(seq 1 12); do
  ADDRESS=$(kubectl get ingress ingress-alb -n bdd-namespace \
    -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
  if [ -n "$ADDRESS" ]; then
    echo "ALB DNS: $ADDRESS"
    break
  fi
  echo "Attempt $i/12 — waiting 10s..."
  sleep 10
done

# Grab the hostname from the ingress rules
kubectl get ingress ingress-alb -n bdd-namespace \
  -o jsonpath='{.spec.rules[0].host}'
```

### Step 6 — Confirm the ALB is active in AWS

```bash
# List ALBs and find yours by DNS name
aws elbv2 describe-load-balancers --query "LoadBalancers[?DNSName=='$ADDRESS']" \
  --output table

# Or check state specifically
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?DNSName=='$ADDRESS'].State.Code" \
  --output text
# Should return: active

# If you want to find it by cluster tag instead
aws elbv2 describe-load-balancers --query "LoadBalancers[*].LoadBalancerArn" \
  --output text | tr '\t' '\n' | while read arn; do
  TAGS=$(aws elbv2 describe-tags --resource-arns "$arn" \
    --query "TagDescriptions[0].Tags[?Key=='elbv2.k8s.aws/cluster'].Value" \
    --output text)
  if [ "$TAGS" = "<your-cluster-name>" ]; then
    echo "Found ALB: $arn"
    aws elbv2 describe-load-balancers --load-balancer-arns "$arn" \
      --query "LoadBalancers[0].[DNSName,State.Code]" --output text
  fi
done
```

### Steps 7 & 8 — Send traffic and check HTTP 200

```bash
# Get the host from the ingress rules
HOST=$(kubectl get ingress ingress-alb -n bdd-namespace \
  -o jsonpath='{.spec.rules[0].host}')

# Make the request with the Host header
curl -v -H "Host: $HOST" http://$ADDRESS

# Or just check the status code
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: $HOST" http://$ADDRESS)
echo "HTTP Status: $STATUS"
# Should be 200
```

### Steps 9 & 10 — Cleanup

```bash
# Delete the Certificate CR (this should cascade-delete the TLS secret)
kubectl delete certificate <certificate-name> -n bdd-namespace

# Confirm the secret is gone
kubectl get secret traefik-sidecar-secret-tls -n bdd-namespace
# Should return "not found"

# Delete the ingress and associated resources
kubectl delete -f ./resources/ingress-alb.test.local -n bdd-namespace

# Verify the ALB is being deprovisioned
aws elbv2 describe-load-balancers --query "LoadBalancers[?DNSName=='$ADDRESS'].State.Code" \
  --output text
# Should eventually disappear or show "deprovisioning"

# Confirm everything is cleaned up
kubectl get all -n bdd-namespace
```

---

## All-in-One Shell Script

This script mirrors the BDD scenario exactly, with the same polling intervals and retry counts. Adjust the `NAMESPACE`, file paths, and cluster name to match your environment.

```bash
#!/bin/bash
set -e

NAMESPACE="bdd-namespace"
INGRESS_NAME="ingress-alb"
CERT_YAML="./resources/cert_alb.yaml"
INGRESS_YAML="./resources/ingress-alb.test.local"
SECRET_NAME="traefik-sidecar-secret-tls"

echo "=== Step 1: Pre-flight check ==="
kubectl get clusterissuer selfsigned-cluster-issuer || { echo "SKIP: no ClusterIssuer"; exit 0; }

echo "=== Step 2: Create TLS certificate ==="
kubectl apply -f "$CERT_YAML" -n "$NAMESPACE"

echo "=== Step 3: Wait for certificate to be ready ==="
kubectl wait --for=condition=Ready certificate --all -n "$NAMESPACE" --timeout=120s
kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
  -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout | grep "Signature Algorithm"

echo "=== Step 4: Deploy ingress resources ==="
kubectl apply -f "$INGRESS_YAML" -n "$NAMESPACE"

echo "=== Step 5: Wait for ALB address ==="
for i in $(seq 1 12); do
  ADDRESS=$(kubectl get ingress "$INGRESS_NAME" -n "$NAMESPACE" \
    -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
  [ -n "$ADDRESS" ] && break
  echo "Waiting... ($i/12)"
  sleep 10
done
[ -z "$ADDRESS" ] && { echo "FAIL: no ALB address after 120s"; exit 1; }
echo "ALB DNS: $ADDRESS"

echo "=== Step 6: Verify ALB is active in AWS ==="
for i in $(seq 1 15); do
  STATE=$(aws elbv2 describe-load-balancers \
    --query "LoadBalancers[?DNSName=='$ADDRESS'].State.Code" --output text 2>/dev/null)
  [ "$STATE" = "active" ] && break
  echo "ALB state: ${STATE:-not-found} ($i/15)"
  sleep 20
done
[ "$STATE" != "active" ] && { echo "FAIL: ALB not active"; exit 1; }
echo "ALB is active"

echo "=== Step 7 & 8: HTTP request ==="
HOST=$(kubectl get ingress "$INGRESS_NAME" -n "$NAMESPACE" \
  -o jsonpath='{.spec.rules[0].host}')
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: $HOST" "http://$ADDRESS")
echo "HTTP Status: $STATUS"
[ "$STATUS" -eq 200 ] || { echo "FAIL: expected 200, got $STATUS"; exit 1; }

echo "=== Step 9 & 10: Cleanup ==="
kubectl delete -f "$CERT_YAML" -n "$NAMESPACE" --ignore-not-found
kubectl delete -f "$INGRESS_YAML" -n "$NAMESPACE" --ignore-not-found

echo "=== ALL PASSED ==="
```
