# git Cheat Sheet

This cheat sheet serves as a convenient reference for NetBox contributors who already somewhat familiar with using git. For a general introduction to the tooling and workflows involved, please see GitHub's guide [Getting started with git](https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git).

## Common Operations

### Clone a Repo

This copies a remote git repository (e.g. from GitHub) to your local workstation. It will create a new directory bearing the repo's name in the current path.

``` title="Command"
git clone https://github.com/$org-name/$repo-name
```

``` title="Example"
$ git clone https://github.com/netbox-community/netbox
Cloning into 'netbox'...
remote: Enumerating objects: 95112, done.
remote: Counting objects: 100% (682/682), done.
remote: Compressing objects: 100% (246/246), done.
remote: Total 95112 (delta 448), reused 637 (delta 436), pack-reused 94430
Receiving objects: 100% (95112/95112), 60.40 MiB | 45.82 MiB/s, done.
Resolving deltas: 100% (74979/74979), done.
```

### Pull New Commits

To update your local branch with any recent upstream commits, run `git pull`.

``` title="Command"
git pull
```

``` title="Example"
$ git pull
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), done.
From https://github.com/netbox-community/netbox
   28bc76695..e0741cc9a  develop    -> origin/develop
Updating 28bc76695..e0741cc9a
Fast-forward
 docs/release-notes/version-3.3.md | 1 +
 netbox/netbox/settings.py         | 1 +
 2 files changed, 2 insertions(+)
```

### List Branches

`git branch` lists all local branches. Appending `-a` to this command will list both local (green) and remote (red) branches.

``` title="Command"
git branch -a
```

``` title="Example"
$ git branch -a
* develop
  remotes/origin/10170-changelog
  remotes/origin/HEAD -> origin/develop
  remotes/origin/develop
  remotes/origin/feature
  remotes/origin/master
```

### Switch Branches

To switch to a different branch, use the `checkout` command.

``` title="Command"
git checkout $branchname
```

``` title="Example"
$ git checkout feature
Branch 'feature' set up to track remote branch 'feature' from 'origin'.
Switched to a new branch 'feature'
```

### Create a New Branch

Use the `-b` argument with `checkout` to create a new _local_ branch from the current branch.

``` title="Command"
git checkout -b $newbranch
```

``` title="Example"
$ git checkout -b 123-fix-foo
Switched to a new branch '123-fix-foo'
```

### Rename a Branch

To rename the current branch, use the `git branch` command with the `-m` argument (for "modify").

``` title="Command"
git branch -m $newname
```

``` title="Example"
$ git branch -m jstretch-testing
$ git branch
  develop
  feature
* jstretch-testing
```

### Merge a Branch

To merge one branch into another, use the `git merge` command. Start by checking out the _destination_ branch, and merge the _source_ branch into it.

``` title="Command"
git merge $sourcebranch
```

``` title="Example"
$ git checkout testing 
Switched to branch 'testing'
Your branch is up to date with 'origin/testing'.
$ git merge branch2 
Updating 9a12b5b5f..8ee42390b
Fast-forward
 newfile.py | 0
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 newfile.py
```

!!! warning "Avoid Merging Remote Branches"
    You generally want to avoid merging branches that exist on the remote (upstream) repository, namely `main` and `feature`: Merges into these branches should be done via a pull request on GitHub. Only merge branches when it is necessary to consolidate work you've done locally.

### Show Pending Changes

After making changes to files in the repo, `git status` will display a summary of created, modified, and deleted files.

``` title="Command"
git status
```

``` title="Example"
$ git status
On branch 123-fix-foo
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

	modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)

	foo.py

no changes added to commit (use "git add" and/or "git commit -a")
```

### Stage Changed Files

Before creating a new commit, modified files must be staged. This is typically done with the `git add` command. You can specify a particular path, or just append `-A` to automatically staged _all_ changed files within the current directory. Run `git status` again to verify what files have been staged.

``` title="Command"
git add -A
```

``` title="Example"
$ git add -A
$ git status
On branch 123-fix-foo
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

	modified:   README.md
	new file:   foo.py

```

### Review Staged Files

It's a good idea to thoroughly review all staged changes immediately prior to creating a new commit. This can be done using the `git diff` command. Appending the `--staged` argument will show staged changes; omitting it will show changes that have not yet been staged.

``` title="Command"
git diff --staged
```

``` title="Example"
$ git diff --staged
diff --git a/README.md b/README.md
index 93e125079..4344fb514 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,8 @@
+
+Added some lines here
+and here
+and here too
+
 <div align="center">
   <img src="https://raw.githubusercontent.com/netbox-community/netbox/main/docs/netbox_logo.svg" width="400" alt="NetBox logo" />
 </div>
diff --git a/foo.py b/foo.py
new file mode 100644
index 000000000..e69de29bb
```

### Create a New Commit

