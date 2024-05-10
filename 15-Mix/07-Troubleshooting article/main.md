If the app secret expired 


Create a new secret and uplaod to KV

 

=============================================================================

 

To look at the secret value of a given secret in a given Key Vault


$vault = ""

$secret = ""

az keyvault secret show --name $secret --vault-name $vault | ConvertFrom-Json | Select-Object -Property value

==============================================================================

 

 

