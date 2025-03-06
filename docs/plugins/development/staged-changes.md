# Staged Changes

!!! danger "Deprecated Feature"
    This feature has been deprecated in NetBox v4.2 and will be removed in a future release. Please consider using the [netbox-branching plugin](https://github.com/netboxlabs/netbox-branching), which provides much more robust functionality.

NetBox provides a programmatic API to stage the creation, modification, and deletion of objects without actually committing those changes to the active database. This can be useful for performing a "dry run" of bulk operations, or preparing a set of changes for administrative approval, for example.

To begin staging changes, first create a [branch](../../models/extras/branch.md):

```python
from extras.models import Branch

branch1 = Branch.objects.create(name='branch1')
```

Then, activate the branch using the `checkout()` context manager and begin making your changes. This initiates a new database transaction.

```python
from extras.models import Branch
from netbox.staging import checkout

branch1 = Branch.objects.get(name='branch1')
with checkout(branch1):
    Site.objects.create(name='New Site', slug='new-site')
    # ...
```

Upon exiting the context, the database transaction is automatically rolled back and your changes recorded as [staged changes](../../models/extras/stagedchange.md). Re-entering a branch will trigger a new database transaction and automatically apply any staged changes associated with the branch.

To apply the changes within a branch, call the branch's `commit()` method:

```python
from extras.models import Branch

branch1 = Branch.objects.get(name='branch1')
branch1.commit()
```

Committing a branch is an all-or-none operation: Any exceptions will revert the entire set of changes. After successfully committing a branch, all its associated StagedChange objects are automatically deleted (however the branch itself will remain and can be reused).
