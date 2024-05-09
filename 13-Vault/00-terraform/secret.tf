# create a secret 

resource "vault_mount" "kv-v2" {
  path        = "kv-v2"
  type        = "kv-v2"
}

resource "vault_mount" "trasnit" {
  path        = "transit"
  type        = "transit"
}

#
resource "vault_transit_secret_backend_key" "key" {
  depends_on = [vault_mount.transit]
  backend = transit
  name    = "dummy"
  deleteion_allowed = true 
}

# Plan and apply 