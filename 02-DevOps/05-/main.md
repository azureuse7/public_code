DefaultWorkingDirectory

- In Azure DevOps, System.DefaultWorkingDirectory is a predefined system variable used during pipeline execution to specify the local path on the build agent where the source code repository is downloaded (checked out).


System.DefaultWorkingDirectory points to:  <agent-root>/_work/<pipeline-id>/s


This is the directory where your pipeline repository (and possibly any other repositories specified via checkout) are downloaded during the checkout step.

/home/vsts/work/1/s
