#!/bin/bash
set -euo pipefail

source .env

echo "⏳ Creating healthcheck user..."

# Create role
curl -sf -u "elastic:${ELASTIC_PASSWORD}" \
  -H "Content-Type: application/json" \
  -X PUT http://localhost:9200/_security/role/healthcheck \
  -d '{"cluster":["monitor"],"indices":[]}'

# Create user
curl -sf -u "elastic:${ELASTIC_PASSWORD}" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:9200/_security/user/healthcheck \
  -d "{\"password\":\"${HEALTHCHECK_PASSWORD}\",\"roles\":[\"healthcheck\"]}"

echo "✅ healthcheck user created!"
