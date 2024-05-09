# Injecting vault secret into Pods using Sidecar

- Injector → fetches secrets from the vault to pods.  

- service account → makes a bridge between the vault and pods 

- Vault sidecar  --> looks at annotations and fetch the secret from the vault

```t
# create kv secret engine
vault secrets enable -path=internal kv-v2

#let’s add some secrets 
vault kv put internal/database/config username='shan' password='shan'

# now they are ready to be fetched by pods we deploy in Kubernetes 

#enable auth Kubernetes
vault auth enable kubernetes  

#k needs to authenticate with our cluster 
vault write auth/kubernetes/config kubernetes_host=”https://$KUBERNETES_PORT_443_TCP_ADDR:443”

#check if the hostname is added below
#access → auth method--> Kubernetes-> configuration-->configure 

#Two options you can upload CA certificate either using host or a Ca certificate 
#we need to create a policy → create a policy 

path "internal/data/database/config" {
  capabilities = ["read"]
}

# Create a service account 
k create sa internal-app.

#we also create a policy we need to map the two using a role. 
access -> auth method -->
name: internal-app
Bound service account names : internal-app
Bound service account namespace: default 
Generate Token Policy: Internal-app

#Check the roles is created 

#Launch application 
k apply -f k orgchart.yaml

#exec into pod

# Notice there is no secret 
cd /vault/secret 

# Add add the annotation file : patch.yaml 
k patch deployment orgchart --patch "$(cat patch.yaml)"

#Notice vaules are there now
cd /avult/secret 
cat database-config.txt

``` 

# Using API

```t

k port-forward vault-0 -n vault 8200

#Enable authentication
curl -k --header "X-Vault-Token: hvs.fix6NmFqLuWAezZp4LIUMaWS" --data '{"type": "kubernetes"}' --request POST  http://localhost:8200/v1/sys/auth/kubernetes

#ckeck in ui 

#Need to create roles
{
  "kubernetes_host": "https://10.96.0.1:443",
  "bound_service_account_names": "internal-app",
  "bound_service_account_namespaces": ["vault"],
  "policies": ["internal-app"],
  "max_ttl": 1800000
}

curl -k --header "X-Vault-Token: hvs.fix6NmFqLuWAezZp4LIUMaWS" --data @k8sauth.json --request POST  http://localhost:8200/v1/auth/kubernetes/config


#Need to attach the roles
curl -k --header "X-Vault-Token: hvs.fix6NmFqLuWAezZp4LIUMaWS" --data @k8sauth.json --request POST  http://localhost:8200/v1/auth/kubernetes/role/internal-app

#Check the roles
