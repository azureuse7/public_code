# Kubernetes ExternalDNS to Create Record Sets in Azure DNS from AKS

ExternalDNS automatically creates and manages DNS records in Azure DNS based on Kubernetes Ingress and Service resources.

[![Image](https://www.stacksimplify.com/course-images/azure-aks-ingress-external-dns.png "Azure AKS Kubernetes - Masterclass")](https://www.udemy.com/course/aws-eks-kubernetes-masterclass-devops-microservices/?referralCode=257C9AD5B5AF8D12D1E1)

## Step-02: Create External DNS Manifests

ExternalDNS needs permissions to Azure DNS to add, update, and delete DNS record sets. Permissions can be granted in two ways:

- Using an Azure Service Principal
- Using Azure Managed Service Identity (MSI)

This guide uses **MSI**, which is the recommended approach for Azure.

### Gather Information Required for `azure.json`

```bash
# Get Azure Tenant ID
az account show --query "tenantId"

# Get Azure Subscription ID
az account show --query "id"
```

### Create `azure.json`

```json
{
  "tenantId": "c81f465b-99f9-42d3-a169-8082d61c677a",
  "subscriptionId": "82808767-144c-4c66-a320-b30791668b0a",
  "resourceGroup": "dns-zones",
  "useManagedIdentityExtension": true,
  "userAssignedIdentityID": "404b0cc1-ba04-4933-bcea-7d002d184436"
}
```

### Review `external-dns.yml` Manifest

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-dns
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: external-dns
rules:
- apiGroups: [""]
  resources: ["services","endpoints","pods", "nodes"]
  verbs: ["get","watch","list"]
- apiGroups: ["extensions","networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get","watch","list"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: external-dns-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-dns
subjects:
- kind: ServiceAccount
  name: external-dns
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
spec:
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: external-dns
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      serviceAccountName: external-dns
      containers:
      - name: external-dns
        image: k8s.gcr.io/external-dns/external-dns:v0.11.0
        args:
        - --source=service
        - --source=ingress
        #- --domain-filter=example.com # (optional) limit to only example.com domains
        - --provider=azure
        #- --azure-resource-group=externaldns # (optional) use DNS zones from a specific resource group
        volumeMounts:
        - name: azure-config-file
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: azure-config-file
        secret:
          secretName: azure-config-file
```

## Step-03: Create a Managed Service Identity (MSI) for ExternalDNS

### Create the MSI

In the Azure Portal, go to **All Services -> Managed Identities -> Add** and create with:

- **Resource Name:** aksdemo1-externaldns-access-to-dnszones
- **Subscription:** Pay-as-you-go
- **Resource group:** aks-rg1
- **Location:** Central US

Click **Create**.

### Add an Azure Role Assignment to the MSI

1. Open the MSI `aksdemo1-externaldns-access-to-dnszones`
2. Click **Azure Role Assignments -> Add role assignment**
3. Set the following:
   - **Scope:** Resource group
   - **Subscription:** Pay-as-you-go
   - **Resource group:** dns-zones
   - **Role:** Contributor

### Update `azure.json` with the Client ID

Go to the MSI **Overview** and note the **Client ID**, then update `azure.json`:

```json
"userAssignedIdentityID": "de836e14-b1ba-467b-aec2-93f31c027ab7"
```

## Step-04: Associate the MSI with the AKS Cluster VMSS

1. Go to **All Services -> Virtual Machine Scale Sets (VMSS)**
2. Open the VMSS associated with `aksdemo1` (for example, `aks-agentpool-27193923-vmss`)
3. Go to **Settings -> Identity -> User assigned -> Add**
4. Select `aksdemo1-externaldns-access-to-dnszones`

## Step-05: Create the Kubernetes Secret and Deploy ExternalDNS

```bash
# Create the secret from azure.json
cd kube-manifests/01-ExteranlDNS
kubectl create secret generic azure-config-file --from-file=azure.json

# List secrets
kubectl get secrets

# Deploy ExternalDNS
cd kube-manifests/01-ExteranlDNS
kubectl apply -f external-dns.yml

# Verify ExternalDNS logs
kubectl logs -f $(kubectl get po | egrep -o 'external-dns[A-Za-z0-9-]+')
```

Common log messages to look for:

```log
# Error Type 400 - identity not found
time="2020-08-24T11:25:04Z" level=error msg="azure.BearerAuthorizer#WithAuthorization: Failed to refresh the Token for request to https://management.azure.com/subscriptions/82808767-144c-4c66-a320-b30791668b0a/resourceGroups/dns-zones/providers/Microsoft.Network/dnsZones?api-version=2018-05-01: StatusCode=400 -- Original Error: adal: Refresh request failed. Status Code = '400'. Response body: {\"error\":\"invalid_request\",\"error_description\":\"Identity not found\"}"

# Error Type 403 - occurs when the MSI does not have access to the target resource

# Success message
time="2020-08-24T11:27:59Z" level=info msg="Resolving to user assigned identity, client id is 404b0cc1-ba04-4933-bcea-7d002d184436."
```

## Step-06: Deploy an Application and Test

### Deploy the Application

```bash
kubectl apply -f kube-manifests/02-NginxApp1

# Verify pods and services
kubectl get po,svc

# Verify ingress
kubectl get ingress
```

### Verify ExternalDNS Logs

Wait 3 to 5 minutes for the DNS record set to be created in DNS Zones:

```bash
kubectl logs -f $(kubectl get po | egrep -o 'external-dns[A-Za-z0-9-]+')
```

Expected success log output:

```log
time="2020-08-24T11:30:54Z" level=info msg="Updating A record named 'eapp1' to '20.37.141.33' for Azure DNS zone 'kubeoncloud.com'."
time="2020-08-24T11:30:55Z" level=info msg="Updating TXT record named 'eapp1' to '\"heritage=external-dns,external-dns/owner=default,external-dns/resource=ingress/default/nginxapp1-ingress-service\"' for Azure DNS zone 'kubeoncloud.com'."
```

### Verify the Record Set in Azure DNS Zones

Go to **All Services -> DNS Zones -> kubeoncloud.com** and verify that `eapp1.kubeoncloud.com` was created.

```bash
# List DNS record sets
az network dns record-set a list -g dns-zones -z kubeoncloud.com
```

Perform an `nslookup` test:

```bash
nslookup eapp1.kubeoncloud.com
# Server:		192.168.0.1
# Address:	192.168.0.1#53
#
# Non-authoritative answer:
# Name:	eapp1.kubeoncloud.com
# Address: 20.37.141.33
```

### Access the Application

```
http://eapp1.kubeoncloud.com
http://eapp1.kubeoncloud.com/app1/index.html
```

> **Note:** Replace `kubeoncloud.com` with your own domain name.
