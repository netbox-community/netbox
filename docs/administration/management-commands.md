# Management Commands

In addition to Django's built-in management commands, NetBox provides several commands of its own. These are run using `manage.py`:

```
cd /opt/netbox
source /opt/netbox/venv/bin/activate
python3 netbox/manage.py <command>
```

Run any command with `--help` to see its full set of arguments.

## calculate_cached_counts

Force a recalculation of all cached counter fields (for example, the device count shown on a site). NetBox keeps these counters current automatically; this command is useful to repair them if they have drifted.

```
python3 netbox/manage.py calculate_cached_counts
```

## nbshell

Start the Django shell with all NetBox models already imported. See [NetBox Shell](./netbox-shell.md) for details.

```
python3 netbox/manage.py nbshell
```

## populate_image_sizes

Image attachments cache the size of their file in the database so that list views do not need to query the storage backend for each image when rendered. Attachments created or updated on a recent NetBox release have this value populated automatically; those created on an earlier release do not, and will fall back to querying the storage backend until they are next saved.

This command populates the cached size for any image attachments that are missing it. Running it once after upgrading is recommended for deployments with many existing image attachments, particularly when using a remote storage backend (such as S3), where the per-image queries are most expensive.

```
python3 netbox/manage.py populate_image_sizes
```

This command is safe to run on a live system. It reads each file's size from the storage backend, so it may take some time to complete on a deployment with a large number of attachments; progress is reported as it runs. The command may also be run again safely: any attachments whose file could not be read (for example, due to a temporary storage outage) are left unchanged and retried on a subsequent run.

## rebuild_prefixes

Rebuild the IPAM prefix hierarchy, recalculating the depth and child counts for all prefixes.

```
python3 netbox/manage.py rebuild_prefixes
```

## reindex

Reindex objects for the search backend. Pass one or more apps or models to reindex a subset; with no arguments, all models are reindexed. See [Removing a Plugin](../plugins/removal.md) for a related use.

```
python3 netbox/manage.py reindex [app_label[.ModelName] ...]
```

## renaturalize

Recalculate natural ordering values for the affected models. Pass one or more `app_label.ModelName` arguments to limit the scope; with no arguments, all models with natural ordering fields are processed.

```
python3 netbox/manage.py renaturalize [app_label.ModelName ...]
```

## runscript

Run a [custom script](../customization/custom-scripts.md) from the command line, outside the web UI or API.

```
python3 netbox/manage.py runscript <module.ScriptName>
```

## rqworker

Start a background task worker to process queued jobs (provided by django-rq). At least one worker must be running for background tasks such as report and script execution, webhooks, and synchronization to be processed.

```
python3 netbox/manage.py rqworker
```

## syncdatasource

Synchronize a data source from its remote upstream. Pass one or more data source names, or `--all` to synchronize every data source.

```
python3 netbox/manage.py syncdatasource <name> [<name> ...]
python3 netbox/manage.py syncdatasource --all
```

## trace_paths

Generate any missing cable paths among all cable termination objects. This is useful after a bulk import of cabling, or to repair paths that were not generated automatically.

```
python3 netbox/manage.py trace_paths
```
