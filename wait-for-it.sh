#!/usr/bin/env bash
# Use: ./wait-for-it.sh host:port -- command args
# Source: https://github.com/vishnubob/wait-for-it (MIT License)

set -e

HOSTPORT=$1
shift

HOST=$(echo $HOSTPORT | cut -d: -f1)
PORT=$(echo $HOSTPORT | cut -d: -f2)

TIMEOUT=60

for i in $(seq $TIMEOUT); do
    nc -z $HOST $PORT && break
    echo "Waiting for $HOST:$PORT... ($i/$TIMEOUT)"
    sleep 1
done

if ! nc -z $HOST $PORT; then
    echo "Timeout waiting for $HOST:$PORT"
    exit 1
fi

exec "$@"
