#!/bin/sh
# Drop, re-create and load a local NetBox database from a SQL dump, granting
# the role named after the database create on it and on schema public. The
# schema grant is required since PostgreSQL 15. Runs psql as the postgres
# superuser via sudo.
#
# Usage:   scripts/load_database.sh <dump.sql> [database=netbox]
# Example: scripts/load_database.sh netbox.sql

DB=${2:-netbox}

sudo -u postgres psql -c "DROP DATABASE $DB"
sudo -u postgres psql -c "CREATE DATABASE $DB"
sudo -u postgres psql -c "GRANT CREATE ON DATABASE $DB TO $DB"

# Load tables from the production dump
sudo -u postgres psql $DB < $1

# Grant after the load so a dump that re-creates schema public cannot undo it
sudo -u postgres psql -d $DB -c "GRANT CREATE ON SCHEMA public TO $DB"
