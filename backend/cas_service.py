#!/usr/bin/env python3
"""
CAS Service for SAS Viya Integration
Handles connection to trck1056928.trc.sas.com with proper error handling
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CASService:
    """Service for connecting to your SAS Viya server"""
    
    def __init__(self):
        self.config = {
            'hostname': 'trck1056928.trc.sas.com',
            'port': 5570,
            'username': 'sasboot',
            'password': 'Orion123',
            'protocol': 'cas'
        }
        self.is_available = self._check_swat_availability()
    
    def _check_swat_availability(self) -> bool:
        """Check if SWAT package is available for CAS connectivity"""
        try:
            import swat
            return True
        except ImportError:
            logger.warning("SWAT package not available - CAS functionality disabled")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to your CAS server"""
        if not self.is_available:
            return {
                "status": "unavailable",
                "error": "SWAT package not available",
                "message": "CAS connectivity requires SWAT package installation",
                "server_info": {
                    "host": self.config['hostname'],
                    "port": self.config['port'],
                    "username": self.config['username']
                }
            }
        
        try:
            import swat
            
            # Attempt connection to your server
            conn = swat.CAS(**self.config)
            
            # Get server information
            about_info = conn.about()
            session_info = conn.sessionStatus()
            
            # Test casuser library access
            try:
                tables_result = conn.tableInfo(caslib='casuser')
                table_count = len(tables_result.get('TableInfo', []))
            except Exception:
                table_count = 0
            
            conn.close()
            
            return {
                "status": "connected",
                "server_host": about_info.get('About', {}).get('Hostname', self.config['hostname']),
                "server_version": about_info.get('About', {}).get('Version', 'Unknown'),
                "session_id": session_info.get('Session', {}).get('SessionId', 'Unknown'),
                "casuser_tables": table_count,
                "message": f"Successfully connected to {self.config['hostname']}"
            }
            
        except Exception as e:
            return {
                "status": "connection_failed",
                "error": str(e),
                "message": f"Cannot connect to {self.config['hostname']} - requires VPN access",
                "server_info": {
                    "host": self.config['hostname'],
                    "port": self.config['port'],
                    "username": self.config['username']
                }
            }
    
    def load_topic_vectors(self, rows: int = 5) -> List[Dict[str, Any]]:
        """Load data from topic_vectors table in casuser library"""
        if not self.is_available:
            logger.warning("SWAT package not available - returning empty data")
            return []
        
        try:
            import swat
            
            conn = swat.CAS(**self.config)
            topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
            
            # Get sample data
            result = topic_vectors.head(rows)
            
            if len(result) > 0:
                data = result.to_dict('records')
                logger.info(f"Loaded {len(data)} rows from topic_vectors table")
                conn.close()
                return data
            else:
                logger.warning("No data returned from topic_vectors table")
                conn.close()
                return []
                
        except Exception as e:
            logger.error(f"Error loading topic_vectors: {e}")
            return []
    
    def find_similar_cases(self, case_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases using topic vectors from your server"""
        if not self.is_available:
            logger.warning("SWAT package not available - similarity search disabled")
            return []
        
        try:
            import swat
            import math
            
            conn = swat.CAS(**self.config)
            topic_vectors = conn.CASTable('topic_vectors', caslib='casuser')
            
            # Find target case
            target_case = topic_vectors.query(f'"Case Number" = "{case_number}"')
            
            if len(target_case) == 0:
                logger.warning(f"Case {case_number} not found in topic_vectors")
                conn.close()
                return []
            
            # Get target case vector
            target_row = target_case.iloc[0]
            topic_cols = [col for col in target_case.columns if col.startswith('_TextTopic_')]
            
            if not topic_cols:
                logger.warning("No topic vector columns found")
                conn.close()
                return []
            
            target_vector = [target_row[col] for col in topic_cols]
            
            # Get other cases for comparison
            other_cases = topic_vectors.query(f'"Case Number" != "{case_number}"')
            
            similar_cases = []
            for _, row in other_cases.head(100).iterrows():  # Limit for performance
                case_vector = [row[col] for col in topic_cols]
                
                # Calculate cosine similarity
                dot_product = sum(a * b for a, b in zip(target_vector, case_vector))
                magnitude1 = math.sqrt(sum(a * a for a in target_vector))
                magnitude2 = math.sqrt(sum(a * a for a in case_vector))
                
                if magnitude1 > 0 and magnitude2 > 0:
                    similarity = dot_product / (magnitude1 * magnitude2)
                else:
                    similarity = 0.0
                
                similar_cases.append({
                    "case_number": str(row.get("Case Number", "")),
                    "similarity_score": round(similarity, 4),
                    "title": str(row.get("Description", ""))[:100],
                    "resolution": str(row.get("Resolution", ""))[:100],
                    "assignment_group": str(row.get("Assignment Group", "")),
                    "case_type": str(row.get("Concern", "")),
                    "status": "resolved"
                })
            
            # Sort by similarity and return top K
            similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
            conn.close()
            
            logger.info(f"Found {len(similar_cases[:top_k])} similar cases for {case_number}")
            return similar_cases[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return []

# Global service instance
_cas_service = CASService()

# API functions for integration
def test_cas_server_connection():
    """Test connection to your CAS server"""
    return _cas_service.test_connection()

def load_topic_vectors_preview(rows=5):
    """Load preview data from topic_vectors table"""
    return _cas_service.load_topic_vectors(rows)

def get_similar_cases(case_number, top_k=5):
    """Find similar cases for given case number"""
    return _cas_service.find_similar_cases(case_number, top_k)

if __name__ == "__main__":
    print("CAS Service Test")
    print("=" * 50)
    print(f"Server: {_cas_service.config['hostname']}:{_cas_service.config['port']}")
    print(f"Username: {_cas_service.config['username']}")
    print(f"SWAT Available: {_cas_service.is_available}")
    print("=" * 50)
    
    # Test connection
    status = test_cas_server_connection()
    print("Connection Status:")
    print(json.dumps(status, indent=2))
    
    if status.get("status") == "connected":
        print("\nTesting table access...")
        preview = load_topic_vectors_preview(3)
        print(f"Loaded {len(preview)} rows from topic_vectors")
        
        if preview:
            print("Sample columns:", list(preview[0].keys())[:8])
    else:
        print("\nConnection not available - expected in development environment")
        print("Deploy with VPN access for full CAS functionality")