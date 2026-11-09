# Install NetBox

NetBox is published as a [Python package on PyPI](https://pypi.org/project/netbox/). This guide uses `pip` to install the NetBox application and its Python dependencies into a virtual environment. Configuration, uploaded media, custom scripts and reports, collected static files, and deployment configuration are kept outside the installed package.

This step does **not** configure PostgreSQL, Redis, a WSGI server, an HTTP server, or system services. These are covered by the other steps of the installation guide.

!!! info "Installing from source"
    NetBox can also be run from a clone of its [Git repository](https://github.com/netbox-community/netbox) or from a release archive (tarball) downloaded from [GitHub](https://github.com/netbox-community/netbox/releases). These methods are intended for developers working on NetBox itself; see the [development guide](../development/getting-started.md) to set up a development environment. Existing deployments installed by these methods can be [migrated to the Python package](#migrate-an-existing-archive-or-git-installation).

## Understand the Installation Layout

A package installation separates the application code from the files that belong to a particular NetBox instance.

| Component | Example Location | Purpose |
|-----------|------------------|---------|
| Application code | `<venv>/lib/pythonX.Y/site-packages/` | Installed and replaced by `pip`; do not modify it directly |
| Python virtual environment | `/opt/netbox/venv/` | Contains NetBox, its dependencies, and any plugins |
| Instance root | `/opt/netbox/` | Holds local configuration and mutable instance data |
| Configuration | `/opt/netbox/conf/configuration.py` | Contains settings and credentials for this instance |
| Mutable data | `/opt/netbox/{media,reports,scripts,static}/` | Persists independently of package upgrades |
| Deployment examples | `/opt/netbox/contrib/` | Local copies to review and adapt before use |

The instance root defaults to `/opt/netbox` and may be changed with the `NETBOX_ROOT` environment variable. The virtual environment does not need to be located below the instance root; `/opt/netbox/venv` is used throughout this guide only to keep the example straightforward.

!!! note "Custom instance roots"
    The `--target` option for `netbox setup` selects where the local files are created. It does not permanently set the instance root. When using a location other than `/opt/netbox`, set `NETBOX_ROOT` for all NetBox commands and services.

## Install System Packages

Begin by installing all system packages required by NetBox and its dependencies.

!!! warning "Python 3.12 or later required"
    NetBox supports only Python 3.12 or later.

```no-highlight
sudo apt install -y python3 python3-pip python3-venv python3-dev \
build-essential libxml2-dev libxslt1-dev libffi-dev libpq-dev \
libssl-dev zlib1g-dev
```

Before continuing, check that your installed Python version is at least 3.12:

```no-highlight
python3 -V
```

## Create the System User and Instance Root

Create the `netbox` system account and the default instance root:

```no-highlight
sudo adduser --system --group netbox
sudo mkdir -p /opt/netbox
sudo chown root:netbox /opt/netbox
sudo chmod 755 /opt/netbox
```

## Create the Virtual Environment

Create a Python virtual environment and update `pip`:

```no-highlight
sudo python3 -m venv /opt/netbox/venv
sudo /opt/netbox/venv/bin/python -m pip install --upgrade pip
```

If the default `python3` executable is older than Python 3.12, create the virtual environment with a supported interpreter instead (for example, `sudo python3.12 -m venv /opt/netbox/venv`).

Install the desired NetBox release. Replace `X.Y.Z` with the exact version to install. (Available releases are listed on [PyPI](https://pypi.org/project/netbox/#history).)

```no-highlight
sudo /opt/netbox/venv/bin/python -m pip install "netbox==X.Y.Z"
```

Pinning the version makes the installed release explicit and prevents an unintended upgrade when the command is repeated later.

## Scaffold the Instance Root

Run `netbox setup` to create the local configuration skeleton and copy the bundled deployment examples:

```no-highlight
sudo /opt/netbox/venv/bin/netbox setup --target /opt/netbox
```

The command creates the following files when they do not already exist:

```no-highlight
/opt/netbox/
├── conf/
│   ├── __init__.py
│   └── configuration.py
├── contrib/
│   ├── apache.conf
│   ├── gunicorn.py
│   ├── netbox-rq.service
│   ├── netbox.env
│   ├── netbox.service
│   ├── nginx.conf
│   └── uwsgi.ini
└── local_requirements.txt
```

`netbox setup` is intentionally non-destructive: existing files are left untouched. It does not install systemd units, configure an HTTP server, rewrite deployment examples for the local paths, or enable plugins.

Create the directories used for mutable instance data and grant the NetBox service account ownership of them:

```no-highlight
sudo mkdir -p /opt/netbox/{media,reports,scripts,static}
sudo chown --recursive netbox:netbox \
    /opt/netbox/media \
    /opt/netbox/reports \
    /opt/netbox/scripts \
    /opt/netbox/static
```

## Configure NetBox

Open the scaffolded configuration file with your preferred editor:

```no-highlight
sudo ${EDITOR:-vi} /opt/netbox/conf/configuration.py
```

NetBox offers [many configuration parameters](../configuration/index.md), but only the following five are required for new installations:

* `ALLOWED_HOSTS`
* `API_TOKEN_PEPPERS`
* `DATABASES`
* `REDIS`
* `SECRET_KEY`

### ALLOWED_HOSTS

This is a list of the valid hostnames and IP addresses by which this server can be reached. You must specify at least one name or IP address. (Note that this does not restrict the locations from which NetBox may be accessed: It is merely for [HTTP host header validation](https://docs.djangoproject.com/en/stable/topics/security/#host-headers-virtual-hosting).)

```python
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

If you are not yet sure what the domain name and/or IP address of the NetBox installation will be, you can set this to a wildcard (asterisk) to allow all host values:

```python
ALLOWED_HOSTS = ['*']
```

### API_TOKEN_PEPPERS

Define at least one random cryptographic pepper, identified by a numeric ID starting at 1. This will be used to generate SHA256 checksums for API tokens.

```python
API_TOKEN_PEPPERS = {
    # DO NOT USE THIS EXAMPLE PEPPER IN PRODUCTION
    1: 'kp7ht*76fiQAhUi5dHfASLlYUE_S^gI^(7J^K5M!LfoH@vl&b_',
}
```

!!! tip
    As with [`SECRET_KEY`](#secret_key) below, you can use the `netbox secret-key` command to generate a random pepper. Run it separately for each value so that the pepper and `SECRET_KEY` are independent:
    ```no-highlight
    sudo /opt/netbox/venv/bin/netbox secret-key
    ```

### DATABASES

This parameter holds the PostgreSQL database configuration details. The default database must be defined; additional databases may be defined as needed e.g. by plugins.

A username and password must be defined for the default database. If the service is running on a remote host, update the `HOST` and `PORT` parameters accordingly. See the [configuration documentation](../configuration/required-parameters.md#databases) for more detail on individual parameters.

```python
DATABASES = {
    'default': {
        'NAME': 'netbox',               # Database name
        'USER': 'netbox',               # PostgreSQL username
        'PASSWORD': 'J5brHrAXFLQSif0K', # PostgreSQL password
        'HOST': 'localhost',            # Database server
        'PORT': '',                     # Database port (leave blank for default)
        'CONN_MAX_AGE': 300,            # Max database connection age (seconds)
    }
}
```

### REDIS

Redis is an in-memory key-value store used by NetBox for caching and background task queuing. Redis typically requires minimal configuration; the values below should suffice for most installations. See the [configuration documentation](../configuration/required-parameters.md#redis) for more detail on individual parameters.

Note that NetBox requires the specification of two separate Redis databases: `tasks` and `caching`. These may both be provided by the same Redis service, however each should have a unique numeric database ID.

```python
REDIS = {
    'tasks': {
        'HOST': 'localhost',      # Redis server
        'PORT': 6379,             # Redis port
        'PASSWORD': '',           # Redis password (optional)
        'DATABASE': 0,            # Database ID
        'SSL': False,             # Use SSL (optional)
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,            # Unique ID for second database
        'SSL': False,
    }
}
```

### SECRET_KEY

This parameter must be assigned a randomly-generated key employed as a salt for hashing and related cryptographic functions. (Note, however, that it is _never_ directly used in the encryption of secret data.) This key must be unique to this installation and is recommended to be at least 50 characters long. It should not be shared outside the local system.

Generate a suitable key with the installed `netbox secret-key` command:

```no-highlight
sudo /opt/netbox/venv/bin/netbox secret-key
```

!!! warning "SECRET_KEY values must match"
    In the case of a highly available installation with multiple web servers, `SECRET_KEY` must be identical among all servers in order to maintain a persistent user session state.

### Restrict Access to the Configuration

After saving the configuration, restrict access while allowing the NetBox service account to read it:

```no-highlight
sudo chown --recursive root:netbox /opt/netbox/conf
sudo chmod 750 /opt/netbox/conf
sudo chmod 640 /opt/netbox/conf/configuration.py
```

!!! note "Environment-based configuration"
    Ensure that any environment variables referenced by `configuration.py` are present when running `netbox upgrade`, `netbox createsuperuser`, and other management commands, and provide the same variables to both NetBox services. The copied `contrib/netbox.env` file is an example only and is not loaded automatically.

## Install Optional Packages and Plugins

### Package Extras

NetBox provides optional package extras for several common integrations. Each extra installs the additional Python libraries required by an integration:

| Extra | Installs | Purpose |
|-------|----------|---------|
| `ldap` | `django-auth-ldap` | [LDAP authentication](6-ldap.md) |
| `saml2` | `python3-saml` | SAML single sign-on |
| `remote-auth` | `django-auth-ldap`, `python3-saml` | LDAP authentication and SAML single sign-on |
| `s3` | `boto3` | Amazon S3 [remote data sources](../features/synchronized-data.md) and [file storage](../configuration/system.md#storages) |
| `git` | `dulwich` | Git [remote data sources](../features/synchronized-data.md) |
| `swift` | `django-storage-swift` | OpenStack Swift [file storage](../configuration/system.md#storages) |
| `sentry` | `sentry-sdk` | [Sentry error reporting](../administration/error-reporting.md) |

To install one or more extras, install NetBox again with the same pinned version, listing the extras in brackets. For example, to install the LDAP and Amazon S3 dependencies:

```no-highlight
sudo /opt/netbox/venv/bin/python -m pip install "netbox[ldap,s3]==X.Y.Z"
```

Remember which extras are in use and specify them again when upgrading. For LDAP authentication, create `ldap_config.py` beside the active configuration file at `/opt/netbox/conf/ldap_config.py` when following the [LDAP configuration guide](6-ldap.md). Give it the same ownership and permissions as `configuration.py`:

```no-highlight
sudo chown root:netbox /opt/netbox/conf/ldap_config.py
sudo chmod 640 /opt/netbox/conf/ldap_config.py
```

### Plugins and Other Python Packages

Plugins and any other local Python requirements must be installed into the **same virtual environment** as NetBox before running the installation or upgrade tasks. Add each package to `/opt/netbox/local_requirements.txt`, then install the file:

```no-highlight
sudo ${EDITOR:-vi} /opt/netbox/local_requirements.txt
sudo /opt/netbox/venv/bin/python -m pip install \
    -r /opt/netbox/local_requirements.txt
```

Installing a plugin does not enable it. Add the plugin to the `PLUGINS` list in `/opt/netbox/conf/configuration.py` and complete any plugin-specific configuration separately.

## Run the Installation Tasks

Run the `netbox upgrade` command to perform the application installation tasks:

```no-highlight
sudo -u netbox /opt/netbox/venv/bin/netbox upgrade --no-input
```

The same command is used for both a fresh installation and future upgrades. It performs the following actions:

* Applies database schema migrations
* Traces any missing cable paths
* Collects static files to be served by the HTTP server
* Removes stale content types from the database
* Rebuilds the search index
* Clears expired user sessions from the database

For a custom instance root, pass `NETBOX_ROOT` explicitly. The virtual environment may remain elsewhere:

```no-highlight
sudo -u netbox env NETBOX_ROOT=/srv/netbox \
    /opt/netbox-venv/bin/netbox upgrade --no-input
```

!!! note
    To run the command on a node connected to a database in read-only mode, include the `--readonly` option. This skips all tasks that modify the database or filesystem.

## Create a Superuser

NetBox does not come with any predefined user accounts. Create a superuser (administrative account) to be able to log into NetBox. Specifying an email address for the user is not required, but be sure to use a very strong password.

```no-highlight
sudo -u netbox /opt/netbox/venv/bin/netbox createsuperuser
```

## Test the Application

Start Django's development server temporarily to confirm that NetBox can load its configuration and connect to its dependencies:

```no-highlight
sudo -u netbox /opt/netbox/venv/bin/netbox \
    runserver 0.0.0.0:8000 --insecure
```

If successful, you should see output similar to the following:

```no-highlight
Performing system checks...

System check identified no issues (0 silenced).
January 26, 2026 - 17:00:00
Django version 5.2.10, using settings 'netbox.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

Next, connect to the name or IP of the server (as defined in `ALLOWED_HOSTS`) on port 8000; for example, <http://127.0.0.1:8000/>. You should be greeted with the NetBox home page. Try logging in using the username and password specified when creating a superuser.

!!! danger "Not for production use"
    The development server is for development and testing purposes only. It is neither performant nor secure enough for production use. **Do not use it in production.**

!!! warning
    If the test service does not run, or you cannot reach the NetBox home page, something has gone wrong. Do not proceed with the rest of this guide until the installation has been corrected.

Type `Ctrl+c` to stop the development server.

## Adapt the Deployment Examples

The files copied to `/opt/netbox/contrib/` reference a source-tree layout and are not rewritten for the package layout. Adapt them before following the Gunicorn, uWSGI, and HTTP server instructions.

For the default paths used in this guide, the following commands remove the source-tree references:

```no-highlight
sudo sed -i \
    's| --pythonpath /opt/netbox/netbox||' \
    /opt/netbox/contrib/netbox.service

sudo sed -i \
    's|/opt/netbox/venv/bin/python3 /opt/netbox/netbox/manage.py|/opt/netbox/venv/bin/netbox|' \
    /opt/netbox/contrib/netbox-rq.service

sudo sed -i \
    's|chdir = netbox|chdir = /opt/netbox|' \
    /opt/netbox/contrib/uwsgi.ini

sudo sed -i \
    's|/opt/netbox/netbox/static|/opt/netbox/static|g' \
    /opt/netbox/contrib/nginx.conf \
    /opt/netbox/contrib/apache.conf
```

These changes have the following effect:

| File | Package Installation Change |
|------|-----------------------------|
| `netbox.service` | Imports `netbox.wsgi` from the virtual environment without a source-tree `--pythonpath` |
| `netbox-rq.service` | Runs the RQ worker through the installed `netbox` command instead of `manage.py` |
| `uwsgi.ini` | Uses the instance root rather than the absent `/opt/netbox/netbox/` source directory |
| `nginx.conf` and `apache.conf` | Serve collected static files from `/opt/netbox/static/` |

Review every file before installing it. When using a different instance root or virtual environment, update all `WorkingDirectory`, `ExecStart`, `chdir`, virtual environment, and static-file paths accordingly. Also add the following line to the `[Service]` section of both systemd units, replacing the path as needed:

```ini
Environment=NETBOX_ROOT=/srv/netbox
```

When using environment-based configuration, reference an appropriate environment file from both systemd units or define the required variables directly in each unit.

## Continue the Installation

With the deployment examples adapted, continue with either [Gunicorn](4a-gunicorn.md) or [uWSGI](4b-uwsgi.md). Then configure an [HTTP server](5-http-server.md) and, if needed, [LDAP authentication](6-ldap.md).

The following pages copy files from `/opt/netbox/contrib/`, so make the package-specific changes above **before** copying those files into their final locations.

## Migrate an Existing Archive or Git Installation

!!! warning "Back up before migrating"
    Migrating an existing deployment to the Python package changes its filesystem layout and upgrade procedure. Take a complete backup, document the current configuration, and verify a rollback procedure before proceeding.

Deployments installed from a release archive or Git checkout can be migrated to the Python package. This is not an in-place conversion: the procedure below builds a new package-based deployment alongside the existing one, which is retained until the new deployment has been validated.

Python package releases begin with NetBox v4.7. Before migrating an older deployment, first upgrade the existing archive or Git installation to a version that is available as a Python package.

Migrate the layout separately from a NetBox version upgrade. Install the **same NetBox version** that is currently running, validate the package-based deployment, and only then upgrade to a newer release.

The following example keeps the existing `/opt/netbox` installation in place during migration. It uses `/srv/netbox` as the new instance root and `/opt/netbox-venv` for the new virtual environment.

1. Stop the existing NetBox services after completing a backup:

    ```no-highlight
    sudo systemctl stop netbox netbox-rq
    ```

2. Create the new virtual environment and install the same NetBox version as the existing deployment:

    ```no-highlight
    sudo python3 -m venv /opt/netbox-venv
    sudo /opt/netbox-venv/bin/python -m pip install --upgrade pip
    sudo /opt/netbox-venv/bin/python -m pip install "netbox==X.Y.Z"
    ```

3. Scaffold the new instance root and create its mutable directories:

    ```no-highlight
    sudo mkdir -p /srv/netbox
    sudo chown root:netbox /srv/netbox
    sudo chmod 755 /srv/netbox
    sudo /opt/netbox-venv/bin/netbox setup --target /srv/netbox
    sudo mkdir -p /srv/netbox/{media,reports,scripts,static}
    sudo chown --recursive netbox:netbox \
        /srv/netbox/media \
        /srv/netbox/reports \
        /srv/netbox/scripts \
        /srv/netbox/static
    ```

4. Copy the active configuration from the existing installation. If `local_requirements.txt` exists, copy it over the empty file created by `netbox setup`:

    ```no-highlight
    sudo cp /opt/netbox/netbox/netbox/configuration.py \
        /srv/netbox/conf/configuration.py

    if [ -f /opt/netbox/local_requirements.txt ]; then
        sudo cp /opt/netbox/local_requirements.txt \
            /srv/netbox/local_requirements.txt
    fi
    ```

    When the existing deployment uses `NETBOX_CONFIGURATION`, copy the active configuration module instead, together with any sibling modules or local files it imports. Review the copied configuration and update any filesystem paths that still reference the old source tree.

    If LDAP is configured, also copy the active `ldap_config.py` to `/srv/netbox/conf/ldap_config.py`.

5. Copy locally stored media, reports, and scripts. Do not copy collected static files; `netbox upgrade` will create them again.

    ```no-highlight
    sudo cp -a /opt/netbox/netbox/media/. /srv/netbox/media/
    sudo cp -a /opt/netbox/netbox/reports/. /srv/netbox/reports/
    sudo cp -a /opt/netbox/netbox/scripts/. /srv/netbox/scripts/
    sudo chown --recursive netbox:netbox \
        /srv/netbox/media \
        /srv/netbox/reports \
        /srv/netbox/scripts
    ```

    Use the paths configured by `MEDIA_ROOT`, `REPORTS_ROOT`, and `SCRIPTS_ROOT` instead when the existing deployment stores these files elsewhere.

6. Install all plugins and local requirements into the new virtual environment **before** running the upgrade tasks:

    ```no-highlight
    sudo /opt/netbox-venv/bin/python -m pip install \
        -r /srv/netbox/local_requirements.txt
    ```

    Repeat any [package extras](#package-extras) needed by the deployment, and verify that each plugin supports the installed NetBox version.

7. Secure the configuration and run the package installation tasks against the existing database:

    ```no-highlight
    sudo chown --recursive root:netbox /srv/netbox/conf
    sudo chmod 750 /srv/netbox/conf
    sudo chmod 640 /srv/netbox/conf/configuration.py

    sudo -u netbox env NETBOX_ROOT=/srv/netbox \
        /opt/netbox-venv/bin/netbox upgrade --no-input
    ```

    If `ldap_config.py` was copied, also run `sudo chmod 640 /srv/netbox/conf/ldap_config.py`.

8. Follow [Adapt the Deployment Examples](#adapt-the-deployment-examples), substituting `/srv/netbox` and `/opt/netbox-venv` for the example paths. Install the updated systemd and HTTP server configuration, switch the services to the package deployment, and ensure that both systemd units define `NETBOX_ROOT=/srv/netbox`.

9. Start the services, test the web interface and background processing, and retain the previous installation until the new deployment has been validated:

    ```no-highlight
    sudo systemctl start netbox netbox-rq
    ```

After the migration is complete, use the [standard upgrade procedure](upgrading.md#upgrade-a-python-package-installation) for future releases.
