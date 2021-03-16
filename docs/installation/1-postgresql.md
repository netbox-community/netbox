# PostgreSQL Database Installation

This section entails the installation and configuration of a local PostgreSQL database. If you already have a PostgreSQL database service in place, skip to [the next section](2-redis.md).

!!! warning
    NetBox requires PostgreSQL 9.6 or higher. Please note that MySQL and other relational databases are **not** currently supported.

## Installation

#### Ubuntu

Install the PostgreSQL server and client development libraries using `apt`.

```no-highlight
sudo apt update
sudo apt install -y postgresql libpq-dev
```

#### CentOS

PostgreSQL 9.6 and later are available natively on CentOS 8.2. If using an earlier CentOS release, you may need to [install it from an RPM](https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/).

```no-highlight
sudo yum install -y postgresql-server libpq-devel
sudo postgresql-setup --initdb
```

CentOS configures ident host-based authentication for PostgreSQL by default. Because NetBox will need to authenticate using a username and password, modify `/var/lib/pgsql/data/pg_hba.conf` to support MD5 authentication by changing `ident` to `md5` for the lines below:

```no-highlight
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Then, start the service and enable it to run at boot:

```no-highlight
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Database Creation

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. This is done with the following commands.

!!! danger
    **Do not use the password from the example.** Choose a strong, random password to ensure secure database authentication for your NetBox installation.

```no-highlight
$ sudo -u postgres psql
psql (12.5 (Ubuntu 12.5-0ubuntu0.20.04.1))
Type "help" for help.

postgres=# CREATE DATABASE netbox;
CREATE DATABASE
postgres=# CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
GRANT
postgres=# \q
```

## Verify Service Status

You can verify that authentication works issuing the following command and providing the configured password. (Replace `localhost` with your database server if using a remote database.)

```no-highlight
$ psql --username netbox --password --host localhost netbox
Password for user netbox: 
psql (12.5 (Ubuntu 12.5-0ubuntu0.20.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

netbox=> \conninfo
You are connected to database "netbox" as user "netbox" on host "localhost" (address "127.0.0.1") at port "5432".
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
netbox=> \q
```

If successful, you will enter a `netbox` prompt. Type `\conninfo` to confirm your connection, or type `\q` to exit.
