#!/bin/bash
set -euo pipefail

source .env

ES_URL="http://localhost:9200"
TEMPLATE_NAME="fastapi-logs-rag-chat-template"
TEMPLATE_FILE="templates/rag-chat-template.json"

if [[ ! -f "${TEMPLATE_FILE}" ]]; then
  echo "❌ Template file not found: ${TEMPLATE_FILE}"
  exit 1
fi

echo "➡️ Creating index template '${TEMPLATE_NAME}'..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -u "elastic:${ELASTIC_PASSWORD}" \
  -H "Content-Type: application/json" \
  -X PUT "${ES_URL}/_index_template/${TEMPLATE_NAME}" \
  -d @"${TEMPLATE_FILE}")

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ Template '${TEMPLATE_NAME}' created!"
else
  echo "❌ Failed with HTTP code: $HTTP_CODE"
  exit 1
fi
