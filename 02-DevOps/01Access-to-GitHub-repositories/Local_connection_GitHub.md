# Local (laptop) connection to GitHub
To connect to GitHub with SSH from Windows, follow these steps:

- Open PowerShell
- Run the "ssh-keygen" command to create SSH keys (ssh-keygen -o -t rsa -C "windows-ssh@mcnz.com")
- Copy the value of the SSH public key ( This is validated against a locally stored private key that Git uses to validate and establish a connection.)
- Save the public key in your GitHub account settings
- Perform a Git clone operation using your repo’s SSH URL


