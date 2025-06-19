#!/usr/bin/env python3
"""
Clean test for CAS connectivity without numpy conflicts
Direct connection to trck1056928.trc.sas.com
"""

import os
import sys
import tempfile
import subprocess
import json

def create_isolated_cas_test():
    """Create isolated Python script for CAS testing"""
    test_script = '''
#!/usr/bin/env python3
import sys
import json

def test_cas_connection():
    try:
        import swat
        
        # Connect to your SAS server
        conn = swat.CAS(
            hostname='trck1056928.trc.sas.com',
            port=5570,
            username='sasboot',
            password='Orion123',
            protocol='cas'
        )
        
        # Get server info
        about_info = conn.about()
        session_info = conn.sessionStatus()
        
        # Test casuser library
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
            "message": "Connected successfully to your SAS server"
        }
        
        conn.close()
        return result
        
    except ImportError as e:
        return {
            "status": "import_error",
            "error": str(e),
            "message": "SWAT package not available"
        }
    except Exception as e:
        return {
            "status": "connection_failed",
            "error": str(e),
            "message": "Cannot connect - requires VPN access to trck1056928.trc.sas.com"
        }

def test_topic_vectors(rows=3):
    try:
        import swat
        
        conn = swat.CAS(
            hostname='trck1056928.trc.sas.com',
            port=5570,
            username='sasboot',
            password='Orion123',
            protocol='cas'
        )
        
        # Access topic_vectors table
        topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
        result = topic_vectors.head(rows)
        
        if len(result) > 0:
            data = result.to_dict('records')
            conn.close()
            return {
                "status": "success",
                "rows_loaded": len(data),
                "columns": list(data[0].keys()) if data else [],
                "sample_data": data[:2]  # Return first 2 rows
            }
        else:
            conn.close()
            return {"status": "no_data", "message": "No data in topic_vectors table"}
            
    except Exception as e:
        return {
            "status": "table_error",
            "error": str(e),
            "message": "Cannot access topic_vectors table"
        }

if __name__ == "__main__":
    print("Testing connection to your SAS server...")
    
    # Test connection
    conn_result = test_cas_connection()
    print(json.dumps(conn_result, indent=2))
    
    if conn_result.get("status") == "success":
        print("\\nTesting topic_vectors table...")
        table_result = test_topic_vectors()
        print(json.dumps(table_result, indent=2))
'''
    
    return test_script

def run_isolated_test():
    """Run CAS test in isolated environment"""
    try:
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(create_isolated_cas_test())
            script_path = f.name
        
        # Run in clean environment
        env = os.environ.copy()
        # Remove problematic paths
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']
        
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=45, env=env)
        
        # Clean up
        os.unlink(script_path)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Connection timeout - server may be unreachable",
            "returncode": 1
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Test execution failed: {str(e)}",
            "returncode": 1
        }

if __name__ == "__main__":
    print("Clean CAS Connectivity Test")
    print("=" * 50)
    print("Testing connection to trck1056928.trc.sas.com")
    print("Username: sasboot")
    print("Port: 5570")
    print("=" * 50)
    
    result = run_isolated_test()
    
    print("STDOUT:")
    print(result["stdout"])
    
    if result["stderr"]:
        print("\nSTDERR:")
        print(result["stderr"])
    
    print(f"\nReturn Code: {result['returncode']}")
    
    if result["returncode"] == 0:
        print("\n✓ Test completed successfully")
    else:
        print("\n⚠ Test failed - expected without VPN access")