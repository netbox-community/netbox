# Install NetBox from the Python Package (Experimental)

!!! warning "Experimental in NetBox v4.7"
    Installing NetBox from the Python package is experimental in NetBox v4.7 and is **not recommended for production use**. Use this workflow to evaluate the packaged installation, test upgrades and rollback procedures, and provide feedback.

    The established [release archive and Git installation methods](3-netbox.md) remain supported and are not replaced by this workflow.

The Python package installs the NetBox application and its Python dependencies into a virtual environment using `pip`. Configuration, uploaded media, custom scripts and reports, collected static files, and deployment configuration remain outside the installed package.

This installation method does **not** configure PostgreSQL, Redis, a WSGI server, an HTTP server, or system services. These remain administrator-managed deployment tasks, just as they are for an archive or Git installation.

## When to Use This Installation Method

Use the Python package for a new test or evaluation deployment when you want `pip` to manage the NetBox application code in a dedicated virtual environment. While this workflow remains experimental, use a [release archive or Git checkout](3-netbox.md) for production deployments.

A package installation is also available as a migration target for an existing deployment, but it is not an in-place conversion. Follow the [migration procedure](#migrate-an-existing-archive-or-git-installation) only after validating the workflow in a separate environment.

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

## Before You Begin

Complete the [PostgreSQL](1-postgresql.md) and [Redis](2-redis.md) installation steps first. Then install the same [required system packages](3-netbox.md#install-system-packages) used by the archive and Git installation methods.

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

Install the desired NetBox release. Replace `X.Y.Z` with the exact version to install:

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

Open the scaffolded configuration file:

```no-highlight
sudo ${EDITOR:-vi} /opt/netbox/conf/configuration.py
```

Define the five [required configuration parameters](../configuration/required-parameters.md):

* `ALLOWED_HOSTS`
* `API_TOKEN_PEPPERS`
* `DATABASES`
* `REDIS`
* `SECRET_KEY`

Generate a suitable random value for `SECRET_KEY` with the installed command:

```no-highlight
sudo /opt/netbox/venv/bin/netbox secret-key
```

Run the command again to generate an independent value for the first entry in `API_TOKEN_PEPPERS`. Treat both values as sensitive and do not reuse the examples from the documentation.

After saving the configuration, restrict access while allowing the NetBox service account to read it:

```no-highlight
sudo chown --recursive root:netbox /opt/netbox/conf
sudo chmod 750 /opt/netbox/conf
sudo chmod 640 /opt/netbox/conf/configuration.py
```

!!! note "Environment-based configuration"
    Ensure that any environment variables referenced by `configuration.py` are present when running `netbox upgrade`, `netbox createsuperuser`, and other management commands, and provide the same variables to both NetBox services. The copied `contrib/netbox.env` file is an example only and is not loaded automatically.

## Install Plugins and Optional Python Packages

Plugins and any other local Python requirements must be installed into the **same virtual environment** as NetBox before running the installation or upgrade tasks. Add each package to `/opt/netbox/local_requirements.txt`, then install the file:

```no-highlight
sudo ${EDITOR:-vi} /opt/netbox/local_requirements.txt
sudo /opt/netbox/venv/bin/python -m pip install \
    -r /opt/netbox/local_requirements.txt
```

Installing a plugin does not enable it. Add the plugin to the `PLUGINS` list in `/opt/netbox/conf/configuration.py` and complete any plugin-specific configuration separately.

NetBox also provides optional package extras for several common integrations. For example, install the LDAP dependencies together with the same pinned NetBox version as follows:

```no-highlight
sudo /opt/netbox/venv/bin/python -m pip install "netbox[ldap]==X.Y.Z"
```

Remember which extras are in use and specify them again when upgrading. For LDAP authentication, create `ldap_config.py` beside the active configuration file at `/opt/netbox/conf/ldap_config.py` when following the [LDAP configuration guide](6-ldap.md). Give it the same ownership and permissions as `configuration.py`:

```no-highlight
sudo chown root:netbox /opt/netbox/conf/ldap_config.py
sudo chmod 640 /opt/netbox/conf/ldap_config.py
```

When using uWSGI, install `pyuwsgi` into the same virtual environment and record it as a local requirement:

```no-highlight
sudo sh -c "echo 'pyuwsgi' >> /opt/netbox/local_requirements.txt"
sudo /opt/netbox/venv/bin/python -m pip install pyuwsgi
```

## Run the Installation Tasks

Run the packaged upgrade command to apply database migrations, collect static files, and perform the remaining application installation tasks:

```no-highlight
sudo -u netbox /opt/netbox/venv/bin/netbox upgrade --no-input
```

The `netbox upgrade` command is used for both a fresh package installation and future package upgrades. It replaces the source installation's `upgrade.sh` workflow.

For a custom instance root, pass `NETBOX_ROOT` explicitly. The virtual environment may remain elsewhere:

```no-highlight
sudo -u netbox env NETBOX_ROOT=/srv/netbox \
    /opt/netbox-venv/bin/netbox upgrade --no-input
```

## Create a Superuser

Create the first administrative account:

```no-highlight
sudo -u netbox /opt/netbox/venv/bin/netbox createsuperuser
```

## Test the Application

Start Django's development server temporarily to confirm that NetBox can load its configuration and connect to its dependencies:

```no-highlight
sudo -u netbox /opt/netbox/venv/bin/netbox \
    runserver 0.0.0.0:8000 --insecure
```

Connect to the server on port 8000 and log in with the superuser account. Type `Ctrl+c` to stop the development server after testing.

!!! danger "Not for production use"
    The development server is intended only for installation testing. It is neither performant nor secure enough for production use.

## Adapt the Deployment Examples

The files copied to `/opt/netbox/contrib/` are the same deployment examples shipped for archive and Git installations. They are not rewritten for the package layout. Adapt them before following the shared Gunicorn, uWSGI, and HTTP server instructions.

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

With the deployment examples adapted, continue with either [Gunicorn](4a-gunicorn.md) or [uWSGI](4b-uwsgi.md). When using uWSGI and you installed `pyuwsgi` above, skip the **Installation** subsection on the uWSGI page and begin with its configuration steps. Then configure an [HTTP server](5-http-server.md) and, if needed, [LDAP authentication](6-ldap.md).

The shared pages copy files from `/opt/netbox/contrib/`, so make the package-specific changes above **before** copying those files into their final locations.

## Migrate an Existing Archive or Git Installation

!!! warning "Experimental migration path"
    Migrating an existing deployment to the Python package changes its filesystem and upgrade model. Take a complete backup, document the current configuration, and verify a rollback procedure before proceeding.

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

    Repeat any NetBox package extras used by the deployment, and verify that each plugin supports the installed NetBox version.

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

After the migration is complete, use the [Python package upgrade procedure](upgrading.md#upgrade-a-python-package-installation-experimental) for future releases.
