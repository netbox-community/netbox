#!/bin/sh

DB=${1:-netbox}

# Drop and re-create the database locally
sudo -u postgres psql -c "drop database $DB"
sudo -u postgres psql -c "create database $DB"
