#!/bin/sh
# Drop and re-create a local NetBox database, granting the role named after
# it create on the database and on schema public. The schema grant is
# required since PostgreSQL 15. Runs psql as the postgres superuser via sudo.
#
# Usage:   scripts/drop_database.sh [database=netbox]
# Example: scripts/drop_database.sh

DB=${1:-netbox}

sudo -u postgres psql -c "drop database $DB"
sudo -u postgres psql -c "create database $DB"
sudo -u postgres psql -c "grant create on database $DB to $DB"
sudo -u postgres psql -d $DB -c "grant create on schema public to $DB"
