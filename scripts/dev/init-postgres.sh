#!/bin/bash
# Creates the test database and enables pgvector on both databases.
# Mounted into postgres via docker-entrypoint-initdb.d — runs once on fresh volumes.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE DATABASE intelli_test;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname intelli_test <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL
