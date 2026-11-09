#!/usr/bin/env bash
set -euo pipefail
artifact=${1:?Pass the static artifact directory}
# Restrict values used by SSH/rsync's remote shell. No arbitrary remote commands.
[[ ${DH_HOST:-} =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]+$ ]]
[[ ${DH_USER:-} =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]]
[[ ${DH_PATH:-} =~ ^/home/${DH_USER}/[a-zA-Z0-9][a-zA-Z0-9._/-]*$ ]]
[[ "$DH_PATH" != *..* && "$DH_PATH" != */ && "$DH_PATH" != */./* ]]
[[ -f "$artifact/index.html" && -f "$artifact/.htaccess" && -f "$artifact/deployment.json" ]]
ssh_opts='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=20'
# The directory must be provisioned by the account owner, with an explicit marker.
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=20 \
  "$DH_USER@$DH_HOST" "test -f '$DH_PATH/.stmts-preview-root'"
# No --delete: preserve old hashed assets and unrelated server files. Upload index last.
rsync -az --delay-updates -e "$ssh_opts" --exclude=index.html --exclude=deployment.json \
  "$artifact/" "$DH_USER@$DH_HOST:$DH_PATH/"
rsync -az -e "$ssh_opts" "$artifact/index.html" "$DH_USER@$DH_HOST:$DH_PATH/index.html"
rsync -az -e "$ssh_opts" "$artifact/deployment.json" "$DH_USER@$DH_HOST:$DH_PATH/deployment.json"
