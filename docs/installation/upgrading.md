# Install the Latest Code

As with the initial installation, you can upgrade NetBox by either downloading the latest release package or by cloning the `master` branch of the git repository. 

## Option A: Download a Release

Download the [latest stable release](https://github.com/digitalocean/netbox/releases) from GitHub as a tarball or ZIP archive. Extract it to your desired path. In this example, we'll use `/opt/netbox`.

Download and extract the latest version:

```no-highlight
# wget https://github.com/digitalocean/netbox/archive/vX.Y.Z.tar.gz
# tar -xzf vX.Y.Z.tar.gz -C /opt
# cd /opt/
# ln -sf netbox-X.Y.Z/ netbox
```

Copy the 'configuration.py' you created when first installing to the new version:

```no-highlight
# cp /opt/netbox-X.Y.Z/netbox/netbox/configuration.py /opt/netbox/netbox/netbox/configuration.py
```

If you followed the original installation guide to set up gunicorn, be sure to copy its configuration as well:

```no-highlight
# cp /opt/netbox-X.Y.Z/gunicorn_config.py /opt/netbox/gunicorn_config.py
```

Copy the LDAP configuration if using LDAP:

```no-highlight
# cp /opt/netbox-X.Y.Z/netbox/netbox/ldap_config.py /opt/netbox/netbox/netbox/ldap_config.py
```

## Option B: Clone the Git Repository (latest master release)

This guide assumes that NetBox is installed at `/opt/netbox`. Pull down the most recent iteration of the master branch:

```no-highlight
# cd /opt/netbox
# git checkout master
# git pull origin master
# git status
```

# Run the Upgrade Script

Once the new code is in place, run the upgrade script (which may need to be run as root depending on how your environment is configured).

```no-highlight
# ./upgrade.sh
```

!!! warning
    The upgrade script will prefer Python3 and pip3 if both executables are available. To force it to use Python2 and pip, use the `-2` argument as below.

```no-highlight
# ./upgrade.sh -2
```

This script:

* Installs or upgrades any new required Python packages
* Applies any database migrations that were included in the release
* Collects all static files to be served by the HTTP service

!!! note
    It's possible that the upgrade script will display a notice warning of unreflected database migrations:

        Your models have changes that are not yet reflected in a migration, and so won't be applied.
        Run 'manage.py makemigrations' to make new migrations, and then re-run 'manage.py migrate' to apply them.

    This may occur due to semantic differences in environment, and can be safely ignored. Never attempt to create new migrations unless you are intentionally modifying the database schema.

# Restart the WSGI Service

Finally, restart the WSGI service to run the new code. If you followed this guide for the initial installation, this is done using `supervisorctl`:

```no-highlight
# sudo supervisorctl restart netbox
```
