# Policies on vault

- we need to give users some policy 

# Using the UI 
- login the UI ia root and create some ACL  → ACL policies 
  
```t
name = secret_policy
policy 

path "kv/metadata/users"{
capabilities= ["list"]
}

path "kv/meta/data"{
capabilities= ["list"]
}

path "kv/data/users/shantanu"{
capabilities= ["list", "read", "update"]
}

path "kv/data/users/shantanu"{
capabilities= ["list", "read", "update", "create", "delete"]
}

path "kv/delete/users/shantanu"{
capabilities= [ "update", "delete"]
}

``` 
- we need to attach the policy 
- Go to Authentication → userpass (whatever you created)
- edit User → Token 
- Generate a Token policy → add policy name 
- save 
- Login with a new user and he should be able to see the - - - - secret engine KV

# Policies using CLI 

- delete the above KV 
```t
#Login to the pod 
k exec 

# Log into vault
vauly login

#enable the secret engine 
vault secret enable -version=2 kv 

# Create Policy 
vault policy --help 
create a user and attach policy → vault write auth/userpass/users/bikram password=vault policies=secret_policy

```
# Using API 

- Create a json file name: secretngine.json
```t
{
  "options" : {
    "version": "2"
  },
  "type": "kv"
}

# Use the curl command to create policy 
curl -k -h "X-vault-Token: <toke>: --data @secretengine.json <ip>:8200/v1/sys/mount/kv 