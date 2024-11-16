Access to GitHub repositories thee are thee way. 

<img src="images/a.png">

#### GitHub app authentication
- After you install the GitHub App in your GitHub account or organization, your pipeline will run without using your personal GitHub identity. 
 
- Builds and GitHub status updates will be performed using the Azure Pipelines identity. 

- To use the GitHub App, install it in your GitHub organization or user account.

- After installation, the GitHub App will become Azure Pipelines' default method of authentication to GitHub (instead of OAuth) when pipelines are created for the repositories.



### How to configure.
https://www.youtube.com/watch?v=YZlaoNPzaxA

- I have created a new github and azure devops project.
There is no connection at present 

- Install the Github App --> Market place --> serach --> add
<img src="images/b.png">

- What access you want to give 
<img src="images/c.png">
- Now its taking me to Azure DevOps side
<img src="images/d.png">
- Now it wants to authorize
<img src="images/e.png">
- Go to started pipeline in Devops and create pipeline, save and run  

- Notice a build has started and its also created that pipeline in our gihub repo 
<img src="images/f.png">
- Notice The app is created in github
<img src="images/g.png">
- also created in Azure devops
<img src="images/h.png">




- Lets delete the service and let seee what happends 
<img src="images/11.png">


Now How would this be used in DevOps
,Each pipeline has .yml files that has a reference to one repo that contains all the templates for build and release. Like this:
```yaml
resources:  
   repositories:    
   - repository: templates      
     type: github    
     name: MyGitHubOrg/MyTemplatesRepo    
     ref: refs/heads/master    
     endpoint: MyGitHubOrg
stages:
   - template: build.yml@templates
     parameters:
        ...
```
- The main character in this story is the endpoint **MyGitHubOrg**. This is the name of a service connection created by the Azure Pipelines GitHub App mentioned above.

- When you install the Azure Pipelines app it will create the Service Connection for you. In whatever team project you supply during installation.

Once it’s installed and working for one Team Project in Azure DevOps you can share it with other projects so they can also use it. To do this go to that Service Connection in Azure DevOps and select Security. If you are not sure where this is it’s under Project Settings — Service Connections in Azure DevOps.