The `git commit` command records your changes to the current branch. Specify a commit message with the `-m` argument. (If omitted, a file editor will be opened to provide a message.

``` title="Command"
git commit -m "Fixes #123: Fixed the thing that was broken"
```

``` title="Example"
$ git commit -m "Fixes #123: Fixed the thing that was broken"
[123-fix-foo 9a12b5b5f] Fixes #123: Fixed the thing that was broken
 2 files changed, 5 insertions(+)
 create mode 100644 foo.py
```

!!! tip "Automatically Closing Issues"
    GitHub will [automatically close](https://github.blog/2013-01-22-closing-issues-via-commit-messages/) any issues referenced in a commit message by `Fixes:` or `Closes:` when the commit is merged into the repository's default branch. Contributors are strongly encouraged to follow this convention when forming commit messages. (Use "Closes" for feature requests and "Fixes" for bugs.)

### Push a Commit Upstream

Once you've made a commit locally, it needs to be pushed upstream to the _remote_ repository (typically called "origin"). This is done with the `git push` command. If this is a new branch that doesn't yet exist on the remote repository, you'll need to set the upstream for it when pushing.

``` title="Command"
git push -u origin $branchname
```

``` title="Example"
$ git push -u origin testing
Counting objects: 3, done.
Delta compression using up to 16 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 377 bytes | 377.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
remote: 
remote: Create a pull request for 'testing' on GitHub by visiting:
remote:      https://github.com/netbox-community/netbox/pull/new/testing
remote: 
To https://github.com/netbox-community/netbox
 * [new branch]          testing -> testing
Branch 'testing' set up to track remote branch 'testing' from 'origin'.
```

!!! tip
    You can apply the following git configuration to automatically set the upstream for all new branches. This obviates the need to specify `-u origin`.
    
    ```
    git config --global push.default current
    ```

## The GitHub CLI Client

GitHub provides a [free CLI client](https://cli.github.com/) to simplify many aspects of interacting with GitHub repositories. Note that this utility is separate from `git`, and must be [installed separately](https://github.com/cli/cli#installation).

This guide provides some examples of common operations, but be sure to check out the [GitHub CLI manual](https://cli.github.com/manual/) for a complete accounting of available commands.

### List Open Pull Requests

``` title="Command"
gh pr list
```

``` title="Example"
$ gh pr list

Showing 3 of 3 open pull requests in netbox-community/netbox

#10223  #7503 API Bulk-Create of Devices does not check Rack-Space  7503-bulkdevice             about 17 hours ago
#9716   Closes #9599: Add cursor pagination mode                    lyuyangh:cursor-pagination  about 1 month ago
#9498   Adds replication and adoption for module import             sleepinggenius2:issue_9361  about 2 months ago
```

### Check Out a PR

This command will automatically check out the remote branch associated with an open pull request.

``` title="Command"
gh pr checkout $number
```

``` title="Example"
$ gh pr checkout 10223
Branch '7503-bulkdevice' set up to track remote branch '7503-bulkdevice' from 'origin'.
Switched to a new branch '7503-bulkdevice'
```

## Fixing Mistakes

### Modify the Previous Commit

Sometimes you'll find that you've overlooked a necessary change and need to commit again. If you haven't pushed your most recent commit and just need to make a small tweak or two, you can _amend_ your most recent commit instead of creating a new one.

First, stage the desired files with `git add` and verify the changes, the issue the `git commit` command with the `--amend` argument. You can also append the `--no-edit` argument if you would like to keep the previous commit message.

``` title="Command"
git commit --amend --no-edit
```

``` title="Example"
$ git add -A
$ git diff --staged
$ git commit --amend --no-edit
[testing 239b16921] Added a new file
 Date: Fri Aug 26 16:30:05 2022 -0400
 2 files changed, 1 insertion(+)
 create mode 100644 newfile.py
```

!!! danger "Don't Amend After Pushing"
    Never amend a commit you've already pushed upstream unless you're **certain** no one else is working on the same branch. Force-pushing will overwrite the change history, which will break any commits from other contributors. When in doubt, create a new commit instead.

### Undo the Last Commit

The `git reset` command can be used to undo the most recent commit. (`HEAD~` is equivalent to `HEAD~1` and references the commit prior to the current HEAD.) After making and staging your changes, commit using `-c ORIG_HEAD` to replace the erroneous commit.

``` title="Command"
git reset HEAD~
```

``` title="Example"
$ git add -A
$ git commit -m "Erroneous commit"
[testing 09ce06736] Erroneous commit
 Date: Mon Aug 29 15:20:04 2022 -0400
 1 file changed, 1 insertion(+)
 create mode 100644 BADCHANGE
$ git reset HEAD~
$ rm BADFILE
$ git add -A
$ git commit -m "Fixed commit"
[testing c585709f3] Fixed commit
 Date: Mon Aug 29 15:22:38 2022 -0400
 1 file changed, 65 insertions(+), 20 deletions(-)
```

!!! danger "Don't Reset After Pushing"
    Resetting only works until you've pushed your local changes upstream. If you've already pushed upstream, use `git revert` instead. This will create a _new_ commit that reverts the erroneous one, but ensures that the git history remains intact.

### Rebase from Upstream

If a change has been pushed to the upstream branch since you most recently pulled it, attempting to push a new local commit will fail:

```
$ git push
To https://github.com/netbox-community/netbox.git
 ! [rejected]            develop -> develop (fetch first)
error: failed to push some refs to 'https://github.com/netbox-community/netbox.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first integrate the remote changes
hint: (e.g., 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

To resolve this, first fetch the upstream branch to update your local copy, and then [rebase](https://git-scm.com/book/en/v2/Git-Branching-Rebasing) your local branch to include the new changes. Once the rebase has completed, you can push your local commits upstream.

``` title="Commands"
git fetch
git rebase origin/$branchname
```

``` title="Example"
$ git fetch
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), done.
From https://github.com/netbox-community/netbox
   815b2d8a2..8c35ebbb7  develop    -> origin/develop
$ git rebase origin/develop
First, rewinding head to replay your work on top of it...
Applying: Further tweaks to the PR template
Applying: Changelog for #10176, #10217
$ git push
Counting objects: 9, done.
Delta compression using up to 16 threads.
Compressing objects: 100% (9/9), done.
Writing objects: 100% (9/9), 1.02 KiB | 1.02 MiB/s, done.
Total 9 (delta 6), reused 0 (delta 0)
remote: Resolving deltas: 100% (6/6), completed with 5 local objects.
To https://github.com/netbox-community/netbox.git
   8c35ebbb7..ada745324  develop -> develop
```
