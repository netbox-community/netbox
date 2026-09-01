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

Populate the cached file size for image attachments that predate the `image_size` field. Running this once after upgrading is recommended for deployments with many existing attachments on a remote storage backend (such as S3). It is safe to run on a live system and may be re-run; any file that cannot be read is skipped and retried on the next run.

```
python3 netbox/manage.py populate_image_sizes
```

## rebuild_config_context_cache

Pre-render and cache the merged config context data for all devices and virtual machines. The [upgrade script](../installation/upgrading.md) runs this automatically, so it is not usually necessary to invoke it by hand. It is useful to complete an interrupted run, or (with `--force`) to repair the cache after a bulk write which bypassed NetBox's change handling (cache invalidation is driven by model signals, which a direct `queryset.update()` does not emit).

By default, only those objects whose cache is empty are rendered, so the command is safe to interrupt and re-run. This also means that a default run will not correct a cache which is populated but stale, as a write which bypassed cache invalidation leaves it: Pass `--force` to re-render every object regardless of its current cache. Either form may be run on a live system, as any object whose cache is empty falls back to rendering its config context on demand. See [Context Data](../features/context-data.md) for details.

```
python3 netbox/manage.py rebuild_config_context_cache [--force]
```

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

!!! warning "Deprecation Warning"
    The custom scripts functionality has been deprecated beginning in NetBox v4.7, and is scheduled for removal in NetBox v5.0. This command will be removed along with it.

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

## webhook_receiver

Start a simple HTTP listener that prints any requests it receives. This is a debugging aid for testing webhooks: point a webhook at the listener and inspect exactly what NetBox sends. It listens on port 9000 by default; pass `--port` to change it and `--no-headers` to suppress the request headers.

```
python3 netbox/manage.py webhook_receiver [--port PORT] [--no-headers]
```
