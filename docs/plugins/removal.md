# Removing a Plugin

!!! warning
    The instructions below detail the general process for removing a NetBox plugin. However, each plugin is different and may require additional tasks or modifications to the steps below. Always consult the documentation for a specific plugin **before** attempting to remove it.

## Disable the Plugin

Disable the plugin by removing it from the `PLUGINS` list in `configuration.py`.

## Remove its Configuration

Delete the plugin's entry (if any) in the `PLUGINS_CONFIG` dictionary in `configuration.py`.

!!! tip
    If there's a chance you may reinstall the plugin, consider commenting out any configuration parameters instead of deleting them.

## Re-index Search Entries

Run the `reindex` management command to reindex the global search engine. This will remove any stale entries pertaining to objects provided by the plugin.

```no-highlight
$ cd /opt/netbox/netbox/
$ source /opt/netbox/venv/bin/activate
(venv) $ python3 manage.py reindex
```

## Uninstall its Python Package

Use `pip` to remove the installed plugin:

```no-highlight
$ source /opt/netbox/venv/bin/activate
(venv) $ pip uninstall <package>
```

## Restart WSGI Service

Restart the WSGI service:

```no-highlight
# sudo systemctl restart netbox
```

## Drop Database Tables

!!! note
    This step is necessary only for plugins which have created one or more database tables (generally through the introduction of new models). Check your plugin's documentation if unsure.

Enter the PostgreSQL database shell (`manage.py dbshell`) to determine if the plugin has created any SQL tables. Substitute `pluginname` in the example below for the name of the plugin being removed. (You can also run the `\dt` command without a pattern to list _all_ tables.)

```no-highlight
netbox=> \dt pluginname_*
                   List of relations
                   List of relations
 Schema |       Name     | Type  | Owner
--------+----------------+-------+--------
 public | pluginname_foo | table | netbox
 public | pluginname_bar | table | netbox
(2 rows)
```

!!! warning
    Exercise extreme caution when removing tables. Users are strongly encouraged to perform a backup of their database immediately before taking these actions.

Drop each of the listed tables to remove it from the database:

```no-highlight
netbox=> DROP TABLE pluginname_foo;
DROP TABLE
netbox=> DROP TABLE pluginname_bar;
DROP TABLE
```

### Remove the Django Migration Records

After removing the tables created by a plugin, the migrations that created the tables need to be removed from Django's migration history as well. This is necessary to make it possible to reinstall the plugin at a later time. If the migration history were left in place, Django would skip all migrations that were executed in the course of a previous installation, which would cause the plugin to fail after reinstallation.

```no-highlight
netbox=> SELECT * FROM django_migrations WHERE app='pluginname';
 id  |    app     |          name          |            applied
-----+------------+------------------------+-------------------------------
 492 | pluginname | 0001_initial           | 2023-12-21 11:59:59.325995+00
 493 | pluginname | 0002_add_foo           | 2023-12-21 11:59:59.330026+00
netbox=> DELETE FROM django_migrations WHERE app='pluginname';
```

!!! warning
    Exercise extreme caution when altering Django system tables. Users are strongly encouraged to perform a backup of their database immediately before taking these actions.

## Clean Up Content Types and Permissions

After removing a plugin and its database tables, you may find that object type references (`ContentTypes`) created by the plugin still appear in the permissions management section (e.g., when editing permissions in the NetBox UI).
This happens because the `django_content_type` table retains entries for the models that the plugin registered with Django.

!!! warning
    Please use caution when removing `ContentTypes`. It is strongly recommended to **back up your database** before making these changes.

**Identify Stale Content Types:**

Open the Django shell to inspect lingering `ContentType` entries related to the removed plugin.
Typically, the Content Type's `app_label` matches the plugin’s name.


```no-highlight
$ cd /opt/netbox/
$ source /opt/netbox/venv/bin/activate
(venv) $ python3 netbox/manage.py nbshell
```

Then, in the shell:

```no-highlight
from django.contrib.contenttypes.models import ContentType
# Replace 'pluginname' with your plugin's actual name
stale_types = ContentType.objects.filter(app_label="pluginname")
for ct in stale_types:
    print(ct)
### ^^^ These will be removed, make sure its ok
```

!!! warning
    Review the output carefully and confirm that each listed Content Type is related to the plugin you removed.

**Remove Stale Content Types and Related Permissions:**

Next, check for any permissions associated with these Content Types:

```no-highlight
from django.contrib.auth.models import Permission
for ct in stale_types:
   perms = Permission.objects.filter(content_type=ct)
   print(list(perms))
```

If there are related Permissions, you can remove them safely:

```no-highlight
for ct in stale_types:
   Permission.objects.filter(content_type=ct).delete()
```

After removing any related permissions, delete the Content Type entries:

```no-highlight
stale_types.delete()
```

**Restart NetBox:**

After making these changes, restart the NetBox service to ensure all changes are reflected.

```no-highlight
sudo systemctl restart netbox
```
