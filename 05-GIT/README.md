https://devconnected.com/create-git-branch/#:~:text=The%20easiest%20way%20to%20create,branch%20you%20want%20to%20create.&text=To%20achieve%20that%2C%20you%20will,feature%E2%80%9D%20as%20the%20branch%20name.

```t
# Get the remote URL                          
git config --get remote.origin.url

# To remove a remote repository                   
git remote rm origin

# Update your local master with the origin/master
git pull origin master:master

# Now your origin/masteris up to date, so you can rebase or merge your local branch with these changes.
git fetch

# And your develop branch will be up:          
git rebase origin/master

# To go back to pervious commit                 
git reset --hard 7d2838af6180183c05969e0d1a18b4fed53682c7 (old reference)

# To clone a branch:                         
git clone -b <branch> <remote_repo>

# checkout a new branch:                       
git checkout -b <branch>

# get local branches of your repo.                
git branch

# To push Tags
Make changes
git add .
git commit -m "w"
git tag v.02 
git push --tags


# To push Changes
git add .
git commit -m "w"
git push

# To find the differnce 
$ git diff branch1..branch2
$ git diff master..feature

#Comparing two branches using triple dot syntax
$ git diff branch1...branch2
#Using “git diff” with three dots compares the top of the right branch (the HEAD) with the common ancestor of the two branches.
# https://devconnected.com/how-to-compare-two-git-branches/

# git rev-parse is an ancillary plumbing command primarily used for manipulation.
git rev-parse --symbolic-full-name HEAD
# output: refs/heads/cazr6855


# To display only the name of the current branch you're on:
git rev-parse --abbrev-ref HEAD
# Output:cazr6855



``` 
https://devconnected.com/how-to-compare-two-git-branches/