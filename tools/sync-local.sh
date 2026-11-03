#!/bin/bash
# Copies the source (iCloud workspace) to the local copy the site runs from, then optionally starts it.
# The database, logs, uploaded media and build output stay in the local copy only.
# Usage: tools/sync-local.sh [run]
set -e
SOURCE="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$HOME/Projects/BroudoHoldings-local"
mkdir -p "$TARGET"
rsync -a --delete \
  --exclude bin/ --exclude obj/ --exclude umbraco/Data/ --exclude umbraco/Logs/ --exclude umbraco/mediacache/ \
  --exclude wwwroot/media/ --exclude .git/ --exclude .DS_Store \
  "$SOURCE/" "$TARGET/"
echo "Synced to $TARGET"
if [ "$1" = "run" ]; then
  cd "$TARGET" && exec dotnet run --launch-profile Umbraco.Web.UI
fi
