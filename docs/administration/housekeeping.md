# Housekeeping

NetBox includes a `housekeeping` management command that should be run nightly. This command handles:

* Clearing expired authentication sessions from the database
* Deleting changelog records older than the configured [retention time](../configuration/optional-settings.md#changelog_retention)

This command can be invoked directly, or by using the shell script provided at `/opt/netbox/contrib/netbox-housekeeping.sh`. This script can be copied into your cron scheduler's daily jobs directory (e.g. `/etc/cron.daily`) or referenced directly within the cron configuration file.

The `housekeeping` command can also be run manually at any time: Running the command outside of scheduled execution times will not interfere with its operation.
