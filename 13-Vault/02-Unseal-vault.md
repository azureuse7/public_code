# UnSeal Vault using the UI and CLI

# UI

- To log in we need a minimum of three keys to unseal the vault. 
- Copy past the UI IP and put it on the browser and add :8200
- Login and download the keys 
- click on Unseal and add the keys to unseal with three keys 
- Add the root token to the login and Login

# CLI
- Remove old settings and remove disk etc 

```t
#Login to the vault pod 
k exec -it vault1-0 /bin/sh

# Notice its sealed
vault status  

#Init the pod
vault operator init  
#Copy the keys and token

# Use the keys to unseal
vault operator unseal 
# copy the keys and Repeat three times and Notice it would say sealed false 
# Copy The Ip and test 
``` 