# Mixed Topics Reference

> A collection of standalone guides covering Kubernetes security profiles, networking, SSH, DNS, paths, troubleshooting, monitoring, and database concepts.

---

## Contents

| Directory / File | Topic |
|-----------------|-------|
| [01-Seccomps/](01-Seccomps/) | Seccomp profiles — restrict Linux syscalls in Kubernetes pods |
| [02-Regx/](02-Regx/) | Regular expressions — syntax, patterns, practical examples |
| [04-Links/](04-Links/) | Useful reference links |
| [05-Setting up Environment Variables in Mac OS/](05-Setting%20up%20Environment%20Variables%20in%20Mac%20OS/) | `export` and `.zshrc` / `.bash_profile` on macOS |
| [06-Absolute and Relative Paths/](06-Absolute%20and%20Relative%20Paths/) | File path types explained |
| [07-Troubleshooting article/](07-Troubleshooting%20article/) | Azure KeyVault access troubleshooting tips |
| [09-name resolution/](09-name%20resolution/) | DNS, hostname resolution, `/etc/hosts`, CoreDNS |
| [10-SSH/](10-SSH/) | SSH key generation, config file, tunnelling |
| [11-Nslookup/](11-Nslookup/) | `nslookup` and `dig` — DNS query tools |
| [12-Usefull.md/](12-Usefull.md/) | Useful AI tools and productivity links |
| [13-Dynatrace1/](13-Dynatrace1/) | Dynatrace APM — installation and key concepts |
| [14-SQL databases and NoSQL.md](14-SQL%20%28Structured%20Query%20Language%29%20databases%20and%20NoSQL%20%28Not%20Only%20SQL%29.md) | SQL vs NoSQL — when to use each, key differences |
| [15-alias/](15-alias/) | Shell aliases — productivity shortcuts |
| [17/](17/) | Religious / personal research notes |
| [CA/](CA/) | Certificate Authority — how CAs work, trust chains |

---

## Quick Reference

### Seccomp (Kubernetes)
Restrict which Linux system calls a container can make:
```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault   # or Localhost (custom profile)
```

### SSH
```bash
# Generate a key pair
ssh-keygen -t ed25519 -C "your-comment"

# Copy public key to a server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server

# Connect using a specific key
ssh -i ~/.ssh/id_ed25519 user@server

# SSH config file shortcut (~/.ssh/config)
Host myserver
  HostName 192.168.1.10
  User ubuntu
  IdentityFile ~/.ssh/id_ed25519
```

### DNS / nslookup
```bash
# Lookup a hostname
nslookup google.com

# Lookup using a specific DNS server
nslookup google.com 8.8.8.8

# Reverse lookup
nslookup 8.8.8.8

# dig alternative (more detail)
dig google.com
dig +short google.com
```

### macOS Environment Variables
```bash
# Set temporarily (current session only)
export MY_VAR="value"

# Set permanently — add to ~/.zshrc or ~/.bash_profile
echo 'export MY_VAR="value"' >> ~/.zshrc
source ~/.zshrc
```

### SQL vs NoSQL Summary

| | SQL | NoSQL |
|-|-----|-------|
| Schema | Fixed, predefined | Flexible / schema-less |
| Scaling | Vertical | Horizontal |
| Transactions | ACID guaranteed | Eventual consistency (varies) |
| Examples | PostgreSQL, MySQL | MongoDB, DynamoDB, Cosmos DB |
| Best for | Relational data, complex queries | High-velocity, unstructured data |
