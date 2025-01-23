#!/usr/bin/dumb-init /bin/bash

cleanup() {
  exit 0
}

trap cleanup SIGINT SIGTERM

while true; do
  /home/imio/bin/process_mails "$@"
  sleep 60
done
