# Policies on Vault

Vault policies define what actions a user or application can perform on secrets. Users need to be assigned policies to interact with Vault resources.

## Using the UI

Log in to the UI as root and create an ACL policy:

- Go to **Policies** > **ACL Policies**.
- Create a new policy (e.g., `secret_policy`) with the following HCL content:

```hcl
path "kv/metadata/users" {
  capabilities = ["list"]
}

path "kv/meta/data" {
  capabilities = ["list"]
}

path "kv/data/users/shantanu" {
  capabilities = ["list", "read", "update"]
}

path "kv/data/users/shantanu" {
  capabilities = ["list", "read", "update", "create", "delete"]
}

path "kv/delete/users/shantanu" {
  capabilities = ["update", "delete"]
}
```

### Attach the Policy to a User

- Go to **Authentication** > **userpass** (or whichever auth method you created).
- Edit the user > **Token**.
- Under **Generate a Token Policy**, add the policy name.
- Save.
- Log in with the new user — they should be able to see the KV secret engine.

## Policies Using the CLI

First, delete the above KV engine if it exists, then recreate it via CLI.

### Log In to the Pod

```bash
kubectl exec -it <pod-name> -- /bin/sh
```

### Log In to Vault

```bash
vault login
```

### Enable the Secret Engine

```bash
vault secrets enable -version=2 kv
```

### View Policy Help

```bash
vault policy --help
```

### Create a User and Attach a Policy

```bash
vault write auth/userpass/users/bikram password=vault policies=secret_policy
```

## Using the API

### Create the Secret Engine via API

Create a JSON file named `secretengine.json`:

```json
{
  "options": {
    "version": "2"
  },
  "type": "kv"
}
```

### Use curl to Mount the Secret Engine

```bash
curl -k \
  -H "X-Vault-Token: <token>" \
  --data @secretengine.json \
  <ip>:8200/v1/sys/mounts/kv
```
