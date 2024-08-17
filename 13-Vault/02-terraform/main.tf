provider "vault" {
  address = "http://85.210.52.85:8200"
  token   = "hvs.BsRmQRn0UJpfgbQsDIwgtvDC"
}


resource "vault_mount" "kv" {
  path = "secret"
  type = "kv-v2"
}

resource "vault_kv_secret_v2" "example" {
  mount   = vault_mount.kv.path
  name    = "myapp/config"  # Path where the secret will be stored

  data_json = jsonencode({
    username = "myuser"
    password = "mypassword"
  })
}

data "vault_kv_secret_v2" "example" {
  mount = "secret"
  name = "myapp/config"  # Path to the secret
}

output "my_secret_value" {
  value     = data.vault_kv_secret_v2.example.data["username"]
  sensitive = true
}