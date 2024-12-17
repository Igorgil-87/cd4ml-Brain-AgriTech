#!/bin/bash
set -e

host="$1"
shift
cmd="$@"

until pg_isready -h "$host"; do
  echo "PostgreSQL não está pronto - esperando..."
  sleep 2
done

exec $cmd