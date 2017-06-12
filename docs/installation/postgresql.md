NetBox requires a PostgreSQL database to store data. (Please note that MySQL is not supported, as NetBox leverages PostgreSQL's built-in [network address types](https://www.postgresql.org/docs/9.1/static/datatype-net-types.html).)

!!! note
    The installation instructions provided here have been tested to work on Ubuntu 16.04 and CentOS 6.9. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the NetBox maintainers. Please consult your distribution's documentation for assistance with any errors.

# Installation

**Ubuntu**

```no-highlight
# apt-get update
# apt-get install -y postgresql libpq-dev
```

**CentOS**

```no-highlight
# yum install -y postgresql postgresql-server postgresql-devel
# postgresql-setup initdb
```

CentOS users should modify the PostgreSQL configuration to accept password-based authentication by replacing `ident` with `md5` for all host entries within `/var/lib/pgsql/data/pg_hba.conf`. For example:

```no-highlight
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Then, start the service:

```no-highlight
# systemctl start postgresql
```

# Database Creation

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. This is done with the following commands.

!!! danger
    DO NOT USE THE PASSWORD FROM THE EXAMPLE.

```no-highlight
# sudo -u postgres psql
psql (9.3.13)
Type "help" for help.

postgres=# CREATE DATABASE netbox;
CREATE DATABASE
postgres=# CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
GRANT
postgres=# \q
```

You can verify that authentication works issuing the following command and providing the configured password:

```no-highlight
# psql -U netbox -h localhost -W
```

If successful, you will enter a `postgres` prompt. Type `\q` to exit.
