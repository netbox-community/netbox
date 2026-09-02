#!/bin/sh
# Dump a local NetBox database to a SQL file that load_database.sh can
# restore. Runs pg_dump as the postgres superuser via sudo, but the dump
# file is written by the invoking user.
#
# Usage:   scripts/save_database.sh <dump.sql> [database=netbox]
# Example: scripts/save_database.sh netbox.sql

DB=${2:-netbox}

sudo -u postgres pg_dump $DB > $1

