# Linux

**Check that service enabled by run:-->**.
systemctl --no-page -t service -a | grep apache2
 
**enable it and start-->:**
stemctl enable apache2 && systemctl start apache2

**Check that service works:-->**
systemctl status apache2

**logs-->**
journalctl --no-page -u apache2.service Note. -f key works with journalctl well as with tail



