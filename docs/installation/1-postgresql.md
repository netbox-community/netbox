# PostgreSQL Database Installation

This section entails the installation and configuration of a local PostgreSQL database. If you already have a PostgreSQL database service in place, skip to [the next section](2-redis.md).

!!! warning
    NetBox requires PostgreSQL 9.6 or higher. Please note that MySQL and other relational databases are **not** currently supported.

## Installation

=== "Ubuntu"

    ```no-highlight
    sudo apt update
    sudo apt install -y postgresql
    ```

=== "CentOS"

    ```no-highlight
    sudo yum install -y postgresql-server
    sudo postgresql-setup --initdb
    ```

    CentOS configures ident host-based authentication for PostgreSQL by default. Because NetBox will need to authenticate using a username and password, modify `/var/lib/pgsql/data/pg_hba.conf` to support MD5 authentication by changing `ident` to `md5` for the lines below:

    ```no-highlight
    host    all             all             127.0.0.1/32            md5
    host    all             all             ::1/128                 md5
    ```

Once PostgreSQL has been installed, start the service and enable it to run at boot:

```no-highlight
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Database Creation

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. Start by invoking the PostgreSQL shell as the system Postgres user.

```no-highlight
sudo -u postgres psql
```

Within the shell, enter the following commands to create the database and user (role), substituting your own value for the password:

```postgresql
CREATE DATABASE netbox;
CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
```

!!! danger
    **Do not use the password from the example.** Choose a strong, random password to ensure secure database authentication for your NetBox installation.

Once complete, enter `\q` to exit the PostgreSQL shell.

## Verify Service Status

You can verify that authentication works by executing the `psql` command and passing the configured username and password. (Replace `localhost` with your database server if using a remote database.)

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
