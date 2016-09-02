NetBox requires a PostgreSQL database to store data. MySQL is not supported, as NetBox leverage's PostgreSQL's built-in [network address types](https://www.postgresql.org/docs/9.1/static/datatype-net-types.html).

# Installation

The following packages are needed to install PostgreSQL with Python support:

Debian/Ubuntu

* postgresql
* libpq-dev
* python-psycopg2

Centos/RHEL

* postgresql
* postgresql-server
* postgresql-libs
* postgresql-devel

Debian/Ubuntu
```
# sudo apt-get install -y postgresql libpq-dev python-psycopg2
```
Centos/RHEL
```
# sudo yum install postgresql postgresql-server postgresql-libs postgresql-devel
```

# Configuration

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. This is done with the following commands.

!!! danger
    DO NOT USE THE PASSWORD FROM THE EXAMPLE.

```
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

```
# psql -U netbox -h localhost -W
```

If successful, you will enter a `postgres` prompt. Type `\q` to exit.
