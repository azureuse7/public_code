# Linux: System Administration Reference

> Core Linux commands for managing services, logs, processes, and system resources. Examples use Ubuntu/Debian with `systemd`.

---

## Service Management with systemctl

List all services and check if apache2 is present:
```bash
systemctl --no-pager -t service -a | grep apache2
```

Enable a service to start on boot and start it immediately:
```bash
systemctl enable apache2 && systemctl start apache2
```

Check the running status of a service:
```bash
systemctl status apache2
```

Stop / restart a service:
```bash
systemctl stop apache2
systemctl restart apache2
```

---

## Log Management with journalctl

Stream live logs for a service (like `tail -f`):
```bash
journalctl -f -u apache2.service
```

View all logs for a service (no pager):
```bash
journalctl --no-pager -u apache2.service
```

Show logs since the last boot:
```bash
journalctl -b -u apache2.service
```

Show the last 50 lines:
```bash
journalctl -n 50 -u apache2.service
```

---

## Files in This Section

| File | Topic |
|------|-------|
| [README.md](README.md) | Service management, journalctl commands |
| [01-devnull.md](01-devnull.md) | `/dev/null` — suppressing output and discarding data |
