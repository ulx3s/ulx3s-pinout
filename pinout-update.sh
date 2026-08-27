#!/usr/bin/env bash

if ! command -v inotifywait >/dev/null 2>&1; then
  printf '%s\n' "ERROR: inotifywait not found. Install with: sudo apt install inotify-tools" >&2
  exit 1
fi

while  [ 1 -eq 1 ]; do
  inotifywait -e modify styles.css pinout_ulx3s.py data.py
  echo "Change! $(date)"
  rm pinout_ulx3s.svg
  python3 -m pinout.manager --export pinout_ulx3s.py pinout_ulx3s.svg
done
