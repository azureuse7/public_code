# Vault Authentication

There are many auth methods available in HashiCorp Vault. This document covers authentication via the UI, CLI, and API using the username/password method, as well as GitHub authentication.

## Authentication via UI Using Username and Password

The following steps walk through enabling and using the `userpass` auth method in the Vault UI:

- Log in to the UI.
- Go to **Access** > **Auth Methods**.
- Select **Username & Password**.
- Log in using a token.
- Enable a new method under **Access**.
- Click on **Username and Password**.
- Click **Create**.
- Enable the method and update.
- Notice there are now two auth methods.
- Click **userpass**.
- Create users.
- Add a username and password, then save.
- Log in with the username and password.

## Authentication via CLI Using Username and Password

### Log In to a Pod

```bash
kubectl exec -it <pod> -- /bin/bash
# or
kubectl exec -it <pod> -- /bin/sh

vault status
```

### Enable Auth for Username and Password

Log in using the root token first:

```bash
vault login
```

Then enable the `userpass` auth method:

```bash
vault auth enable userpass
```

#### Check in Vault That Auth Is Enabled

Navigate to the Vault UI to confirm the `userpass` method is listed under **Access > Auth Methods**.

#### Create a User and Password

By default, Vault mounts the `userpass` auth method at `auth/userpass/users`:

```bash
vault write auth/userpass/users/gagan password=ggagan
```

#### Verify in UI

Log in to the Vault UI and confirm the user appears under the `userpass` auth method.

### Log In with the User

```bash
vault login -method=userpass username=gagan
```

After entering the password, notice that Vault creates a token. The token includes applied policies and other information.

#### List the Auth Methods

```bash
vault auth list
```

#### Read the User Details

```bash
vault read auth/userpass/users/gagan
```

The user cannot see much or perform actions until a policy is assigned.

## Authentication via CLI Using GitHub

The GitHub auth method allows users to authenticate using a GitHub personal access token.

### Enable Auth for GitHub

Log in using the root token:

```bash
vault login
```

Enable the GitHub auth method:

```bash
vault auth enable github
```

#### Check in Vault That Auth Is Enabled

Navigate to the Vault UI to confirm the GitHub method is listed under **Access > Auth Methods**.

#### List the Auth Methods

```bash
vault auth list
```

#### Set the GitHub Organization

To log in, the organization name is used as the identifier. Replace `gagan` with your GitHub organization name:

```bash
vault write auth/github/config organization=gagan
```

#### Verify in UI

Log in to the Vault UI and confirm the GitHub auth method is configured correctly.

**Reference:** [Vault Authentication Tutorial](https://www.youtube.com/watch?v=-EHmM5ocUsM&ab_channel=LearnwithGVR)

## Authentication via API

The Vault HTTP API can also be used to enable auth methods and authenticate users.

### Create a Payload File

Create a file named `payload.json` and add the password:

```json
{
  "password": "gagan"
}
```

### Log In Using the API

Use a `curl` command to authenticate:

```bash
curl -k \
  -H "X-Vault-Token: <token>" \
  -X POST \
  --data @payload.json \
  http://<ip>/v1/auth/userpass/login/gagan
```

### Enable Userpass Using the API

```bash
curl -k \
  --header "X-Vault-Token: <token>" \
  --request POST \
  --data '{"type": "userpass"}' \
  http://<ip>/v1/sys/auth/userpass
```
