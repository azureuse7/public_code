# Vault as Certificate Issuer on a Kubernetes Cluster

This guide demonstrates how to use HashiCorp Vault as a Certificate Authority (CA) integrated with cert-manager on a Kubernetes cluster.

**References:**
- [Using HashiCorp Vault as Certificate Manager on a Kubernetes Cluster](https://genekuo.medium.com/using-hashicorp-vault-as-certificate-manager-on-a-kubernetes-cluster-155604d39a60)
- [HashiCorp Vault on Azure AKS Tutorial](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-azure-aks)
- [HashiCorp Vault PKI with cert-manager](https://aperogeek.fr/hashicorp-vault-pki-cert-manager/)
- [IBM Cloud Private: Using Vault to Issue Certificates](https://www.ibm.com/docs/en/cloud-private/3.2.x?topic=manager-using-vault-issue-certificates)

## Installing HashiCorp Vault

### Unseal and Log In

After deploying Vault, unseal it and log in using the root token:

```bash
kubectl exec vault-0 -- vault login $VAULT_ROOT_TOKEN
kubectl exec --stdin=true --tty=true vault-0 -- /bin/sh
vault secrets enable pki
vault secrets tune -max-lease-ttl=8760h pki
```

To configure the PKI engine as CA, generate a self-signed root certificate for signing certificates, set its TTL to 8760 hours, and write to a file called `demo-root-ca.json`.

```bash
vault write -format=json pki/root/generate/internal \
    common_name="Demo Root Certificate Authority" > /tmp/demo-root-ca.json

cat /tmp/demo-root-ca.json

vault write pki/root/generate/internal \
    common_name=example.com ttl=8760h
```

Configure the PKI engine certificate issuing and certificate revocation list (CRL) endpoints for the vault services in the default namespace.

```bash
vault write pki/config/urls \
    issuing_certificates="http://vault.default:8200/v1/pki/ca" \
    crl_distribution_points="http://vault.default:8200/v1/pki/crl"
```

Create a role that enables the creation of certificates under the `example.com` domain with any subdomains, and a policy that defines finer-grained permissions.

```bash
vault write pki/roles/example-dot-com \
    key_type=any \
    allowed_domains=example.com \
    allow_subdomains=true \
    max_ttl=5m
```

Once the role is created, create a policy named `pki` for the corresponding Vault PKI role.

```bash
vault policy write pki - <<EOF
path "pki*" { capabilities = ["read", "list"] }
path "pki/roles/example-dot-com"   { capabilities = ["create", "update"] }
path "pki/sign/example-dot-com"    { capabilities = ["create", "update"] }
path "pki/issue/example-dot-com"   { capabilities = ["create"] }
EOF
```

## Enable the Kubernetes Authentication Method

To simplify how applications interact with Vault, use the Kubernetes auth method. The Kubernetes auth method makes use of JWT tokens associated with Kubernetes Service Accounts.

To configure the auth method, use the local token and CA certificate created when the Vault pod starts, located at `/var/run/secrets/kubernetes.io/serviceaccount/`. Vault periodically re-reads the files in this folder to support short-lived tokens.

When an application tries to interact with Vault, Vault uses this configuration to verify and retrieve the application's identity with the Kubernetes API server and its TokenReview API.

```bash
vault auth enable kubernetes

vault write auth/kubernetes/config \
    token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
    kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443" \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

Create a Kubernetes authentication role named `issuer` that binds the `pki` policy defined earlier with a Kubernetes service account name and namespaces.

```bash
vault write auth/kubernetes/role/issuer \
    bound_service_account_names=issuer \
    bound_service_account_namespaces=cert-manager,default \
    policies=pki \
    ttl=20m
```

```bash
exit
```

After the above configuration, Vault with the PKI engine can act as CA, and the application (cert-manager) can interact with Vault and authenticate through the Kubernetes auth method (TokenReviewer API).

Upon authentication, Vault retrieves the policy defined for the role of the service account `issuer`. Vault can then issue certificates according to the permissions in the policy.

## Installing cert-manager, Configuring the Issuer, and Creating a Certificate

Install cert-manager to interact with the Vault PKI to issue certificates. After installation, check the custom resource definitions and pods created.

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install \
    cert-manager jetstack/cert-manager \
    --namespace cert-manager --create-namespace \
    --version v1.11.0 --set installCRDs=true
kubectl get crds
kubectl get po -n cert-manager
```

Create a service account called `issuer` and a service account token as a Secret resource. This secret will be referenced in the cert-manager Issuer resource to authenticate with Vault via the Kubernetes auth method when generating and issuing certificates.

```bash
kubectl create serviceaccount issuer
kubectl get sa
kubectl apply -f secret.yaml
kubectl get secrets
kubectl describe secret issuer-token
kubectl get secret issuer-token -o jsonpath={.data.token} | base64 -d
```

The `secret.yaml` manifest defines the service account token secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: issuer-token
  annotations:
    kubernetes.io/service-account.name: issuer
type: kubernetes.io/service-account-token
```

Create a cert-manager Issuer resource that references the issuer token and role for authentication against Vault, the Vault PKI certificate issuing endpoint, and the Vault server URL:

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: vault-issuer
  namespace: default
spec:
  vault:
    server: http://vault.default:8200
    path: pki/sign/example-dot-com
    auth:
      kubernetes:
        mountPath: /v1/auth/kubernetes
        role: issuer
        secretRef:
          name: issuer-token
          key: token
```

```bash
kubectl apply -f issuer.yaml
kubectl get issuer
kubectl describe issuer vault-issuer
```

Create a cert-manager Certificate resource. This will create a secret containing a certificate issued by Vault. The Certificate resource is managed by cert-manager.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: demo-example-com
  namespace: default
spec:
  secretName: example-com-tls
  issuerRef:
    name: vault-issuer
  commonName: demo.example.com
  dnsNames:
  - demo.example.com
```

```bash
kubectl apply -f certificate.yaml
kubectl get certificate
kubectl describe certificate demo-example-com

kubectl get secrets example-com-tls
kubectl describe secrets example-com-tls
```

## Install the ingress-nginx Controller

To demonstrate applications deployed on the Kubernetes cluster making use of Vault and cert-manager to issue and manage certificates, deploy a demo web application and enable TLS through an ingress resource. First, deploy an `ingress-nginx` controller to the Kubernetes cluster using Helm.

```bash
helm upgrade --install ingress-nginx ingress-nginx \
    --repo https://kubernetes.github.io/ingress-nginx \
    --namespace ingress-nginx --create-namespace
```

Create a deployment and a service for the web application.

```bash
kubectl create deployment web --image=gcr.io/google-samples/hello-app:1.0
kubectl expose deployment web --port=8080
kubectl get svc web
```

Within the ingress manifest, enable TLS by including a `tls` section to reference the secret containing the issued certificate.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  tls:
  - hosts:
    - demo.example.com
    secretName: example-com-tls
  rules:
  - host: demo.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 8080
```

```bash
kubectl apply -f ingress.yaml
kubectl get ingress
```

To simulate domain name resolution on the local machine, edit the hosts file with `sudo vi /etc/hosts` and add:

```
127.0.0.1 demo.example.com
```

Test the application by browsing `https://demo.example.com` and verifying the certificate in your browser.

You can also verify and show TLS handshake details by running the following command. The output shows the start date, expire date, and issuer info of the issued certificate (valid for 5 minutes based on the configuration).

```bash
curl -kivL https://demo.example.com
```

You can demonstrate automatic certificate renewal by refreshing the browser or rerunning the `curl` command after 5 minutes. The start date and expire date will have automatically renewed.

## Conclusion

The Kubernetes auth method simplifies how an application (cert-manager) uses a Kubernetes Service Account to authenticate and interact with HashiCorp Vault. The HashiCorp Vault PKI engine acts as a Certificate Authority to simplify the issuing process of certificates, which can be managed by cert-manager automatically and efficiently, including certificate renewal.

There are many other use cases for HashiCorp Vault in cloud-native platforms or applications, such as application secret injection and management.
