#!/usr/bin/env python3
"""
Production CAS connection for your SAS Viya server
Connects to trck1056928.trc.sas.com using sasboot credentials
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class CASConnectionError(Exception):
    """Custom exception for CAS connection issues"""
    pass

def connect_to_cas():
    """
    Connect to your CAS server using environment credentials
    """
    try:
        import swat
        
        cas_host = os.getenv('CAS_HOST', 'trck1056928.trc.sas.com')
        cas_port = int(os.getenv('CAS_PORT', 5570))
        cas_username = os.getenv('CAS_USERNAME', 'sasboot')
        cas_password = os.getenv('CAS_PASSWORD', 'Orion123')
        
        logger.info(f"Connecting to CAS server: {cas_host}:{cas_port}")
        
        # Create CAS connection
        conn = swat.CAS(
            hostname=cas_host,
            port=cas_port,
            username=cas_username,
            password=cas_password,
            protocol='cas'
        )
        
        # Verify connection
        about_info = conn.about()
        logger.info(f"Connected to CAS server version: {about_info.get('About', {}).get('Version', 'Unknown')}")
        
        return conn
        
    except ImportError:
        # Install SWAT if needed
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "swat-cas"])
            import swat
            # Retry connection after installation
            return connect_to_cas()
        except Exception as install_error:
            raise CASConnectionError(f"SWAT package installation failed: {install_error}")
    except Exception as e:
        raise CASConnectionError(f"Failed to connect to CAS server {cas_host}:{cas_port} - {str(e)}")

def load_topic_vectors_preview(rows: int = 5) -> List[Dict[str, Any]]:
    """
    Load preview data from topic_vectors table in casuser library
    
    Args:
        rows: Number of rows to return (default 5)
        
    Returns:
        List of dictionaries representing table rows from your server
    """
    conn = None
    try:
        # Connect to your CAS server
        conn = connect_to_cas()
        
        # Access the topic_vectors table from casuser library
        logger.info(f"Loading {rows} rows from casuser.topic_vectors")
        
        # Load the table
        topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
        
        # Get first N rows
        result = topic_vectors.head(rows)
        
        if result is None or len(result) == 0:
            raise CASConnectionError("No data returned from topic_vectors table")
        
        # Convert to JSON-serializable format
        data = result.to_dict('records')
        
        logger.info(f"Successfully loaded {len(data)} rows from topic_vectors")
        return data
        
    except Exception as e:
        raise CASConnectionError(f"Error loading topic_vectors preview: {str(e)}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def test_cas_server_connection() -> Dict[str, Any]:
    """
    Test connection to your CAS server and return status
    """
    try:
        conn = connect_to_cas()
        
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
            "server_host": about_info.get('About', {}).get('Hostname', 'Unknown'),
            "server_version": about_info.get('About', {}).get('Version', 'Unknown'),
            "session_id": session_info.get('Session', {}).get('SessionId', 'Unknown'),
            "casuser_tables": table_count,
            "message": f"Connected to {os.getenv('CAS_HOST')} as {os.getenv('CAS_USERNAME')}"
        }
        
    except CASConnectionError as e:
        return {
            "status": "connection_failed",
            "error": str(e),
            "message": "Cannot connect to CAS server - check network access and VPN"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Unexpected error during connection test"
        }

if __name__ == "__main__":
    # Test the CAS connection
    print("Testing CAS connection to your server...")
    result = test_cas_server_connection()
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        print("\nTesting topic_vectors table access...")
        try:
            preview = load_topic_vectors_preview(3)
            print(f"Successfully loaded {len(preview)} rows")
            if preview:
                print("Sample row structure:")
                print(json.dumps(list(preview[0].keys()), indent=2))
        except Exception as e:
            print(f"Table access failed: {e}")