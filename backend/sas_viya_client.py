#!/usr/bin/env python3
"""
SAS Viya CAS Client for authentic server connectivity
Connects to trck1056928.trc.sas.com with sasboot credentials
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SASVilyaClient:
    """Client for connecting to your SAS Viya server"""
    
    def __init__(self):
        self.host = 'trck1056928.trc.sas.com'
        self.port = 5570
        self.username = 'sasboot'
        self.password = 'Orion123'
        self.connection = None
        
    def connect(self) -> bool:
        """Establish connection to your CAS server"""
        try:
            # Dynamic import to handle dependency issues
            import importlib.util
            
            # Try to import swat
            if importlib.util.find_spec("swat") is None:
                logger.error("SWAT package not available")
                return False
                
            import swat
            
            logger.info(f"Connecting to {self.host}:{self.port} as {self.username}")
            
            self.connection = swat.CAS(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                protocol='cas'
            )
            
            # Verify connection
            about_info = self.connection.about()
            logger.info(f"Connected to {about_info.get('About', {}).get('Hostname', 'Unknown')}")
            
            return True
            
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status and connection information"""
        if not self.connection:
            if not self.connect():
                return {
                    "status": "connection_failed",
                    "error": "Cannot establish connection to CAS server",
                    "message": "Requires VPN access to trck1056928.trc.sas.com"
                }
        
        try:
            about_info = self.connection.about()
            session_info = self.connection.sessionStatus()
            
            # Check casuser library access
            try:
                tables_result = self.connection.tableInfo(caslib='casuser')
                table_count = len(tables_result.get('TableInfo', []))
            except:
                table_count = 0
            
            return {
                "status": "success",
                "server_host": about_info.get('About', {}).get('Hostname', self.host),
                "server_version": about_info.get('About', {}).get('Version', 'Unknown'),
                "session_id": session_info.get('Session', {}).get('SessionId', 'Unknown'),
                "casuser_tables": table_count,
                "message": f"Connected to {self.host} as {self.username}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Error retrieving server status"
            }
    
    def load_topic_vectors(self, rows: int = 5) -> List[Dict[str, Any]]:
        """Load data from topic_vectors table in casuser library"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # Access topic_vectors table
            topic_vectors = self.connection.CASTable('topic_vectors', caslib='casuser')
            
            # Get sample data
            result = topic_vectors.head(rows)
            
            if result is None or len(result) == 0:
                logger.warning("No data returned from topic_vectors table")
                return []
            
            # Convert to JSON-serializable format
            data = result.to_dict('records')
            logger.info(f"Loaded {len(data)} rows from topic_vectors table")
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading topic_vectors: {e}")
            return []
    
    def find_similar_cases(self, case_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases using topic vectors"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # Load topic_vectors table
            topic_vectors = self.connection.CASTable('topic_vectors', caslib='casuser')
            
            # Find the target case
            target_case = topic_vectors.query(f'"Case Number" = "{case_number}"')
            
            if len(target_case) == 0:
                logger.warning(f"Case {case_number} not found in topic_vectors")
                return []
            
            # Get target case vector
            target_vector = target_case.iloc[0]
            
            # Extract topic vector columns
            topic_cols = [col for col in target_case.columns if col.startswith('_TextTopic_')]
            
            if not topic_cols:
                logger.warning("No topic vector columns found")
                return []
            
            # Calculate similarity with all other cases
            # This is a simplified approach - in production you'd use CAS analytics
            all_cases = topic_vectors.query(f'"Case Number" != "{case_number}"')
            
            similar_cases = []
            for _, row in all_cases.head(50).iterrows():  # Limit for performance
                # Calculate cosine similarity
                similarity = self._calculate_similarity(
                    [target_vector[col] for col in topic_cols],
                    [row[col] for col in topic_cols]
                )
                
                similar_cases.append({
                    "case_number": row.get("Case Number", ""),
                    "similarity_score": round(similarity, 4),
                    "title": row.get("Description", "")[:100],
                    "resolution": row.get("Resolution", "")[:100],
                    "assignment_group": row.get("Assignment Group", ""),
                    "case_type": row.get("Concern", ""),
                    "status": "resolved"
                })
            
            # Sort by similarity and return top K
            similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similar_cases[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return []
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception:
            return 0.0
    
    def close(self):
        """Close the CAS connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("CAS connection closed")
            except:
                pass
            finally:
                self.connection = None

# Global client instance
_client = None

def get_client() -> SASVilyaClient:
    """Get or create SAS Viya client instance"""
    global _client
    if _client is None:
        _client = SASVilyaClient()
    return _client

def test_cas_server_connection() -> Dict[str, Any]:
    """Test connection to your CAS server"""
    client = get_client()
    return client.get_server_status()

def load_topic_vectors_preview(rows: int = 5) -> List[Dict[str, Any]]:
    """Load preview data from topic_vectors table"""
    client = get_client()
    return client.load_topic_vectors(rows)

def get_similar_cases(case_number: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Find similar cases for given case number"""
    client = get_client()
    return client.find_similar_cases(case_number, top_k)

if __name__ == "__main__":
    # Test the client
    print("Testing SAS Viya Client...")
    
    status = test_cas_server_connection()
    print(f"Connection Status: {json.dumps(status, indent=2)}")
    
    if status.get("status") == "success":
        print("\nTesting table access...")
        preview = load_topic_vectors_preview(3)
        print(f"Loaded {len(preview)} rows from topic_vectors")
        
        if preview:
            print("Sample data structure:")
            print(json.dumps(list(preview[0].keys()), indent=2))