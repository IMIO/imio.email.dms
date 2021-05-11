#!/usr/bin/dumb-init /bin/bash

cleanup() {
  exit 0
}

trap cleanup SIGINT SIGTERM

while true; do
  /app/bin/process_mails "$@"
  sleep 60
done
