#!/bin/sh

DB=${2:-netbox}

# Dump the database to a file
sudo -u postgres pg_dump $DB > $1

