# Install the Latest Code

As with the initial installation, you can upgrade NetBox by either downloading the latest release package or by cloning the `master` branch of the git repository. 

## Option A: Download a Release

Download the [latest stable release](https://github.com/digitalocean/netbox/releases) from GitHub as a tarball or ZIP archive. Extract it to your desired path. In this example, we'll use `/opt/netbox`.  For this guide we are using 1.0.4 as the old version and 1.0.7 as the new version.

Download & extract latest version:
```
# wget https://github.com/digitalocean/netbox/archive/vX.Y.Z.tar.gz
# tar -xzf vX.Y.Z.tar.gz -C /opt
# cd /opt/
# ln -sf netbox-1.0.7/ netbox
```

Copy the 'configuration.py' you created when first installing to the new version:
```
# cp /opt/netbox-1.0.4/configuration.py /opt/netbox/configuration.py
```

## Option B: Clone the Git Repository (latest master release)

For this guide, we'll use `/opt/netbox`.

Check that your git branch is up to date & is set to master:
```
# cd /opt/netbox
# git status
```

If not on branch master, set it and verify status:
```
# git checkout master
# git status
```

Pull down the set branch from git status above:
```
# git pull
```

# Run the Upgrade Script

Once the new code is in place, run the upgrade script (which may need to be run as root depending on how your environment is configured).

```
# ./upgrade.sh
```

This script:

* Installs or upgrades any new required Python packages
* Applies any database migrations that were included in the release
* Collects all static files to be served by the HTTP service

# Restart the WSGI Service

Finally, restart the WSGI service to run the new code. If you followed this guide for the initial installation, this is done using `supervisorctl`:

```
# sudo supervisorctl restart netbox
```
