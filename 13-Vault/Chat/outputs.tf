output "vault_namespace" {
  value = helm_release.vault.namespace
}

output "certificate_secret" {
  value = "example-com-tls"
}
