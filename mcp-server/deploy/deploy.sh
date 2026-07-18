#!/usr/bin/env bash
# Deploys the JVTO destinations MCP server (Streamable HTTP) to a VPS under pm2.
#
# Ships two things to the remote host, preserving their relative layout so
# mcp-server's bundle.ts path resolution (../../okf/bundles/jvto, relative to
# its own compiled location) keeps working unmodified on the remote host:
#   REMOTE_PATH/okf/bundles/jvto/   <- the public bundle data (read-only)
#   REMOTE_PATH/mcp-server/         <- this app (built + started via pm2)
#
# Usage:
#   DEPLOY_HOST=1.2.3.4 DEPLOY_USER=root ./deploy/deploy.sh
#
# Env vars:
#   DEPLOY_HOST   (required) VPS hostname or IP
#   DEPLOY_USER   (required) SSH user
#   DEPLOY_PORT   (optional) SSH port, default 22
#   REMOTE_PATH   (optional) deploy root on the VPS, default /var/www/okf-mcp

set -euo pipefail

: "${DEPLOY_HOST:?set DEPLOY_HOST (VPS hostname or IP)}"
: "${DEPLOY_USER:?set DEPLOY_USER (SSH user)}"
DEPLOY_PORT="${DEPLOY_PORT:-22}"
REMOTE_PATH="${REMOTE_PATH:-/var/www/okf-mcp}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SSH_TARGET="$DEPLOY_USER@$DEPLOY_HOST"

echo "==> Ensuring remote directory exists"
ssh -p "$DEPLOY_PORT" "$SSH_TARGET" "mkdir -p '$REMOTE_PATH/okf/bundles' '$REMOTE_PATH/mcp-server'"

echo "==> Syncing public bundle data (okf/bundles/jvto)"
rsync -avz --delete -e "ssh -p $DEPLOY_PORT" \
  "$REPO_ROOT/okf/bundles/jvto/" \
  "$SSH_TARGET:$REMOTE_PATH/okf/bundles/jvto/"

echo "==> Syncing mcp-server app code"
rsync -avz --delete \
  --exclude node_modules \
  --exclude dist \
  -e "ssh -p $DEPLOY_PORT" \
  "$REPO_ROOT/mcp-server/" \
  "$SSH_TARGET:$REMOTE_PATH/mcp-server/"

echo "==> Installing, building, and (re)starting via pm2 on the VPS"
ssh -p "$DEPLOY_PORT" "$SSH_TARGET" bash -s -- "$REMOTE_PATH" <<'REMOTE'
set -euo pipefail
REMOTE_PATH="$1"
cd "$REMOTE_PATH/mcp-server"
npm install
npm run build
command -v pm2 >/dev/null 2>&1 || npm install -g pm2
pm2 startOrReload ecosystem.config.cjs
pm2 save
REMOTE

echo "==> Health check"
ssh -p "$DEPLOY_PORT" "$SSH_TARGET" "curl -sf http://127.0.0.1:3300/healthz && echo"
