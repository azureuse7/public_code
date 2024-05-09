# update 
- install ansible 
  

# create an inventory file  
- touch inventory
- add IP address in the file--> <ip address> or you could add URL 
- push to git 

# make a connection to each server 
- ansible all -key-file <ssh path> -i inventory -m ping
- m --> module 


# create a config file, anisble reads this when ever it runs 
nano anisbile.config
- inventory = inventory
- private_key_file = <ssh path>
- save it

now run this should be same as above 
- ansible all -m ping 
- ansible all --list-host

# Push the file to github 


