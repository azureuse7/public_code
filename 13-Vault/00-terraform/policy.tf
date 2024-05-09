resource "vault_policy" "policy1" {
  name = "policy1"

  policy = file ("policy/policy1.hcl")
}
