# Secret Engine

The Vault Secret Engine stores and manages secrets. This document covers enabling and working with the Key-Value (KV) secrets engine via the UI and CLI.

## Enable via the UI

- Click on **Secret Engines**.
- Click **Enable**.
- Select **KV**.
- Create a secret: **KV** > **users** > **gagan**.

## Managing Secrets via CLI

### List the Secrets

```bash
vault secrets list
```

Notice the secret created in the UI is visible.

### Enable the KV Secret Engine

```bash
vault secrets enable kv
```

### List the Secrets Again

```bash
vault secrets list
```

### Enable the Secret Engine at a Custom Path

```bash
vault secrets enable -path=gagan kv
```

### List the Secrets to Confirm

```bash
vault secrets list
```

### Write Secrets to the Custom Path

Add key-value pairs to the `gagan` path:

```bash
vault kv put gagan/webui username=abc password=123
```

### Read the Secret

```bash
vault kv get gagan/webui
```
