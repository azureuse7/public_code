- Creating time-bound SSH keys using HashiCorp Vault and using Certificate Authority (CA) certificates to access Azure Kubernetes Service (AKS) nodes involves several steps. 
- 


#### 1. Configure Vault

```
provider "vault" {
  address = "http://4.158.34.185:8200"
  token   = "hvs.mK3lRHFHStyKCyPKgwEjkddV"
}
```

##### a. Enable the SSH secrets engine
```
vault secrets enable -path=ssh ssh
```
```
# Enable the SSH secrets engine
resource "vault_mount" "ssh" {
  path = "ssh"  #Just a name 
  type = "ssh"
  description = "SSH secrets engine"
}
```
##### b. Configure the SSH role
You need to define a role that specifies the parameters for the SSH certificates. This includes the TTL (time-to-live), which will control how long the SSH key is valid.

```
# Configure the SSH role
resource "vault_ssh_secret_backend_role" "otp_role" {
  backend      = vault_mount.ssh.path
  name         = "aks-role"
  key_type     = "ca"
  default_user = "azureuser"  # Default SSH user on AKS nodes
  ttl          = "1h"         # Time-bound: Certificate valid for 1 hour
  allow_user_certificates = true
  allowed_users           = "azureuser"
  allow_host_certificates = true
  # allow_user_key_ids      = "*"
}
output "ssh_ca_private_key" {
  value = vault_generic_secret.ssh_ca_private_key.data["private_key"]
  sensitive = true
}
```


##### c. . Create the SSH key and store it in Vault


##### The tls_private_key resource in Terraform is used to generate a private key that can be used for 
- cryptographic operations, such as securing SSH connections, signing certificates, or encrypting data. 
- This resource can generate various types of private keys, including RSA, ECDSA, and Ed25519.
```
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 2048
}
```
##### vault_mount is used to manage secret engine mounts in Vault. 
- In this the vault_mount resource is used to enable "Key-Value version 2," 
- which is the second version of the Key-Value secrets engine in Vault.
```
resource "vault_mount" "kv" {
  path = "secret"
  type = "kv-v2"
}
```
##### Store the secret 
```
resource "vault_generic_secret" "ssh_key" {
  path = "secret/aks-ssh-key"
  data_json = jsonencode({
    private_key = tls_private_key.ssh.private_key_pem
    public_key  = tls_private_key.ssh.public_key_pem
  })
}
```

##### d. Configure the Vault SSH client helper (optional)
If you're using Vault's SSH client helper, configure it to automatically request and sign SSH certificates.

```
export VAULT_ADDR='https://your-vault-address:8200'
vault write -field=signed_key ssh/sign/aks \
    public_key=@$HOME/.ssh/id_rsa.pub
```



#### This Terraform code does the following:

- **tls_private_key**: Generates an SSH key pair.
- **vault_ssh_secret_backend_role**: Configures Vault with the role that will issue the time-bound SSH certificates.
- **vault_generic_secret**: Stores the SSH key in Vault for later use.
#### Use the SSH key to access AKS nodes
In this step, you will configure access to AKS nodes using the generated SSH certificate.

```
resource "azurerm_kubernetes_cluster_node_pool" "example" {
  # Your AKS node pool configuration

  ssh_config {
    public_key = tls_private_key.ssh.public_key_openssh
  }
}
```
- When you apply this configuration, Terraform will:

##### Generate a new SSH key.
Store the private key securely in Vault.
Configure your AKS node pool to accept connections using the public key.
##### 1. Requesting SSH Certificates
When you need to access an AKS node, you'll request an SSH certificate from Vault.

```
vault write -field=signed_key ssh/sign/aks \
    public_key=@$HOME/.ssh/id_rsa.pub \
    valid_principals="ubuntu"
```
This command will return a signed SSH certificate that is valid for the duration specified in the TTL.

##### 5. Accessing the AKS Node
Finally, use the signed SSH certificate to access your AKS nodes.

```
ssh -i ~/.ssh/id_rsa-cert.pub ubuntu@<AKS-node-IP>
```
##### 6. Automating the Workflow
You can automate the entire workflow by integrating the SSH certificate request process into your deployment pipelines or other automation tools.

##### Conclusion
This setup provides a secure and time-bound mechanism for accessing AKS nodes using SSH, leveraging Vault’s dynamic secret management capabilities. It ensures that access is temporary and controlled, minimizing the risk of unauthorized access. Terraform plays a crucial role in automating the infrastructure setup and ensuring consistency across environments.