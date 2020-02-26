#!/bin/bash
# This script will prepare NetBox to run after the code has been upgraded to
# its most recent release.

cd "$(dirname "$0")"
VIRTUALENV="$(pwd -P)/venv"

# Remove the existing virtual environment (if any)
if [ -d "$VIRTUALENV" ]; then
  COMMAND="rm -rf ${VIRTUALENV}"
  echo "Removing old virtual environment..."
  eval $COMMAND
fi

# Create a new virtual environment
COMMAND="/usr/bin/python3 -m venv ${VIRTUALENV}"
echo "Creating a new virtual environment at ${VIRTUALENV}..."
eval $COMMAND

# Activate the virtual environment
source "${VIRTUALENV}/bin/activate"

# Install Python packages
COMMAND="pip3 install -r requirements.txt"
echo "Installing Python packages ($COMMAND)..."
eval $COMMAND

# Apply any database migrations
COMMAND="python3 netbox/manage.py migrate"
echo "Applying database migrations ($COMMAND)..."
eval $COMMAND

# Collect static files
COMMAND="python3 netbox/manage.py collectstatic --no-input"
echo "Collecting static files ($COMMAND)..."
eval $COMMAND

# Delete any stale content types
COMMAND="python3 netbox/manage.py remove_stale_contenttypes --no-input"
echo "Removing stale content types ($COMMAND)..."
eval $COMMAND

# Clear all cached data
COMMAND="python3 netbox/manage.py invalidate all"
echo "Clearing cache data ($COMMAND)..."
eval $COMMAND

echo "Upgrade complete! Don't forget to restart the NetBox services:"
echo "  sudo systemctl restart netbox"
echo "  sudo systemctl restart netbox-rq"
