#!/usr/bin/env python3
"""
CAS Connection Module for SAS Viya Integration
Provides reusable functions for connecting to CAS and accessing tables
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

def get_cas_connection():
    """
    Create and return a CAS connection using environment variables
    
    Returns:
        CAS connection object if successful
        
    Raises:
        CASConnectionError: If connection fails
    """
    try:
        import swat
        
        # Get credentials from environment
        cas_host = os.getenv('CAS_HOST')
        cas_port = int(os.getenv('CAS_PORT', 5570))
        cas_username = os.getenv('CAS_USERNAME')
        cas_password = os.getenv('CAS_PASSWORD')
        
        if not all([cas_host, cas_username, cas_password]):
            raise CASConnectionError("Missing required CAS credentials in environment variables")
        
        logger.info(f"Connecting to CAS server: {cas_host}:{cas_port}")
        
        # Create CAS connection
        conn = swat.CAS(
            hostname=cas_host,
            port=cas_port,
            username=cas_username,
            password=cas_password,
            protocol='cas'
        )
        
        # Test the connection
        server_info = conn.about()
        logger.info(f"Connected to CAS server: {server_info.get('About', {}).get('Version', 'Unknown')}")
        
        return conn
        
    except ImportError:
        raise CASConnectionError("SWAT package not installed. Install with: pip install swat")
    except Exception as e:
        raise CASConnectionError(f"Failed to connect to CAS server: {str(e)}")

def load_table_preview(table_name: str = "topic_vectors", library: str = None, rows: int = 5) -> List[Dict[str, Any]]:
    """
    Load preview data from a CAS table
    
    Args:
        table_name: Name of the table to preview
        library: CAS library name (defaults to environment variable)
        rows: Number of rows to return
        
    Returns:
        List of dictionaries representing table rows
        
    Raises:
        CASConnectionError: If connection or table access fails
    """
    conn = None
    try:
        # Get connection
        conn = get_cas_connection()
        
        # Use library from environment if not provided
        if library is None:
            library = os.getenv('CAS_LIBRARY', 'casuser')
        
        logger.info(f"Loading {rows} rows from {library}.{table_name}")
        
        # Check if table exists
        table_info = conn.tableInfo(caslib=library, name=table_name)
        if table_info.status_code != 0:
            raise CASConnectionError(f"Table {library}.{table_name} not found or not accessible")
        
        # Load table data
        table_ref = conn.CASTable(table_name, caslib=library)
        
        # Fetch first N rows
        result = table_ref.head(rows)
        
        if result is None or len(result) == 0:
            raise CASConnectionError(f"No data returned from {library}.{table_name}")
        
        # Convert to list of dictionaries
        data = result.to_dict('records')
        
        logger.info(f"Successfully loaded {len(data)} rows from {library}.{table_name}")
        return data
        
    except CASConnectionError:
        raise
    except Exception as e:
        raise CASConnectionError(f"Error loading table preview: {str(e)}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def test_cas_connection() -> Dict[str, Any]:
    """
    Test CAS connection and return status information
    
    Returns:
        Dictionary with connection status and server info
    """
    try:
        conn = get_cas_connection()
        
        # Get server information
        about_info = conn.about()
        session_info = conn.sessionStatus()
        
        conn.close()
        
        return {
            "status": "success",
            "server_version": about_info.get('About', {}).get('Version', 'Unknown'),
            "server_host": about_info.get('About', {}).get('Hostname', 'Unknown'),
            "session_id": session_info.get('Session', {}).get('SessionId', 'Unknown'),
            "message": "CAS connection successful"
        }
        
    except CASConnectionError as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "CAS connection failed"
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": f"Unexpected error: {str(e)}",
            "message": "CAS connection test failed"
        }

if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing CAS connection...")
    result = test_cas_connection()
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        print("\nTesting table preview...")
        try:
            preview_data = load_table_preview("topic_vectors", rows=3)
            print(f"Preview data: {len(preview_data)} rows")
            print(json.dumps(preview_data[0] if preview_data else {}, indent=2))
        except CASConnectionError as e:
            print(f"Table preview failed: {e}")