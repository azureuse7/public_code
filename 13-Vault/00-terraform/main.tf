provider "vault"{}

#enable authication using username and password
resource "vault_auth_backend" "userpass" {
  type = "userpass"  #The auth backend mount point. userpass/kubernets etc 
}


#lets create user
resource "vault_generic_endpoint" "dummy" {
  depends_on           = [vault_auth_backend.userpass]# it needs authication then only it can work
  path                 = "auth/userpass/users/dummy" # which users
  ignore_absent_fields = true

  data_json = <<EOT
{
  "policies": ["admin","dummy"],
  "password": "changeme"
}
EOT
}

# need to give in some valuves as below 
# URL: http://20.13.90.121:8200/ This is after you create the vault and have IP 
# export VAULT_TOKEN=hvs.9N1LtEs6DqLvAOEM4ZNYslST This is the root token 
# Apply this and its created auth and users