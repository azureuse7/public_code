# OAuth Authentication

OAuth is an authentication method that allows Azure DevOps to access your GitHub repositories on your behalf, without sharing your GitHub credentials directly.

## How It Works

1. **Initiate Connection**: In Azure DevOps, you create a new service connection to GitHub and select OAuth as the authentication method.
2. **Authorization Prompt**: You are redirected to GitHub to log in (if not already logged in) and authorize Azure DevOps.
3. **Grant Permissions**: You grant Azure DevOps the permissions it requests, such as repository read/write access.
4. **Token Exchange**: Azure DevOps receives an access token to interact with your GitHub repositories on your behalf.

To use OAuth, select **Choose a different connection** below the list of repositories while creating a pipeline. Then, select **Authorize** to sign into GitHub and authorize with OAuth.

An OAuth connection will be saved in your Azure DevOps project for later use and applied to the pipeline being created.

## Permissions Needed in GitHub

The required GitHub permissions depend on who owns the repository.

- **Repo in your personal GitHub account**: At least once, authenticate to GitHub with OAuth using your personal GitHub account credentials. This can be done in Azure DevOps project settings under **Pipelines > Service connections > New service connection > GitHub > Authorize**. Grant Azure Pipelines access to your repositories under "Permissions".

- **Repo in someone else's personal GitHub account**: At least once, the other person must authenticate to GitHub with OAuth using their personal GitHub account credentials. This can be done in Azure DevOps project settings under **Pipelines > Service connections > New service connection > GitHub > Authorize**. The other person must grant Azure Pipelines access to their repositories under "Permissions". You must be added as a collaborator in the repository's settings under "Collaborators". Accept the invitation to be a collaborator using the link that is emailed to you.

- **Repo in a GitHub organization that you own**: At least once, authenticate to GitHub with OAuth using your personal GitHub account credentials. This can be done in Azure DevOps project settings under **Pipelines > Service connections > New service connection > GitHub > Authorize**. Grant Azure Pipelines access to your organization under "Organization access". You must be added as a collaborator, or your team must be added, in the repository's settings under "Collaborators and teams".

- **Repo in a GitHub organization that someone else owns**: At least once, a GitHub organization owner must authenticate to GitHub with OAuth using their personal GitHub account credentials. This can be done in Azure DevOps project settings under **Pipelines > Service connections > New service connection > GitHub > Authorize**. The organization owner must grant Azure Pipelines access to the organization under "Organization access". You must be added as a collaborator, or your team must be added, in the repository's settings under "Collaborators and teams". Accept the invitation to be a collaborator using the link that is emailed to you.
