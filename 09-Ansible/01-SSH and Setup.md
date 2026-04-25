# Ansible Step 1: SSH Key Setup and Server Preparation
> Before Ansible can manage remote servers, you need SSH key-based authentication between the control node and all managed nodes. This guide walks through generating a key pair, distributing the public key, and caching the passphrase.

# You need at least two servers: one Ansible control node and one managed (worker) node

- ip a --> get the IP address 
- Make sure you can ssh to the work server --> ssh<ip>

# You should be able to ssh 


# To generta a ssh key 
ssh-keygen -t ed25519 -C "gagan default"

- it asks where to save the key
- Press enter 
- It says for passphrase key 
- ls -la .ssh
- we have two keys one is the piblic and one private key

# Add the public key to a server
ssh-copy-id -i  <public key> <ip of sever>

# Connect to the server
- ssh <ip>
- enter the passphrase

# If you don't want to past the passkey every time
eval $(ssh-agent)
- This only chache your passkey
- 

