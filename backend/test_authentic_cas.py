#!/usr/bin/env python3
"""
Test authentic CAS connection to trck1056928.trc.sas.com
This script verifies connectivity to your SAS Viya server
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_cas_connection():
    """Test connection to your CAS server"""
    try:
        # Import SWAT for CAS connectivity
        import swat
        
        # Your server configuration
        cas_config = {
            'hostname': 'trck1056928.trc.sas.com',
            'port': 5570,
            'username': 'sasboot',
            'password': 'Orion123',
            'protocol': 'cas'
        }
        
        print(f"Connecting to {cas_config['hostname']}:{cas_config['port']}")
        print(f"Username: {cas_config['username']}")
        
        # Establish CAS connection
        conn = swat.CAS(**cas_config)
        
        # Get server information
        about_info = conn.about()
        session_info = conn.sessionStatus()
        
        print("✓ Connection established successfully")
        print(f"Server: {about_info.get('About', {}).get('Hostname', 'Unknown')}")
        print(f"Version: {about_info.get('About', {}).get('Version', 'Unknown')}")
        print(f"Session ID: {session_info.get('Session', {}).get('SessionId', 'Unknown')}")
        
        # Test casuser library access
        try:
            tables_result = conn.tableInfo(caslib='casuser')
            if 'TableInfo' in tables_result:
                table_count = len(tables_result['TableInfo'])
                print(f"✓ casuser library accessible: {table_count} tables found")
                
                # Look for topic_vectors table
                for table in tables_result['TableInfo']:
                    if table.get('Name', '').lower() == 'topic_vectors':
                        print("✓ topic_vectors table found")
                        break
                else:
                    print("⚠ topic_vectors table not found in casuser library")
            else:
                print("⚠ Could not access casuser library")
                
        except Exception as lib_error:
            print(f"⚠ Library access error: {lib_error}")
        
        # Test topic_vectors table access
        try:
            print("\nTesting topic_vectors table access...")
            topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
            
            # Get table info
            table_info = topic_vectors.tableInfo()
            if table_info.status_code == 0:
                rows = table_info.get('TableInfo', [{}])[0].get('Rows', 0)
                cols = table_info.get('TableInfo', [{}])[0].get('Columns', 0)
                print(f"✓ Table info: {rows} rows, {cols} columns")
                
                # Get column information
                column_info = topic_vectors.columnInfo()
                if column_info.status_code == 0:
                    columns = [col['Column'] for col in column_info['ColumnInfo']]
                    print(f"✓ Columns: {len(columns)} total")
                    
                    # Show key columns
                    key_columns = [col for col in columns if any(keyword in col.lower() 
                                                               for keyword in ['case', 'number', 'topic', 'description'])]
                    if key_columns:
                        print(f"Key columns: {key_columns}")
                
                # Load sample data
                sample = topic_vectors.head(3)
                if len(sample) > 0:
                    print(f"✓ Sample data loaded: {len(sample)} rows")
                    print(f"Sample columns: {list(sample.columns)[:5]}...")
                else:
                    print("⚠ No data returned from table")
                    
            else:
                print(f"⚠ Table access failed: {table_info.status}")
                
        except Exception as table_error:
            print(f"⚠ Table error: {table_error}")
        
        # Close connection
        conn.close()
        print("\n✓ Connection closed successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ SWAT package import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("This is expected without VPN access to your server")
        return False

def main():
    """Main test function"""
    print("Authentic CAS Connection Test")
    print("=" * 50)
    print("Testing connection to your SAS Viya server...")
    print("Host: trck1056928.trc.sas.com")
    print("Port: 5570")
    print("User: sasboot")
    print("=" * 50)
    
    success = test_cas_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Test completed successfully")
        print("Your SAS server is accessible and configured correctly")
    else:
        print("⚠ Test failed")
        print("This is expected in Replit environment without VPN access")
        print("Run this test locally with VPN for full functionality")

if __name__ == "__main__":
    main()