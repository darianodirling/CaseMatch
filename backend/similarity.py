import saspy
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimilaritySearcher:
    def __init__(self):
        self.sas = None
        self.cas_session = None
        self.topic_vectors_data = None
        
    def connect_to_viya(self) -> bool:
        """
        Connect to SAS Viya using saspy
        Returns True if connection successful, False otherwise
        """
        try:
            # Initialize SAS session with Viya configuration
            self.sas = saspy.SASsession(cfgname='viya')
            
            if self.sas is None:
                logger.error("Failed to create SAS session")
                return False
            
            # Test basic SAS functionality
            test_code = """
            proc options option=work;
            run;
            """
            result = self.sas.submit(test_code)
            
            if 'ERROR' in result['LOG']:
                logger.error(f"SAS session test failed: {result['LOG']}")
                return False
                
            # Connect to CAS server
            cas_code = """
            cas mySession;
            """
            result = self.sas.submit(cas_code)
            
            if 'ERROR' in result['LOG']:
                logger.warning(f"CAS connection failed: {result['LOG']}")
                # Try alternative CAS connection
                cas_code_alt = """
                cas;
                """
                result = self.sas.submit(cas_code_alt)
                if 'ERROR' in result['LOG']:
                    logger.warning("CAS connection failed, proceeding without CAS")
                else:
                    logger.info("Connected to CAS using default session")
            else:
                logger.info("Successfully connected to CAS")
                
            logger.info("Successfully connected to SAS Viya")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Viya: {str(e)}")
            return False
    
    def load_topic_vectors(self) -> bool:
        """
        Load the topic_vectors CAS table from casuser(daodir) library
        Returns True if successful, False otherwise
        """
        try:
            if self.sas is None:
                logger.error("SAS session not initialized")
                return False
            
            # First, try to access the table directly from your casuser library
            try:
                self.topic_vectors_data = self.sas.sasdata('topic_vectors', 'casuser').to_df()
                
                if self.topic_vectors_data is not None and not self.topic_vectors_data.empty:
                    logger.info(f"Successfully loaded {len(self.topic_vectors_data)} records from topic_vectors")
                    logger.info(f"Columns available: {list(self.topic_vectors_data.columns)}")
                    return True
                    
            except Exception as direct_error:
                logger.warning(f"Direct table access failed: {str(direct_error)}")
            
            # Alternative approach: Use CAS table operations
            cas_code = """
            proc casutil;
                list tables caslib="casuser";
            quit;
            
            data work.topic_vectors_temp;
                set casuser.topic_vectors;
            run;
            """
            
            result = self.sas.submit(cas_code)
            
            if 'ERROR' in result['LOG']:
                logger.error(f"Failed to access topic_vectors table: {result['LOG']}")
                return False
            
            # Try to get data through work library
            try:
                self.topic_vectors_data = self.sas.sasdata('topic_vectors_temp', 'work').to_df()
                
                if self.topic_vectors_data is not None and not self.topic_vectors_data.empty:
                    logger.info(f"Successfully loaded {len(self.topic_vectors_data)} records via work library")
                    logger.info(f"Columns available: {list(self.topic_vectors_data.columns)}")
                    return True
                else:
                    logger.error("No data retrieved from topic_vectors table")
                    return False
                    
            except Exception as work_error:
                logger.error(f"Failed to load data via work library: {str(work_error)}")
                return False
            
        except Exception as e:
            logger.error(f"Error loading topic vectors: {str(e)}")
            return False
    
    def calculate_similarity(self, case_number: str, top_k: int = 5) -> List[Dict]:
        """
        Calculate cosine similarity for a given case number
        
        Args:
            case_number: The case number to find similar cases for
            top_k: Number of top similar cases to return
            
        Returns:
            List of dictionaries containing similar cases with scores
        """
        try:
            if self.topic_vectors_data is None:
                logger.error("Topic vectors data not loaded")
                return []
            
            # Find the target case
            target_case = self.topic_vectors_data[
                self.topic_vectors_data['case_number'] == case_number
            ]
            
            if target_case.empty:
                logger.warning(f"Case number {case_number} not found in topic_vectors")
                return []
            
            # Extract vector columns (assuming they start with 'topic_' or 'vector_')
            vector_columns = [col for col in self.topic_vectors_data.columns 
                            if col.startswith(('topic_', 'vector_', 'dim_'))]
            
            if not vector_columns:
                logger.error("No vector columns found in topic_vectors data")
                return []
            
            # Get target vector
            target_vector = target_case[vector_columns].values
            
            # Get all vectors
            all_vectors = self.topic_vectors_data[vector_columns].values
            
            # Calculate cosine similarity
            similarities = cosine_similarity(target_vector, all_vectors)[0]
            
            # Create results with similarity scores
            results = []
            for idx, similarity_score in enumerate(similarities):
                row = self.topic_vectors_data.iloc[idx]
                
                # Skip the target case itself
                if row['case_number'] == case_number:
                    continue
                
                result = {
                    'case_number': row['case_number'],
                    'similarity_score': float(similarity_score),
                    'resolution': row.get('resolution', 'No resolution available'),
                    'title': row.get('title', row.get('description', 'No title available')),
                    'assignment_group': row.get('assignment_group', 'Unknown'),
                    'case_type': row.get('case_type', 'Unknown'),
                    'status': row.get('status', 'Unknown')
                }
                results.append(result)
            
            # Sort by similarity score and return top_k
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"Found {len(results[:top_k])} similar cases for {case_number}")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return []
    
    def disconnect(self):
        """Clean up connections"""
        try:
            if self.sas:
                self.sas.endsas()
                logger.info("SAS session ended")
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")

# Global instance
similarity_searcher = SimilaritySearcher()

def get_similar_cases(case_number: str, top_k: int = 5) -> List[Dict]:
    """
    Main function to get similar cases for a given case number
    
    Args:
        case_number: The case number to search for similar cases
        top_k: Number of top similar cases to return (default: 5)
        
    Returns:
        List of dictionaries containing similar cases with similarity scores
    """
    try:
        # Initialize connection if not already done
        if similarity_searcher.sas is None:
            if not similarity_searcher.connect_to_viya():
                logger.error("Failed to connect to SAS Viya")
                return []
        
        # Load data if not already loaded
        if similarity_searcher.topic_vectors_data is None:
            if not similarity_searcher.load_topic_vectors():
                logger.error("Failed to load topic vectors data")
                return []
        
        # Ensure data is available before calculating similarities
        if similarity_searcher.topic_vectors_data is not None and len(similarity_searcher.topic_vectors_data) > 0:
            return similarity_searcher.calculate_similarity(case_number, top_k)
        else:
            logger.error("No topic vectors data available for similarity calculation")
            return []
        
    except Exception as e:
        logger.error(f"Error in get_similar_cases: {str(e)}")
        return []

def test_connection():
    """Test function to verify SAS Viya connection"""
    try:
        searcher = SimilaritySearcher()
        if searcher.connect_to_viya():
            print("✓ SAS Viya connection successful")
            if searcher.load_topic_vectors():
                print("✓ Topic vectors loaded successfully")
                if searcher.topic_vectors_data is not None:
                    print(f"✓ Loaded {len(searcher.topic_vectors_data)} records")
                    return True
                else:
                    print("✗ No data in topic vectors")
            else:
                print("✗ Failed to load topic vectors")
        else:
            print("✗ SAS Viya connection failed")
        return False
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the connection and functionality
    test_connection()