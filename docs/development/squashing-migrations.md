# Squashing Database Schema Migrations

## What are Squashed Migrations?

The Django framework on which NetBox is built utilizes [migration files](https://docs.djangoproject.com/en/stable/topics/migrations/) to keep track of changes to the PostgreSQL database schema. Each time a model is altered, the resulting schema change is captured in a migration file, which can then be applied to effect the new schema.

As changes are made over time, more and more migration files are created. Although not necessarily problematic, it can be beneficial to merge and compress these files occasionally to reduce the total number of migrations that need to be applied upon installation of NetBox. This merging process is called _squashing_ in Django vernacular, and results in two parallel migration paths: individual and squashed.

Below is an example showing both individual and squashed migration files within an app:

| Individual | Squashed |
|------------|----------|
| 0001_initial       | 0001_initial_squashed_0004_add_field |
| 0002_alter_field   |                   .                  |
| 0003_remove_field  |                   .                  |
| 0004_add_field     |                   .                  |
| 0005_another_field | 0005_another_field                   |

In the example above, a new installation can leverage the squashed migrations to apply only two migrations:

* `0001_initial_squashed_0004_add_field`
* `0005_another_field`

This is because the squash file contains all of the operations performed by files `0001` through `0004`.

However, an existing installation that has already applied some of the individual migrations contained within the squash file must continue applying individual migrations. For instance, an installation which currently has up to `0002_alter_field` applied must apply the following migrations to become current:

* `0003_remove_field`
* `0004_add_field`
* `0005_another_field`

Squashed migrations are opportunistic: They are used only if applicable to the current environment. Django will fall back to using individual migrations if the squashed migrations do not agree with the current database schema at any point.

## Squashing Migrations

During every minor (i.e. 2.x) release, migrations should be squashed to help simplify the migration process for new installations. The process below describes how to squash migrations efficiently and with minimal room for error.

### 1. Create a New Branch

Create a new branch off of the `develop-2.x` branch. (Migrations should be squashed _only_ in preparation for a new minor release.)

```
git checkout -B squash-migrations
```

### 2. Delete Existing Squash Files

Delete the most recent squash file within each NetBox app. This allows us to extend squash files where the opportunity exists. For example, we might be able to replace `0005_to_0008` with `0005_to_0011`.

### 3. Generate the Current Migration Plan

Use Django's `showmigrations` utility to display the order in which all migrations would be applied for a new installation.

```
manage.py showmigrations --plan
```

From the resulting output, delete all lines which reference an external migration. Any migrations imposed by Django itself on an external package are not relevant.

### 4. Create Squash Files

Begin iterating through the migration plan, looking for successive sets of migrations within an app. These are candidates for squashing. For example:

```
[X]  extras.0014_configcontexts
[X]  extras.0015_remove_useraction
[X]  extras.0016_exporttemplate_add_cable
[X]  extras.0017_exporttemplate_mime_type_length
[ ]  extras.0018_exporttemplate_add_jinja2
[ ]  extras.0019_tag_taggeditem
[X]  dcim.0062_interface_mtu
[X]  dcim.0063_device_local_context_data
[X]  dcim.0064_remove_platform_rpc_client
[ ]  dcim.0065_front_rear_ports
[X]  circuits.0001_initial_squashed_0010_circuit_status
[ ]  dcim.0066_cables
...
```

Migrations `0014` through `0019` in `extras` can be squashed, as can migrations `0062` through `0065` in `dcim`. Migration `0066` cannot be included in the same squash file, because the `circuits` migration must be applied before it. (Note that whether or not each migration is currently applied to the database does not matter.)

Squash files are created using Django's `squashmigrations` utility:

```
manage.py squashmigrations <app> <start> <end>
```

For example, our first step in the example would be to run `manage.py squashmigrations extras 0014 0019`.

!!! note
    Specifying a migration file's numeric index is enough to uniquely identify it within an app. There is no need to specify the full filename.

This will create a new squash file within the app's `migrations` directory, named as a concatenation of its beginning and ending migration. Some manual editing is necessary for each new squash file for housekeeping purposes:

* Remove the "automatically generated" comment at top (to indicate that a human has reviewed the file).
* Reorder `import` statements as necessary per PEP8.
* It may be necessary to copy over custom functions from the original migration files (this will be indicated by a comment near the top of the squash file). It is safe to remove any functions that exist solely to accomodate reverse migrations (which we no longer support).

Repeat this process for each candidate set of migrations until you reach the end of the migration plan.

### 5. Check for Missing Migrations

If everything went well, at this point we should have a completed squashed path. Perform a dry run to check for any missing migrations:

```
manage.py migrate --dry-run
```

### 5. Run Migrations

Next, we'll apply the entire migration path to an empty database. Begin by dropping and creating your development database.

!!! warning
    Obviously, first back up any data you don't want to lose.

```
sudo -u postgres psql -c 'drop database netbox'
sudo -u postgres psql -c 'create database netbox'
```

Apply the migrations with the `migrate` management command. It is not necessary to specify a particular migration path; Django will detect and use the squashed migrations automatically. You can verify the exact migrations being applied by enabling verboes output with `-v 2`.

```
manage.py migrate -v 2
```

### 6. Commit the New Migrations

If everything is successful to this point, commit your changes to the `squash-migrations` branch.

### 7. Validate Resulting Schema

To ensure our new squashed migrations do not result in a deviation from the original schema, we'll compare the two. With the new migration file safely commit, check out the `develop-2.x` branch, which still contains only the individual migrations.

```
git checkout develop-2.x
```

Temporarily install the [django-extensions](https://django-extensions.readthedocs.io/) package, which provides the `sqldiff utility`:

```
pip install django-extensions
```

Also add `django_extensions` to `INSTALLED_APPS` in `netbox/netbox/settings.py`.

At this point, our database schema has been defined by using the squashed migrations. We can run `sqldiff` to see if it differs any from what the current (non-squashed) migrations would generate. `sqldiff` accepts a list of apps against which to run:

```
manage.py sqldiff circuits dcim extras ipam secrets tenancy users virtualization
```

It is safe to ignore errors indicating an "unknown database type" for the following fields:

* `dcim_interface.mac_address`
* `ipam_aggregate.prefix`
* `ipam_prefix.prefix`

It is also safe to ignore the message "Table missing: extras_script".

Resolve any differences by correcting migration files in the `squash-migrations` branch.

!!! warning
    Don't forget to remove `django_extension` from `INSTALLED_APPS` before committing your changes.

### 8. Merge the Squashed Migrations

Once all squashed migrations have been validated and all tests run successfully, merge the `squash-migrations` branch into `develop-2.x`. This completes the squashing process.
