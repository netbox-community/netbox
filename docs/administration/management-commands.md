# Management Commands

In addition to Django's built-in management commands, NetBox provides several commands of its own. These are run using `manage.py`:

```
cd /opt/netbox
source /opt/netbox/venv/bin/activate
python3 netbox/manage.py <command>
```

## populate_image_sizes

Image attachments cache the size of their file in the database so that list views do not need to query the storage backend for each image when rendered. Attachments created or updated on a recent NetBox release have this value populated automatically; those created on an earlier release do not, and will fall back to querying the storage backend until they are next saved.

This command populates the cached size for any image attachments that are missing it. Running it once after upgrading is recommended for deployments with many existing image attachments, particularly when using a remote storage backend (such as S3), where the per-image queries are most expensive.

```
python3 netbox/manage.py populate_image_sizes
```

This command is safe to run on a live system. It reads each file's size from the storage backend, so it may take some time to complete on a deployment with a large number of attachments; progress is reported as it runs. The command may also be run again safely: any attachments whose file could not be read (for example, due to a temporary storage outage) are left unchanged and retried on a subsequent run.
