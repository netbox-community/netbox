# Upgrading to a New NetBox Release

## Review the Release Notes

Prior to upgrading your NetBox instance, be sure to carefully review all [release notes](../release-notes/index.md) that have been published since your current version was released. Although the upgrade process typically does not involve additional work, certain releases may introduce breaking or backward-incompatible changes. These are called out in the release notes under the release in which the change went into effect.

## Update Dependencies to Required Versions

NetBox v3.0 and later requires the following:

| Dependency | Minimum Version |
|------------|-----------------|
| Python     | 3.7             |
| PostgreSQL | 9.6             |
| Redis      | 4.0             |

## Install the Latest Release

As with the initial installation, you can upgrade NetBox by either downloading the latest release package or by cloning the `master` branch of the git repository. 

### Option A: Download a Release

Download the [latest stable release](https://github.com/netbox-community/netbox/releases) from GitHub as a tarball or ZIP archive. Extract it to your desired path. In this example, we'll use `/opt/netbox`.

Download and extract the latest version:

```no-highlight
wget https://github.com/netbox-community/netbox/archive/vX.Y.Z.tar.gz
sudo tar -xzf vX.Y.Z.tar.gz -C /opt
sudo ln -sfn /opt/netbox-X.Y.Z/ /opt/netbox
```

Copy `local_requirements.txt`, `configuration.py`, and `ldap_config.py` (if present) from the current installation to the new version:

```no-highlight
sudo cp /opt/netbox-X.Y.Z/local_requirements.txt /opt/netbox/
sudo cp /opt/netbox-X.Y.Z/netbox/netbox/configuration.py /opt/netbox/netbox/netbox/
sudo cp /opt/netbox-X.Y.Z/netbox/netbox/ldap_config.py /opt/netbox/netbox/netbox/
```

Be sure to replicate your uploaded media as well. (The exact action necessary will depend on where you choose to store your media, but in general moving or copying the media directory will suffice.)

```no-highlight
sudo cp -pr /opt/netbox-X.Y.Z/netbox/media/ /opt/netbox/netbox/
```

Also make sure to copy or link any custom scripts and reports that you've made. Note that if these are stored outside the project root, you will not need to copy them. (Check the `SCRIPTS_ROOT` and `REPORTS_ROOT` parameters in the configuration file above if you're unsure.)

```no-highlight
sudo cp -r /opt/netbox-X.Y.Z/netbox/scripts /opt/netbox/netbox/
sudo cp -r /opt/netbox-X.Y.Z/netbox/reports /opt/netbox/netbox/
```

If you followed the original installation guide to set up gunicorn, be sure to copy its configuration as well:

```no-highlight
sudo cp /opt/netbox-X.Y.Z/gunicorn.py /opt/netbox/
```

### Option B: Clone the Git Repository

This guide assumes that NetBox is installed at `/opt/netbox`. Pull down the most recent iteration of the master branch:

```no-highlight
cd /opt/netbox
sudo git checkout master
sudo git pull origin master
```

## Run the Upgrade Script

Once the new code is in place, verify that any optional Python packages required by your deployment (e.g. `napalm` or `django-auth-ldap`) are listed in `local_requirements.txt`. Then, run the upgrade script:

```no-highlight
sudo ./upgrade.sh
```

This script performs the following actions:

* Destroys and rebuilds the Python virtual environment
* Installs all required Python packages (listed in `requirements.txt`)
* Installs any additional packages from `local_requirements.txt`
* Applies any database migrations that were included in the release
* Collects all static files to be served by the HTTP service
* Deletes stale content types from the database
* Deletes all expired user sessions from the database
* Clears all cached data to prevent conflicts with the new release

!!! note
    If the upgrade script prompts a warning about unreflected database migrations, this indicates that some change has
    been made to your local codebase and should be investigated. Never attempt to create new migrations unless you are
    intentionally modifying the database schema.

## Restart the NetBox Services

!!! warning
    If you are upgrading from an installation that does not use a Python virtual environment (any release prior to v2.7.9), you'll need to update the systemd service files to reference the new Python and gunicorn executables before restarting the services. These are located in `/opt/netbox/venv/bin/`. See the example service files in `/opt/netbox/contrib/` for reference.

Finally, restart the gunicorn and RQ services:

```no-highlight
sudo systemctl restart netbox netbox-rq
```

## Verify Housekeeping Scheduling

If upgrading from a release prior to NetBox v3.0, check that a cron task (or similar scheduled process) has been configured to run NetBox's nightly housekeeping command. A shell script which invokes this command is included at `contrib/netbox-housekeeping.sh`. It can be copied to your system's daily cron task directory, or included within the crontab directly. (If NetBox has been installed in a nonstandard path, be sure to update the system paths within this script first.)

```shell
cp /opt/netbox/contrib/netbox-housekeeping.sh /etc/cron.daily/
```

See the [housekeeping documentation](../administration/housekeeping.md) for further details.
