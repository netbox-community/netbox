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

# Prefer Python 3
PIP=pip
if type -P pip3 >/dev/null 2>&1; then
	# We're likely on something Debian-based with numbered coexistent pythons.
	# If we're running 3.4 or better, use pip3 and invoke scripts with python3
	pip_version=$(pip3 --version | sed -e 's/.*(python \(.*\))/\1/')
	if [[ ${pip_version:0:1} == 3 && ${pip_version:2:1} -gt 3 ]]; then
		PIP=pip3
		find . -type f -name '*.py' -execdir sed -i -e '1s/python/python3/' {} +
	fi
fi

# Install any new Python packages
COMMAND="${PREFIX}${PIP} install -r requirements.txt --upgrade"
echo "Updating required Python packages ($COMMAND)..."
eval $COMMAND

# Apply any database migrations
COMMAND="./netbox/manage.py migrate"
echo "Applying database migrations ($COMMAND)..."
eval $COMMAND

# Collect static files
COMMAND="./netbox/manage.py collectstatic --no-input"
echo "Collecting static files ($COMMAND)..."
eval $COMMAND
