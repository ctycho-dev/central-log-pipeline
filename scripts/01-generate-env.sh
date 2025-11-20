#!/bin/bash
echo "Setting up ELK environment..."

# Generate random passwords
ELASTIC_PASS=$(openssl rand -base64 32)
KIBANA_PASS=$(openssl rand -base64 32)
HEALTH_PASS=$(openssl rand -base64 32)

# Generate encryption keys
ENC_KEY=$(openssl rand -base64 32)
SAVED_KEY=$(openssl rand -base64 32)
REPORT_KEY=$(openssl rand -base64 32)

cat > .env << EOF
# Generated on $(date)
ELASTIC_PASSWORD=$ELASTIC_PASS
KIBANA_SYSTEM_PASSWORD=$KIBANA_PASS
HEALTHCHECK_PASSWORD=$HEALTH_PASS

KIBANA_ENCRYPTION_KEY=$ENC_KEY
KIBANA_SAVEDOBJ_KEY=$SAVED_KEY
KIBANA_REPORTING_KEY=$REPORT_KEY

# Add LOGSTASH_API_KEY after running create-api-key.sh
LOGSTASH_API_KEY=
EOF

echo "✅ Environment file created!"
echo "🔐 Passwords generated securely"
echo "👉 Next: Run 'docker compose up -d' then './scripts/create-api-key.sh'"
