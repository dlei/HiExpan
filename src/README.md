Source codes are put under this folder.

For each source code, please add the author and description information in the header for better maintenance.

## Workflow (and solution for syncing with server)

We first modify the code locally. After debugging, we make a commit locally and push to the remote repo
(the one hosted on GitHub).

**We ONLY make and push commit to remote repo locally.**

We can upload our local code to server via Cyberduck or IDE file upload features, and run the code on server.

To sync with git remote repo. We first discard all changes on server side using following command:

```
$ git stash -u
```

Then, we can make a pull request via:

```
$ git pull
```

In such way, there will be no "double-add" merge conflict.

**We ONLY pull commits from remote repo on server.**

The drawback of this solution is that we cannot change code directly on server and easily sync with remote repo.