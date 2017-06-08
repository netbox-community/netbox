#!/bin/bash
# This script will prepare NetBox to run after the code has been upgraded to
# its most recent release.
#
# Once the script completes, remember to restart the WSGI service (e.g.
# gunicorn or uWSGI).

# Optionally use sudo if not already root, and always prompt for password
# before running the command
PREFIX="sudo -k "
if [ "$(whoami)" = "root" ]; then
	# When running upgrade as root, ask user to confirm if they wish to
	# continue
	read -n1 -rsp $'Running NetBox upgrade as root, press any key to continue or ^C to cancel\n'
	PREFIX=""
fi

# Delete stale bytecode
COMMAND="${PREFIX}find . -name \"*.pyc\" -delete"
echo "Cleaning up stale Python bytecode ($COMMAND)..."
eval $COMMAND

# Prefer python3/pip3
PYTHON="python3"
type $PYTHON >/dev/null 2>&1 || PYTHON="python"
PIP="pip3"
type $PIP >/dev/null 2>&1 || PIP="pip"

# Install any new Python packages
COMMAND="${PREFIX}${PIP} install -r requirements.txt --upgrade"
echo "Updating required Python packages ($COMMAND)..."
eval $COMMAND

# Apply any database migrations
COMMAND="${PYTHON} netbox/manage.py migrate"
echo "Applying database migrations ($COMMAND)..."
eval $COMMAND

# Collect static files
COMMAND="${PYTHON} netbox/manage.py collectstatic --no-input"
echo "Collecting static files ($COMMAND)..."
eval $COMMAND
