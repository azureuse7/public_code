# Local (Laptop) Connection to GitHub

To connect to GitHub with SSH from Windows, follow these steps:

1. Open PowerShell.
2. Run the `ssh-keygen` command to create SSH keys:

   ```bash
   ssh-keygen -o -t rsa -C "windows-ssh@mcnz.com"
   ```

3. Copy the value of the SSH public key. This is validated against a locally stored private key that Git uses to validate and establish a connection.
4. Save the public key in your GitHub account settings.
5. Perform a `git clone` operation using your repository's SSH URL.
