#!/bin/sh
# node_modules lives in a Docker volume. Reinstall it whenever package-lock.json changes.
set -e
want=$(sha256sum package-lock.json | cut -d' ' -f1)
if [ "$(cat node_modules/.lock-hash 2>/dev/null)" != "$want" ]; then
  npm ci --no-audit --no-fund
  echo "$want" > node_modules/.lock-hash
fi
exec "$@"
