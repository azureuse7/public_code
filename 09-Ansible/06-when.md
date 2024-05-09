# install_apache.yml
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: update repository index
     apt:
       update_cache: yes
     when: ansible_distribution == "Ubuntu"
 
   - name: install apache2 package
     apt:
       name: apache2
       state: latest
     when: ansible_distribution == "Ubuntu"
 
   - name: add php support for apache
     apt:
       name: libapache2-mod-php
       state: latest
     when: ansible_distribution == "Ubuntu"
Gather facts, while limiting to a single host
 ansible all -m gather_facts --limit 172.16.250.248
install_apache.yml (updated to include centos)
 ---
 
 - hosts: all
   become: true
   tasks:
 
   - name: update repository index
     apt:
       update_cache: yes
     when: ansible_distribution == "Ubuntu"
 
   - name: install apache2 package
     apt:
       name: apache2
       state: latest
     when: ansible_distribution == "Ubuntu"
 
   - name: add php support for apache
     apt:
       name: libapache2-mod-php
       state: latest
     when: ansible_distribution == "Ubuntu"
 
   - name: update repository index
     dnf:
       update_cache: yes
     when: ansible_distribution == "CentOS"
 
   - name: install httpd package
     dnf:
       name: httpd
       state: latest
     when: ansible_distribution == "CentOS"
 
   - name: add php support for apache
     dnf:
       name: php
       state: latest
     when: ansible_distribution == "CentOS"