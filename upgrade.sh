#!/bin/bash
# This script will prepare NetBox to run after the code has been upgraded to
# its most recent release.
#
# Once the script completes, remember to restart the WSGI service (e.g.
# gunicorn or uWSGI).

cd "$(dirname "$0")"

PYTHON="python3"
PIP="pip3"

# Uninstall any Python packages which are no longer needed
COMMAND="${PIP} uninstall -r old_requirements.txt -y"
echo "Removing old Python packages ($COMMAND)..."
eval $COMMAND

# Install any new Python packages
COMMAND="${PIP} install -r requirements.txt --upgrade"
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
