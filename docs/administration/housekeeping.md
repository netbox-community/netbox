# Housekeeping

NetBox includes a `housekeeping` management command that should be run nightly. This command handles:

* Clearing expired authentication sessions from the database
* Deleting changelog records older than the configured [retention time](../configuration/miscellaneous.md#changelog_retention)
* Deleting job result records older than the configured [retention time](../configuration/miscellaneous.md#job_retention)
* Check for new NetBox releases (if [`RELEASE_CHECK_URL`](../configuration/miscellaneous.md#release_check_url) is set)

This command can be invoked directly, or by using the shell script provided at `/opt/netbox/contrib/netbox-housekeeping.sh`.

## Scheduling

### Using Cron

This script can be linked from your cron scheduler's daily jobs directory (e.g. `/etc/cron.daily`) or referenced directly within the cron configuration file.

```shell
sudo ln -s /opt/netbox/contrib/netbox-housekeeping.sh /etc/cron.daily/netbox-housekeeping
```

!!! note
    On Debian-based systems, be sure to omit the `.sh` file extension when linking to the script from within a cron directory. Otherwise, the task may not run.

### Using Systemd

First, create symbolic links for the systemd service and timer files. Link the existing service and timer files from the `/opt/netbox/contrib/` directory to the `/etc/systemd/system/` directory:

```bash
sudo ln -s /opt/netbox/contrib/netbox-housekeeping.service /etc/systemd/system/netbox-housekeeping.service
sudo ln -s /opt/netbox/contrib/netbox-housekeeping.timer /etc/systemd/system/netbox-housekeeping.timer
```

Then, reload the systemd configuration and enable the timer to start automatically at boot:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now netbox-housekeeping.timer
```

Check the status of your timer by running:

```bash
sudo systemctl list-timers --all
```

This command will show a list of all timers, including your `netbox-housekeeping.timer`. Make sure the timer is active and properly scheduled.

That's it! Your NetBox housekeeping service is now configured to run daily using systemd.
