# Ansible: Configuration Management

> A step-by-step learning path for Ansible — from setting up SSH key authentication between servers, to writing playbooks and using conditional task execution.

---

## Learning Path (follow in order)

| Step | File | Topic |
|------|------|-------|
| 1 | [01-SSH and Setup.md](01-SSH%20and%20Setup.md) | Generate SSH keys, copy public key to worker nodes, configure SSH agent |
| 2 | [02-git.md](02-git.md) | Install and configure Git on the Ansible control node |
| 3 | [03-installing-Ansible.md](03-installing-Ansible.md) | Install Ansible, configure the inventory file |
| 4 | [04-Ansible-comands.md](04-Ansible-comands.md) | Ad-hoc commands with the `apt` module, using `--become` for sudo |
| 5 | [05-playbook.md](05-playbook.md) | Write a playbook to install Apache and manage services |
| 6 | [06-when.md](06-when.md) | Conditional task execution with `when` for Ubuntu vs CentOS |

---

## Prerequisites

- Two servers (or VMs): one **control node** (Ansible installed), one or more **managed nodes**
- SSH access from the control node to all managed nodes
- Python installed on all managed nodes

---

## Quick Setup

### 1 — Generate an SSH key on the control node
```bash
ssh-keygen -t ed25519 -C "ansible-key"
```

### 2 — Copy the public key to each managed node
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub <managed-node-ip>
```

### 3 — Cache the passphrase (avoid re-entering every run)
```bash
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
```

### 4 — Create an inventory file
```ini
[webservers]
192.168.1.10
192.168.1.11

[dbservers]
192.168.1.20
```

### 5 — Test connectivity
```bash
ansible all -i inventory.ini -m ping
```

### 6 — Run a playbook
```bash
ansible-playbook -i inventory.ini install_apache.yml
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Inventory** | List of managed hosts (INI or YAML format) |
| **Ad-hoc command** | One-off task run without a playbook (`ansible all -m apt`) |
| **Playbook** | YAML file defining ordered tasks to run on hosts |
| **Module** | The unit of work (`apt`, `yum`, `service`, `copy`, `template`, etc.) |
| `--become` | Run tasks with `sudo` (privilege escalation) |
| `when` | Conditionally run a task based on facts (e.g., OS type) |
