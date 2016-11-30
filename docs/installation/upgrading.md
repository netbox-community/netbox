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

This script:

* Installs or upgrades any new required Python packages
* Applies any database migrations that were included in the release
* Collects all static files to be served by the HTTP service

# Restart the WSGI Service

Finally, restart the WSGI service to run the new code. If you followed this guide for the initial installation, this is done using `supervisorctl`:

```no-highlight
# sudo supervisorctl restart netbox
```
