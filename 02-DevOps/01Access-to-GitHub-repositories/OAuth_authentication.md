# OAuth authentication


###  How It Works
1) **Initiate** **Connection**: In Azure DevOps, you create a new service connection to GitHub and select OAuth as the authentication method.
2) **Authorization Prompt**: You're redirected to GitHub to log in (if not already logged in) and authorize Azure DevOps.
3) **Grant Permissions**: You grant Azure DevOps the permissions it requests, such as repository read/write access.
4) **Token Exchange**: Azure DevOps receives an access token to interact with your GitHub repositories on your behalf.


To use OAuth, select Choose a different connection below the list of repositories while creating a pipeline. Then, select Authorize to sign into GitHub and authorize with OAuth. 

An OAuth connection will be saved in your Azure DevOps project for later use, and used in the pipeline being created.

### Permissions needed in GitHub


If the repo is in your personal GitHub account, at least once, authenticate to GitHub with OAuth using your personal GitHub account credentials. 

This can be done in Azure DevOps project settings under Pipelines > Service connections > New service connection > GitHub > Authorize. Grant Azure Pipelines access to your repositories under "Permissions" here.

If the repo is in someone else's personal GitHub account, at least once, the other person must authenticate to GitHub with OAuth using their personal GitHub account credentials. This can be done in Azure DevOps project settings under Pipelines > Service connections > New service connection > GitHub > Authorize. The other person must grant Azure Pipelines access to their repositories under "Permissions" here. You must be added as a collaborator in the repository's settings under "Collaborators". Accept the invitation to be a collaborator using the link that is emailed to you.

If the repo is in a GitHub organization that you own, at least once, authenticate to GitHub with OAuth using your personal GitHub account credentials. This can be done in Azure DevOps project settings under Pipelines > Service connections > New service connection > GitHub > Authorize. Grant Azure Pipelines access to your organization under "Organization access" here. You must be added as a collaborator, or your team must be added, in the repository's settings under "Collaborators and teams".

If the repo is in a GitHub organization that someone else owns, at least once, a GitHub organization owner must authenticate to GitHub with OAuth using their personal GitHub account credentials. This can be done in Azure DevOps project settings under Pipelines > Service connections > New service connection > GitHub > Authorize. The organization owner must grant Azure Pipelines access to the organization under "Organization access" here. You must be added as a collaborator, or your team must be added, in the repository's settings under "Collaborators and teams". Accept the invitation to be a collaborator using the link that is emailed to you.