#!/usr/bin/env python3
"""Get last N logs from Elasticsearch"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

ES_HOST = os.getenv('ES_HOST', 'http://localhost:9200')
ES_PASSWORD = os.getenv('ELASTIC_PASSWORD')


def get_logs(index_pattern='fastapi-logs-*', size=10, full=False):
    """Fetch last N logs sorted by timestamp"""
    
    query = {
        "size": size,
        "sort": [{"asctime": {"order": "desc"}}],
        "query": {"match_all": {}}
    }
    
    url = f"{ES_HOST}/{index_pattern}/_search"
    response = requests.post(url, auth=('elastic', ES_PASSWORD), json=query)
    
    if response.status_code != 200:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    data = response.json()
    hits = data.get('hits', {}).get('hits', [])
    
    if not hits:
        print(f"📋 No logs found in '{index_pattern}'")
        return
    
    print(f"📋 Last {len(hits)} logs from '{index_pattern}':\n")
    
    for i, hit in enumerate(hits, 1):
        source = hit['_source']
        
        if full:
            # Print full JSON log
            print(f"{'='*80}")
            print(f"Log #{i} (Index: {hit['_index']})")
            print(f"{'='*80}")
            print(json.dumps(source, indent=2, ensure_ascii=False))
            print()
        else:
            # Format timestamp
            timestamp = source.get('asctime', 'N/A')
            level = source.get('levelname', 'INFO')
            message = source.get('message', '')
            
            # Color codes
            level_color = {
                'ERROR': '\033[91m',  # Red
                'WARNING': '\033[93m',  # Yellow
                'INFO': '\033[92m',  # Green
                'DEBUG': '\033[94m'  # Blue
            }
            reset = '\033[0m'
            
            color = level_color.get(level, '')
            
            print(f"{color}[{timestamp}] {level}{reset} - {message}")
            
            # Show key fields
            if 'request_id' in source and source['request_id']:
                print(f"  Request: {source['request_id']}")
            if 'method' in source and 'path' in source:
                print(f"  {source['method']} {source['path']} → {source.get('status_code', '?')}")
            if 'latency_s' in source:
                print(f"  Latency: {source['latency_s']}s")
            if 'user_email' in source and source['user_email']:
                print(f"  User: {source['user_email']}")
            
            print()


if __name__ == "__main__":
    # Parse arguments
    full_mode = '--full' in sys.argv or '-f' in sys.argv
    
    # Remove flags from args
    args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
    
    index = args[0] if len(args) > 0 else 'fastapi-logs-rag-chat-*'
    size = int(args[1]) if len(args) > 1 else 10
    
    get_logs(index, size, full=full_mode)
