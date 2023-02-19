#!/bin/bash
set -e

psql -U "$POSTGRES_USER" -c "CREATE DATABASE $DB_NAME;"
