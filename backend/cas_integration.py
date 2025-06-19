#!/usr/bin/env python3
"""
Direct CAS integration for SAS Viya server
Connects to trck1056928.trc.sas.com using sasboot credentials
"""

import os
import json
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def test_cas_server_connection():
    """Test connection to CAS server and return status"""
    try:
        import swat
        
        cas_host = os.getenv('CAS_HOST', 'trck1056928.trc.sas.com')
        cas_port = int(os.getenv('CAS_PORT', 5570))
        cas_username = os.getenv('CAS_USERNAME', 'sasboot')
        cas_password = os.getenv('CAS_PASSWORD', 'Orion123')
        
        # Create CAS connection
        conn = swat.CAS(
            hostname=cas_host,
            port=cas_port,
            username=cas_username,
            password=cas_password,
            protocol='cas'
        )
        
        # Get server information
        about_info = conn.about()
        session_info = conn.sessionStatus()
        
        # Test table access
        try:
            tables_result = conn.tableInfo(caslib='casuser')
            table_count = len(tables_result['TableInfo']) if 'TableInfo' in tables_result else 0
        except:
            table_count = 0
        
        conn.close()
        
        return {
            "status": "success",
            "server_host": about_info.get('About', {}).get('Hostname', cas_host),
            "server_version": about_info.get('About', {}).get('Version', 'Unknown'),
            "session_id": session_info.get('Session', {}).get('SessionId', 'Unknown'),
            "casuser_tables": table_count,
            "message": f"Connected to {cas_host} as {cas_username}"
        }
        
    except ImportError:
        return {
            "status": "swat_missing",
            "error": "SWAT package not installed",
            "message": "Install with: pip install swat-cas"
        }
    except Exception as e:
        return {
            "status": "connection_failed", 
            "error": str(e),
            "message": f"Cannot connect to CAS server {cas_host}:{cas_port} - check network access and VPN"
        }

def load_topic_vectors_preview(rows=5):
    """Load preview data from topic_vectors table"""
    try:
        import swat
        
        cas_host = os.getenv('CAS_HOST', 'trck1056928.trc.sas.com')
        cas_port = int(os.getenv('CAS_PORT', 5570))
        cas_username = os.getenv('CAS_USERNAME', 'sasboot')
        cas_password = os.getenv('CAS_PASSWORD', 'Orion123')
        
        # Connect to CAS server
        conn = swat.CAS(
            hostname=cas_host,
            port=cas_port,
            username=cas_username,
            password=cas_password,
            protocol='cas'
        )
        
        # Access the topic_vectors table
        topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
        
        # Get first N rows
        result = topic_vectors.head(rows)
        
        if result is None or len(result) == 0:
            conn.close()
            return []
        
        # Convert to JSON-serializable format
        data = result.to_dict('records')
        conn.close()
        
        return data
        
    except ImportError:
        # Return empty list if SWAT not available
        return []
    except Exception as e:
        # Return empty list on connection failure
        return []

if __name__ == "__main__":
    # Test the connection
    print("Testing CAS connection...")
    status = test_cas_server_connection()
    print(json.dumps(status, indent=2))
    
    if status["status"] == "success":
        print("\nTesting table access...")
        preview = load_topic_vectors_preview(3)
        print(f"Loaded {len(preview)} rows from topic_vectors")