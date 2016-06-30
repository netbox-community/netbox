#!/bin/sh
# This script will prepare NetBox to run after the code has been upgraded to
# its most recent release.
#
# Once the script completes, remember to restart the WSGI service (e.g.
# gunicorn or uWSGI).

# Install any new Python packages
echo "Updating required Python packages (pip install -r requirements.txt --upgrade)..."
sudo pip install -r requirements.txt --upgrade

# Apply any database migrations
./netbox/manage.py migrate

# Collect static files
./netbox/manage.py collectstatic --noinput
