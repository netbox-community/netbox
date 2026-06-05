#!/bin/sh

DB=${2:-netbox}

# Drop and re-create the database locally
sudo -u postgres psql -c "DROP DATABASE $DB"
sudo -u postgres psql -c "CREATE DATABASE $DB"
sudo -u postgres psql -c "GRANT CREATE ON DATABASE $DB TO $DB"

# Load tables from the production dump
sudo -u postgres psql $DB < $1
