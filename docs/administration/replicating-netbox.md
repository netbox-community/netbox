# Replicating the Database

NetBox uses [PostgreSQL](https://www.postgresql.org/) for its database, so general PostgreSQL best practices will apply to NetBox. You can dump and restore the database using the `pg_dump` and `psql` utilities, respectively.

!!! note
    The examples below assume that your database is named `netbox`.

## Export the Database

Use the `pg_dump` utility to export the entire database to a file:

```no-highlight
pg_dump netbox > netbox.sql
```

When replicating a production database for development purposes, you may find it convenient to exclude changelog data, which can easily account for the bulk of a database's size. To do this, exclude the `extras_objectchange` table data from the export. The table will still be included in the output file, but will not be populated with any data.

```no-highlight
pg_dump --exclude-table-data=extras_objectchange netbox > netbox.sql
```

## Load an Exported Database

!!! warning
    This will destroy and replace any existing instance of the database.

```no-highlight
psql -c 'drop database netbox'
psql -c 'create database netbox'
psql netbox < netbox.sql
```

Keep in mind that PostgreSQL user accounts and permissions are not included with the dump: You will need to create those manually if you want to fully replicate the original database (see the [installation docs](installation/1-postgresql.md)). When setting up a development instance of NetBox, it's strongly recommended to use different credentials anyway.

## Export the Database Schema

If you want to export only the database schema, and not the data itself (e.g. for development reference), do the following:

```no-highlight
pg_dump -s netbox > netbox_schema.sql
```

---

# Replicating Media

NetBox stored uploaded files (such as image attachments) in its media directory. To fully replicate an instance of NetBox, you'll need to copy both the database and the media files.

## Archive the Media Directory

Execute the following command from the root of the NetBox installation path (typically `/opt/netbox`):

```no-highlight
tar -czf netbox_media.tar.gz netbox/media/
```

## Restore the Media Directory

To extract the saved archive into a new installation, run the following from the installation root:

```no-highlight
tar -xf netbox_media.tar.gz
```
