# Ansible Step 4: Ad-Hoc Commands
> Ad-hoc commands let you run a single Ansible task without writing a playbook. They are useful for quick one-off operations like package installation, service checks, or running shell commands across all hosts.

# How to install something on other servers using ad-hoc commands

# Tell ansible to use sudo (become)
ansible all -m apt -a update_cache=true --become --ask-become-pass


# Install a package via the apt module
ansible all -m apt -a name=vim-nox --become --ask-become-pass


# Install a package via the apt module, and also make sure it’s the latest version available
ansible all -m apt -a "name=snapd state=latest" --become --ask-become-pass


# Upgrade all the package updates that are available
ansible all -m apt -a upgrade=dist --become --ask-become-pass