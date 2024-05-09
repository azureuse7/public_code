# how would be install some thing on other servers 

# Tell ansible to use sudo (become)
ansible all -m apt -a update_cache=true --become --ask-become-pass


# Install a package via the apt module
ansible all -m apt -a name=vim-nox --become --ask-become-pass


# Install a package via the apt module, and also make sure it’s the latest version available
ansible all -m apt -a "name=snapd state=latest" --become --ask-become-pass


# Upgrade all the package updates that are available
ansible all -m apt -a upgrade=dist --become --ask-become-pass