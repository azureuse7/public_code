# Local connection to GitHub
To connect to GitHub with SSH from Windows, follow these steps:

- Open PowerShell

- Run the "ssh-keygen" command to create SSH keys

- Copy the value of the SSH public key

- Save the public key in your GitHub account settings

- Perform a Git clone operation using your repo’s SSH URL

# Create SSH Keys for GitHub

To start, store a public SSH key on GitHub. This is validated against a locally stored private key that Git uses to validate and establish a connection. GitHub SSH keys are created with the ssh-keygen tool that comes prepackaged with updated versions of Windows.

In Windows PowerShell, issue the following ssh-keygen command to create GitHub SSH keys:
```t
PS C:\github\ssh\example> ssh-keygen -o -t rsa -C "windows-ssh@mcnz.com"
```
You will be asked for an optional passphrase. It’s permissible to click enter and leave this blank.


Use the newest OpenSSH format

Leave blank

You will also be asked for a location to save the GitHub SSH keys on Windows. Again, just click enter to accept the default location, which is the .ssh folder under the user’s home directory.

The Windows GitHub SSH keys live in the .ssh folder under the current user’s home directory. The following directory listing under the .ssh folder of a user named Cameron shows the two files created by the ssh-keygen tool:



PS C:\Users\Cameron\.ssh> dir
LastWriteTime      Name
-------------      ----
1/1/2022           id_rsa
1/1/2022           id_rsa.pub

# GitHub SSH config

Open the SSH public key in a text editor such as Notepad++, perform a Select All, and copy the key.

GitHub SSH KeyGen Key Git
Copy the public GitHub SSH key and store this value as a registered

# SSH key in your GitHub account.

With the SSH key copied, log into GitHub, navigate to your account settings, and paste the public key as a new SSH key.

GitHub SSH Windows
To obtain a secure, GitHub SSH Windows connection, you must register the public key in your online account settings.


# Azure-DevOps connection to GitHub repositories
Build GitHub repositories - Azure Pipelines 

To create a PAT, visit Personal access tokens in your GitHub settings. The required permissions are repo, admin:repo_hook, read:user, and user:email. These are the same permissions required when using OAuth above. Copy the generated PAT to the clipboard and paste it into a new GitHub service connection in your Azure DevOps project settings. For future recall, name the service connection after your GitHub username. It will be available in your Azure DevOps project for later use when creating pipelines.


Azure-DevOps connection to Azure 
[Azure DevOps | Creating a Service connection with Azure ]
# https://www.youtube.com/watch?v=06wxMtSt_0g&t=367s

# Service connection 
- What is service connection, 
"service connection" refers to a secure and managed way to connect to external services or resources from Azure Pipelines, Azure DevOps, or Azure Automation to azure basically its a connection.

To create a service conection you need the below

- subscpition id 
- subscpition name
- authication --> select service connection
- service principle id
- service principle key
- tentant id 


# authicate method used by Service connection we use Service Principle 
- what is service principle

It will use the app ID and aap secret to connect to azure subscpition 


# create an app-registration
- app regsitration needs api permssions check them 
- Secrets --> this is where we generate our secrets --> create a new secret 
- copy the value and this is the "service principle key". SO in the service connection copy the secret into service principle key
- service principle id = application(client)id 

One very important thing,  the application must have correct roles example owners on the rescource its going to create rescouce 




To authenticate Azure DevOps with GitHub, you typically use a combination of service connections and service principals. Here's a general guide on how to set this up:

Create a GitHub Personal Access Token:

Go to your GitHub account settings.
Navigate to "Developer settings" > "Personal access tokens."
Generate a new token with appropriate permissions, such as repo access.
Copy the generated token. You'll need this for authentication.
Create a GitHub Service Connection in Azure DevOps:

In your Azure DevOps project, go to "Project settings" > "Service connections."
Click on "New service connection" and select "GitHub."
Provide a connection name and paste the personal access token you generated.
Click "OK" to create the service connection.
Create a Service Principal (Optional):

If you need to deploy resources from Azure DevOps to Azure, you might want to create a service principal in Azure.
Go to the Azure portal and create a new Azure AD application registration.
Assign appropriate roles to this service principal, such as contributor on the resource group where you're deploying resources.
Authorize GitHub OAuth App (Optional):

If you're integrating GitHub with Azure Pipelines, you might need to authorize a GitHub OAuth app.
In GitHub, go to "Settings" > "Developer settings" > "OAuth Apps."
Register a new OAuth app and provide callback URLs as needed.
Use the client ID and client secret generated from this OAuth app to configure Azure Pipelines.
Use Service Connections in Pipelines:

In your Azure Pipelines YAML or classic editor, specify the GitHub service connection you created to access GitHub repositories.
For example, in YAML pipelines, you might use the github service connection in your repository section.
With these configurations, your Azure DevOps pipelines or other services can authenticate with GitHub using the provided personal access token or OAuth app credentials. Make sure to manage these credentials securely and follow best practices for access control and permission


