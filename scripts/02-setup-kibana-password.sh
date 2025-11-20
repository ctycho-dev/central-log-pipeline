#!/bin/bash
set -euo pipefail

source .env

echo "⏳ Setting kibana_system password..."

curl -sf -u "elastic:${ELASTIC_PASSWORD}" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:9200/_security/user/kibana_system/_password \
  -d "{\"password\":\"${KIBANA_SYSTEM_PASSWORD}\"}"

echo "✅ kibana_system password set!"
