NetBox requires a PostgreSQL database to store data. This can be hosted locally or on a remote server. (Please note that MySQL is not supported, as NetBox leverages PostgreSQL's built-in [network address types](https://www.postgresql.org/docs/current/static/datatype-net-types.html).)

!!! note
    The installation instructions provided here have been tested to work on Ubuntu 16.04 and CentOS 7.4. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the NetBox maintainers. Please consult your distribution's documentation for assistance with any errors.

!!! warning
    NetBox v2.2 and later requires PostgreSQL 9.4 or higher.

# Installation

**Ubuntu**

If a recent enough version of PostgreSQL is not available through your distribution's package manager, you'll need to install it from an official [PostgreSQL repository](https://wiki.postgresql.org/wiki/Apt).

```no-highlight
# apt-get update
# apt-get install -y postgresql libpq-dev
```

**CentOS**

CentOS 7.4 does not ship with a recent enough version of PostgreSQL, so it will need to be installed from an external repository. The instructions below show the installation of PostgreSQL 9.6.

```no-highlight
# yum install https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
# yum install postgresql96 postgresql96-server postgresql96-devel
# /usr/pgsql-9.6/bin/postgresql96-setup initdb
```

CentOS users should modify the PostgreSQL configuration to accept password-based authentication by replacing `ident` with `md5` for all host entries within `/var/lib/pgsql/9.6/data/pg_hba.conf`. For example:

```no-highlight
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Then, start the service and enable it to run at boot:

```no-highlight
# systemctl start postgresql-9.6
# systemctl enable postgresql-9.6
```

# Database Creation

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. This is done with the following commands.

!!! danger
    DO NOT USE THE PASSWORD FROM THE EXAMPLE.

```no-highlight
# sudo -u postgres psql
psql (9.4.5)
Type "help" for help.

postgres=# CREATE DATABASE netbox;
CREATE DATABASE
postgres=# CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
GRANT
postgres=# \q
```

You can verify that authentication works issuing the following command and providing the configured password. (Replace `localhost` with your database server if using a remote database.)

```no-highlight
# psql -U netbox -W -h localhost netbox
```

If successful, you will enter a `netbox` prompt. Type `\q` to exit.
