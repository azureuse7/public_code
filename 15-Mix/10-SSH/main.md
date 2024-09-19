- An SSH key consists of two components: 
- A **public** **key** and a **private** **key**. These keys are generated using cryptographic algorithms, and they work together as a pair. 
- The public key is meant to be shared with others, while the private key must be kept secret and protected. 
- Therefore, the private key remains securely stored on the developer's local machine & the public key can be safely shared with GitHub.

```tf
ssh-keygen -t ed25519
```
-Now this will create public and private key 
- Public key can be stored say in VM
- Now to acesss the VM  
```tf
ssh -i <privatekey> <username><ip>
```

```tf
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

cd ~/.ssh
ls -la ~/.ssh 

ssh -keygen -R <IP address>

ssh user@<ip addresss> - l <private key>
