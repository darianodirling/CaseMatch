#!/usr/bin/env python3
"""
Final CAS connector for trck1056928.trc.sas.com
Uses subprocess isolation to avoid numpy conflicts
"""

import json
import subprocess
import sys
import os
import tempfile
from typing import Dict, List, Any

class CASConnector:
    """Connector for your SAS Viya server"""
    
    def __init__(self):
        self.host = 'trck1056928.trc.sas.com'
        self.port = 5570
        self.username = 'sasboot'
        self.password = 'Orion123'
    
    def _execute_cas_script(self, script_content: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute CAS script in isolated environment"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            # Clean environment
            env = os.environ.copy()
            env.pop('PYTHONPATH', None)
            
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, timeout=timeout, env=env)
            
            os.unlink(script_path)
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError:
                    return {"status": "parse_error", "output": result.stdout}
            else:
                return {"status": "execution_error", "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Connection timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to your CAS server"""
        script = f'''
import json
import sys

try:
    import swat
    
    conn = swat.CAS(
        hostname='{self.host}',
        port={self.port},
        username='{self.username}',
        password='{self.password}',
        protocol='cas'
    )
    
    about_info = conn.about()
    session_info = conn.sessionStatus()
    
    try:
        tables_result = conn.tableInfo(caslib='casuser')
        table_count = len(tables_result.get('TableInfo', []))
    except:
        table_count = 0
    
    result = {{
        "status": "success",
        "server_host": about_info.get('About', {{}}).get('Hostname', '{self.host}'),
        "server_version": about_info.get('About', {{}}).get('Version', 'Unknown'),
        "session_id": session_info.get('Session', {{}}).get('SessionId', 'Unknown'),
        "casuser_tables": table_count,
        "message": "Connected to {self.host} as {self.username}"
    }}
    
    conn.close()
    print(json.dumps(result))
    
except ImportError as e:
    result = {{
        "status": "import_error",
        "error": str(e),
        "message": "SWAT package unavailable"
    }}
    print(json.dumps(result))
    
except Exception as e:
    result = {{
        "status": "connection_failed",
        "error": str(e),
        "message": "Cannot connect to CAS server - requires VPN access"
    }}
    print(json.dumps(result))
'''
        
        return self._execute_cas_script(script)
    
    def load_topic_vectors(self, rows: int = 5) -> List[Dict[str, Any]]:
        """Load data from topic_vectors table"""
        script = f'''
import json
import sys

try:
    import swat
    
    conn = swat.CAS(
        hostname='{self.host}',
        port={self.port},
        username='{self.username}',
        password='{self.password}',
        protocol='cas'
    )
    
    topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
    result = topic_vectors.head({rows})
    
    if len(result) > 0:
        data = result.to_dict('records')
        print(json.dumps(data))
    else:
        print(json.dumps([]))
    
    conn.close()
    
except Exception as e:
    print(json.dumps([]))
'''
        
        result = self._execute_cas_script(script, timeout=60)
        if isinstance(result, list):
            return result
        elif result.get("status") == "parse_error":
            # Try to parse the output directly
            try:
                return json.loads(result.get("output", "[]"))
            except:
                return []
        return []
    
    def find_similar_cases(self, case_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases using cosine similarity"""
        script = f'''
import json
import math
import sys

try:
    import swat
    
    conn = swat.CAS(
        hostname='{self.host}',
        port={self.port},
        username='{self.username}',
        password='{self.password}',
        protocol='cas'
    )
    
    topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
    
    # Find target case
    target_case = topic_vectors.query(f'"Case Number" = "{case_number}"')
    
    if len(target_case) == 0:
        conn.close()
        print(json.dumps([]))
        sys.exit(0)
    
    target_row = target_case.iloc[0]
    topic_cols = [col for col in target_case.columns if col.startswith('_TextTopic_')]
    target_vector = [target_row[col] for col in topic_cols]
    
    # Get other cases
    other_cases = topic_vectors.query(f'"Case Number" != "{case_number}"')
    
    similar_cases = []
    for _, row in other_cases.head(100).iterrows():
        case_vector = [row[col] for col in topic_cols]
        
        # Cosine similarity
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
    
    similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    print(json.dumps(similar_cases[:{top_k}]))
    
    conn.close()
    
except Exception as e:
    print(json.dumps([]))
'''
        
        result = self._execute_cas_script(script, timeout=90)
        if isinstance(result, list):
            return result
        elif result.get("status") == "parse_error":
            try:
                return json.loads(result.get("output", "[]"))
            except:
                return []
        return []

# Global connector instance
_cas_connector = CASConnector()

# API functions for Node.js integration
def test_cas_server_connection():
    """Test connection to your CAS server"""
    return _cas_connector.test_connection()

def load_topic_vectors_preview(rows=5):
    """Load preview data from topic_vectors table"""
    return _cas_connector.load_topic_vectors(rows)

def get_similar_cases(case_number, top_k=5):
    """Find similar cases for given case number"""
    return _cas_connector.find_similar_cases(case_number, top_k)

if __name__ == "__main__":
    print("Final CAS Connector Test")
    print("=" * 50)
    print(f"Server: {_cas_connector.host}:{_cas_connector.port}")
    print(f"User: {_cas_connector.username}")
    print("=" * 50)
    
    # Test connection
    status = test_cas_server_connection()
    print("Connection Status:")
    print(json.dumps(status, indent=2))
    
    if status.get("status") == "success":
        print("\nTesting table access...")
        preview = load_topic_vectors_preview(3)
        print(f"Loaded {len(preview)} rows from topic_vectors")
        
        if preview:
            print("Sample columns:", list(preview[0].keys())[:10])
            
            # Test similarity search with first case
            if preview and preview[0].get("Case Number"):
                case_num = preview[0]["Case Number"]
                print(f"\nTesting similarity search for case {case_num}...")
                similar = get_similar_cases(case_num, 3)
                print(f"Found {len(similar)} similar cases")
    else:
        print("Connection failed - expected without VPN access to your server")