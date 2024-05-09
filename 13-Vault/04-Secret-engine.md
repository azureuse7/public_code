# Secret engine

- Click on the secret engine  
- enable 
- Use kV
- create a secret  > kv > users > gautam 

```t
#List the secerts
vault secret list 

#Notice a secret has been created in UI
vault secret enable kv 

#List the secerts 
vault secret list 

#enable the secert 
vault secret enable -path=gautam kv 

#List the secerts 
vault secret list 

#Now if I want to write secrets to gutam, (adding key value )
vault kv put gautam/webui username=abc password=123

#How to read 
vaullt get gautam/webui 

``` 