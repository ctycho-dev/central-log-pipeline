#!/usr/bin/env python3
"""
Elasticsearch Manager - Check templates, indices, and logs
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configuration
ES_HOST = os.getenv('ES_HOST', 'http://localhost:9200')
ES_USER = 'elastic'
ES_PASSWORD = os.getenv('ELASTIC_PASSWORD')

if not ES_PASSWORD:
    print("❌ ELASTIC_PASSWORD not found in .env file")
    sys.exit(1)


def cluster_health():
    """Check cluster health"""
    url = f"{ES_HOST}/_cluster/health"
    response = requests.get(url, auth=(ES_USER, ES_PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        status = data['status']
        emoji = "🟢" if status == "green" else "🟡" if status == "yellow" else "🔴"
        print(f"{emoji} Cluster: {data['cluster_name']}")
        print(f"   Status: {status}")
        print(f"   Nodes: {data['number_of_nodes']}")
        print(f"   Total Indices: {data['active_primary_shards']}")
        print()
    else:
        print("❌ Could not connect to Elasticsearch")
        sys.exit(1)


def list_templates():
    """List all index templates"""
    url = f"{ES_HOST}/_index_template"
    response = requests.get(url, auth=(ES_USER, ES_PASSWORD))
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        sys.exit(1)
    
    data = response.json()
    templates = data.get('index_templates', [])
    
    # Filter out built-in templates (show only fastapi ones)
    custom_templates = [t for t in templates if 'fastapi' in t['name']]
    
    if not custom_templates:
        print("📋 No custom templates found (no fastapi-* templates)")
        return
    
    print(f"📋 Found {len(custom_templates)} custom template(s):\n")
    
    for tmpl in custom_templates:
        name = tmpl['name']
        patterns = tmpl['index_template']['index_patterns']
        priority = tmpl['index_template'].get('priority', 0)
        
        print(f"  • {name}")
        print(f"    Pattern: {', '.join(patterns)}")
        print(f"    Priority: {priority}")
        print()


def list_indices(pattern='fastapi-logs-*'):
    """List all indices matching pattern"""
    url = f"{ES_HOST}/_cat/indices/{pattern}?v&s=index"
    response = requests.get(url, auth=(ES_USER, ES_PASSWORD))
    
    if response.status_code == 404:
        print(f"📋 No indices found matching '{pattern}'")
        return
    elif response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        sys.exit(1)
    
    lines = response.text.strip().split('\n')
    
    if len(lines) <= 1:
        print(f"📋 No indices found matching '{pattern}'")
        return
    
    print(f"📋 Indices matching '{pattern}':\n")
    print(lines[0])  # Header
    print("-" * 100)
    
    for line in lines[1:]:
        print(line)
    print()


def get_logs(index_pattern='fastapi-logs-*', size=10):
    """Fetch last N logs sorted by timestamp"""
    
    query = {
        "size": size,
        "sort": [{"asctime": {"order": "desc"}}],
        "query": {"match_all": {}}
    }
    
    url = f"{ES_HOST}/{index_pattern}/_search"
    response = requests.post(url, auth=(ES_USER, ES_PASSWORD), json=query)
    
    if response.status_code == 404:
        print(f"📋 No indices found matching '{index_pattern}'")
        print("   (Logs haven't been sent to Elasticsearch yet)")
        return
    elif response.status_code != 200:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    data = response.json()
    hits = data.get('hits', {}).get('hits', [])
    
    if not hits:
        print(f"📋 No logs found in '{index_pattern}'")
        return
    
    print(f"📋 Last {len(hits)} logs from '{index_pattern}':\n")
    
    for hit in hits:
        source = hit['_source']
        
        # Format output
        timestamp = source.get('asctime', 'N/A')
        level = source.get('levelname', 'INFO')
        message = source.get('message', '')
        
        # Color codes
        level_colors = {
            'ERROR': '\033[91m',    # Red
            'WARNING': '\033[93m',  # Yellow
            'INFO': '\033[92m',     # Green
            'DEBUG': '\033[94m'     # Blue
        }
        reset = '\033[0m'
        color = level_colors.get(level, '')
        
        print(f"{color}[{timestamp}] {level}{reset} - {message}")
        
        # Show additional fields
        if 'request_id' in source:
            print(f"  Request: {source['request_id']}")
        if 'method' in source and 'path' in source:
            status = source.get('status_code', '?')
            print(f"  {source['method']} {source['path']} → {status}")
        if 'latency_s' in source:
            print(f"  Latency: {source['latency_s']}s")
        if 'user_email' in source and source['user_email']:
            print(f"  User: {source['user_email']}")
        
        print()


def show_help():
    """Show usage help"""
    print("""
Elasticsearch Manager - Manage templates, indices, and logs

Usage:
  python es-manager.py [command] [options]

Commands:
  health              Show cluster health
  templates           List all custom templates
  indices [pattern]   List indices (default: fastapi-logs-*)
  logs [pattern] [N]  Show last N logs (default: 10 from fastapi-logs-*)

Examples:
  python es-manager.py health
  python es-manager.py templates
  python es-manager.py indices
  python es-manager.py indices fastapi-logs-rag-chat-*
  python es-manager.py logs
  python es-manager.py logs fastapi-logs-* 50
    """)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show health + templates + indices
        cluster_health()
        list_templates()
        list_indices()
    else:
        command = sys.argv[1]
        
        if command == "health":
            cluster_health()
        
        elif command == "templates":
            cluster_health()
            list_templates()
        
        elif command == "indices":
            pattern = sys.argv[2] if len(sys.argv) > 2 else 'fastapi-logs-*'
            cluster_health()
            list_indices(pattern)
        
        elif command == "logs":
            pattern = sys.argv[2] if len(sys.argv) > 2 else 'fastapi-logs-*'
            size = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            get_logs(pattern, size)
        
        elif command in ["help", "-h", "--help"]:
            show_help()
        
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            sys.exit(1)
