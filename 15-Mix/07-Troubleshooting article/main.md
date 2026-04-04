# Troubleshooting: Expired App Secret in Azure Key Vault

This document covers how to handle an expired application secret and update the value in Azure Key Vault.

## Scenario: App Secret Expired

If the app secret has expired, create a new secret and upload it to Key Vault.

## Look Up a Secret Value in Key Vault

To retrieve the value of a given secret from a specific Key Vault, use the following PowerShell snippet with the Azure CLI:

```bash
$vault = "<your-key-vault-name>"
$secret = "<your-secret-name>"

az keyvault secret show --name $secret --vault-name $vault | ConvertFrom-Json | Select-Object -Property value
```

Replace `<your-key-vault-name>` and `<your-secret-name>` with your actual Key Vault name and secret name.
