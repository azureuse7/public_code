# Ansible Step 2: Install Git and Configure GitHub SSH Access
> Git is needed on the Ansible control node to clone playbooks and roles from a repository. This guide covers installation and setting up an SSH key for GitHub.

# Install git
- git 

# create an account if you don't have one. 
- click on ssh and GPG keys 
- get the public key and copy it into github 
- clone with ssh git clone <URL>

# Tell git who we are 
- git config --global user.name "gagan"
- git config --global user.email "gagan@gmail.com"
- 