# Vault Authentication There are many auth methods 

# Authentication UI using username and password

- Login the UI 
- Access --> auth method
- lets use username 
- Login using token 
- enable a new method under access
- Click on usrname and password
- click on create
- enable method nd upadate
- Notice we have to auth method now
- click userpass 
- create users
- add username and password and save
- Login with username and password

# Authentication CLI using username and password



#### Login a pod
```
k exec -it <pod> bin/bash or bin/sh

vault status
```
### I need to enable auth for username and password
vault login
#using the  root token 

#enable vault auth userpass
```
vault auth enable userpass
```
#### Check-in vault that auth is enabled 

#### Create user and password
#### my default vault monts auth/userpass/users
```
vault write auth/userpass/users/gagan password=ggagan
```
#### Verify this in UI 

### Login with the user
```
vault login -method=userpass username=gagan
```
#### login using the password notice it created a token and with the token there are policy applied and other information

#### list the auth methos
```
Vault auth list 
```
#### read the deatils 
```
vault read auth/userpass/users/gagan
```
#### The user can’t see much or do anything and we need to assign the policy 
``` 

# Same can be down for github
```


#### I need to enable auth for username and password
```
vault login
```
#### login using the  root token 

#### enable vault auth github
```
vault auth enable github
```
#### Check-in vault that auth is enabled 

#### list the auth methos
```
Vault auth list 
```
#### To login, the organization name is the username in github
```
vault write auth/github/config organization=gagan
```
#### Verify this in UI 

https://www.youtube.com/watch?v=-EHmM5ocUsM&ab_channel=LearnwithGVR
 

#### Authentication API




#### create a payload.json file and add the password below
"password": "gagan"

#### Do a curl command to login 
```
curl -k -h 'X-vault-Token: <toke> -x post --data @payload.json http://<ip>/v1/auth/userspass/users/gagan 

``` 

#### Enable userpass using API 
```
curl -k --header 'X-vault-Token: <toke> --request POST --data '{"type": "userpass"}
```

#### login user using API 
