# playbook 

install_apache.yml
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: install apache2 package  # name 
     apt:                           # which modeule
       name: apache2                # what we want to install


# Run the playbook
ansible-playbook --ask-become-pass install_apache.yml


install_apache.yml (second version)
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: update repository index
     apt:
       update_cache: yes
 
   - name: install apache2 package
     apt:
       name: apache2

# install_apache.yml (third version)
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: update repository index
     apt:
       update_cache: yes
 
   - name: install apache2 package
     apt:
     name: apache2
 
   - name: add php support for apache
     apt:
       name: libapache2-mod-php
       
# install_apache.yml (fourth version)
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: update repository index
     apt:
       update_cache: yes
 
   - name: install apache2 package
     apt:
       name: apache2
       state: latest
 
   - name: add php support for apache
     apt:
       name: libapache2-mod-php
       state: latest
remove_apache.yml
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: remove apache2 package
     apt:
       name: apache2
       state: absent
 
   - name: remove php support for apache
     apt:
       name: libapache2-mod-php
       state: absent