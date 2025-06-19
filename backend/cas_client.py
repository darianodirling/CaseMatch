#!/usr/bin/env python3
"""
Clean CAS client for your SAS Viya server
Direct connection to trck1056928.trc.sas.com without numpy conflicts
"""

import json
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional

def test_swat_availability() -> bool:
    """Test if SWAT package can be imported cleanly"""
    try:
        # Use subprocess to avoid numpy import conflicts
        result = subprocess.run([
            sys.executable, '-c', 
            'import swat; print("SWAT_AVAILABLE")'
        ], capture_output=True, text=True, timeout=10)
        
        return "SWAT_AVAILABLE" in result.stdout
    except:
        return False

def connect_to_cas_server() -> Dict[str, Any]:
    """Connect to your CAS server and return status"""
    if not test_swat_availability():
        return {
            "status": "swat_unavailable",
            "error": "SWAT package cannot be imported",
            "message": "Package conflicts prevent CAS connection"
        }
    
    # Create connection script
    connection_script = '''
import swat
import json
import sys

try:
    # Your server configuration
    conn = swat.CAS(
        hostname='trck1056928.trc.sas.com',
        port=5570,
        username='sasboot',
        password='Orion123',
        protocol='cas'
    )
    
    # Get server information
    about_info = conn.about()
    session_info = conn.sessionStatus()
    
    # Test table access
    try:
        tables_result = conn.tableInfo(caslib='casuser')
        table_count = len(tables_result.get('TableInfo', []))
    except:
        table_count = 0
    
    result = {
        "status": "success",
        "server_host": about_info.get('About', {}).get('Hostname', 'trck1056928.trc.sas.com'),
        "server_version": about_info.get('About', {}).get('Version', 'Unknown'),
        "session_id": session_info.get('Session', {}).get('SessionId', 'Unknown'),
        "casuser_tables": table_count,
        "message": "Connected to trck1056928.trc.sas.com as sasboot"
    }
    
    conn.close()
    print(json.dumps(result))
    
except Exception as e:
    error_result = {
        "status": "connection_failed",
        "error": str(e),
        "message": "Cannot connect to CAS server - requires VPN access to trck1056928.trc.sas.com"
    }
    print(json.dumps(error_result))
'''
    
    try:
        result = subprocess.run([
            sys.executable, '-c', connection_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            return {
                "status": "execution_failed",
                "error": result.stderr,
                "message": "Failed to execute CAS connection script"
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Connection attempt timed out",
            "message": "Server may be unreachable without VPN"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Unexpected error during connection test"
        }

def load_topic_vectors_data(rows: int = 5) -> List[Dict[str, Any]]:
    """Load data from topic_vectors table"""
    if not test_swat_availability():
        return []
    
    # Create data loading script
    data_script = f'''
import swat
import json
import sys

try:
    # Connect to your CAS server
    conn = swat.CAS(
        hostname='trck1056928.trc.sas.com',
        port=5570,
        username='sasboot',
        password='Orion123',
        protocol='cas'
    )
    
    # Access topic_vectors table
    topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
    
    # Get sample data
    result = topic_vectors.head({rows})
    
    if len(result) > 0:
        # Convert to JSON-serializable format
        data = result.to_dict('records')
        print(json.dumps(data))
    else:
        print(json.dumps([]))
    
    conn.close()
    
except Exception as e:
    print(json.dumps([]))
'''
    
    try:
        result = subprocess.run([
            sys.executable, '-c', data_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            return []
    except:
        return []

def find_similar_cases_data(case_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Find similar cases using topic vectors from your server"""
    if not test_swat_availability():
        return []
    
    similarity_script = f'''
import swat
import json
import math
import sys

try:
    # Connect to CAS server
    conn = swat.CAS(
        hostname='trck1056928.trc.sas.com',
        port=5570,
        username='sasboot',
        password='Orion123',
        protocol='cas'
    )
    
    # Load topic_vectors table
    topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
    
    # Find target case
    target_case = topic_vectors.query(f'"Case Number" = "{case_number}"')
    
    if len(target_case) == 0:
        print(json.dumps([]))
        conn.close()
        sys.exit(0)
    
    # Get target vector
    target_row = target_case.iloc[0]
    topic_cols = [col for col in target_case.columns if col.startswith('_TextTopic_')]
    target_vector = [target_row[col] for col in topic_cols]
    
    # Get other cases for comparison
    other_cases = topic_vectors.query(f'"Case Number" != "{case_number}"')
    
    similar_cases = []
    for _, row in other_cases.head(100).iterrows():  # Limit for performance
        # Calculate cosine similarity
        case_vector = [row[col] for col in topic_cols]
        
        # Cosine similarity calculation
        dot_product = sum(a * b for a, b in zip(target_vector, case_vector))
        magnitude1 = math.sqrt(sum(a * a for a in target_vector))
        magnitude2 = math.sqrt(sum(a * a for a in case_vector))
        
        if magnitude1 > 0 and magnitude2 > 0:
            similarity = dot_product / (magnitude1 * magnitude2)
        else:
            similarity = 0.0
        
        similar_cases.append({{
            "case_number": str(row.get("Case Number", "")),
            "similarity_score": round(similarity, 4),
            "title": str(row.get("Description", ""))[:100],
            "resolution": str(row.get("Resolution", ""))[:100],
            "assignment_group": str(row.get("Assignment Group", "")),
            "case_type": str(row.get("Concern", "")),
            "status": "resolved"
        }})
    
    # Sort by similarity and return top K
    similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    print(json.dumps(similar_cases[:{top_k}]))
    
    conn.close()
    
except Exception as e:
    print(json.dumps([]))
'''
    
    try:
        result = subprocess.run([
            sys.executable, '-c', similarity_script
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            return []
    except:
        return []

# Main API functions for Node.js integration
def test_cas_server_connection():
    """Test connection to your CAS server"""
    return connect_to_cas_server()

def load_topic_vectors_preview(rows=5):
    """Load preview data from topic_vectors table"""
    return load_topic_vectors_data(rows)

def get_similar_cases(case_number, top_k=5):
    """Find similar cases for given case number"""
    return find_similar_cases_data(case_number, top_k)

if __name__ == "__main__":
    # Test the CAS client
    print("Testing CAS Client for your SAS server...")
    print("Host: trck1056928.trc.sas.com")
    print("Port: 5570") 
    print("User: sasboot")
    print("-" * 50)
    
    # Test connection
    status = test_cas_server_connection()
    print(f"Connection Status: {json.dumps(status, indent=2)}")
    
    if status.get("status") == "success":
        print("\nTesting table access...")
        preview = load_topic_vectors_preview(3)
        print(f"Loaded {len(preview)} rows from topic_vectors table")
        
        if preview:
            print("Table structure:")
            print(f"Columns: {list(preview[0].keys())}")
    else:
        print("Connection failed - expected without VPN access to your server")