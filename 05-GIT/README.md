# Git Version Control

> Essential Git commands for everyday development — branching, remotes, rebasing, resetting, tagging, and comparing branches.

---

## Remote Operations

Get the remote URL:
```bash
git config --get remote.origin.url
```

Remove a remote:
```bash
git remote rm origin
```

Update local master from origin:
```bash
git pull origin master:master
```

---

## Branching

Create and switch to a new branch:
```bash
git checkout -b feature/my-feature
# or (Git 2.23+)
git switch -c feature/my-feature
```

Clone a specific branch:
```bash
git clone -b <branch> <remote_repo>
```

List all branches (including remote):
```bash
git branch -a
```

---

## Syncing and Rebasing

Fetch latest changes without merging:
```bash
git fetch
```

Rebase your branch onto origin/master:
```bash
git rebase origin/master
```

---

## Undoing Changes

Reset to a specific commit (destructive — discards local changes):
```bash
git reset --hard <commit-hash>
```

Undo the last commit but keep changes staged:
```bash
git reset --soft HEAD~1
```

---

## Tags

Create a tag:
```bash
git tag v1.0.0
git tag -a v1.0.0 -m "Release 1.0.0"
```

Push tags to remote:
```bash
git push origin --tags
```

---

## Branch Comparison

Two-dot diff — changes reachable from B but not A:
```bash
git diff main..feature
```

Three-dot diff — changes on feature since it diverged from main:
```bash
git diff main...feature
```

Get the SHA of the current branch HEAD:
```bash
git rev-parse HEAD
```

---

## Common Workflow

```bash
git fetch                          # get latest remote state
git checkout -b feature/my-work    # create feature branch
# ... make changes ...
git add -p                         # stage interactively
git commit -m "describe the why"
git rebase origin/main             # rebase before PR
git push origin feature/my-work
```
