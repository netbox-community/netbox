#!/bin/sh
# This shell script invokes NetBox's housekeeping management command, which
# intended to be run nightly. This script can be copied into your system's
# daily cron directory (e.g. /etc/cron.daily), or referenced directly from
# within the cron configuration file.
#
# If NetBox has been installed into a nonstandard location, update the paths
# below.
# By default, all output is discarded. Uncomment the log lines below to enable
# logging.

# Run quietly (no log)
# --------------------
/opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py housekeeping > /dev/null 2>&1

# Run with logging (append output to log file)
# --------------------------------------------
# LOGFILE="/var/log/netbox/housekeeping.log"
# echo "[$(date)] Starting NetBox housekeeping..." >> "$LOGFILE"
# /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py housekeeping >> "$LOGFILE" 2>&1
# echo "[$(date)] NetBox housekeeping complete." >> "$LOGFILE"
