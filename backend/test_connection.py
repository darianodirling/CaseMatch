#!/usr/bin/env python3
"""
Test script to verify SAS Viya connection and topic_vectors table access
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing Python imports...")
    try:
        import saspy
        print("✓ saspy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import saspy: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        print("✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import scikit-learn: {e}")
        return False
    
    return True

def test_sas_connection():
    """Test SAS Viya connection"""
    print("\nTesting SAS Viya connection...")
    try:
        from similarity import SimilaritySearcher
        
        searcher = SimilaritySearcher()
        
        # Test connection
        if searcher.connect_to_viya():
            print("✓ Successfully connected to SAS Viya")
            
            # Test data loading
            if searcher.load_topic_vectors():
                print("✓ Successfully loaded topic_vectors table")
                
                # Show table info
                if searcher.topic_vectors_data is not None:
                    print(f"✓ Table contains {len(searcher.topic_vectors_data)} rows")
                    print(f"✓ Available columns: {list(searcher.topic_vectors_data.columns)}")
                    
                    # Show sample data
                    print("\nSample data (first 3 rows):")
                    print(searcher.topic_vectors_data.head(3))
                    
                    return True
                else:
                    print("✗ Table data is empty")
                    return False
            else:
                print("✗ Failed to load topic_vectors table")
                return False
        else:
            print("✗ Failed to connect to SAS Viya")
            return False
            
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)}")
        return False

def test_similarity_search():
    """Test similarity search functionality"""
    print("\nTesting similarity search...")
    try:
        from similarity import get_similar_cases
        
        # Test with a sample case number (you can modify this)
        test_case = "CS10023856"  # Replace with actual case number from your data
        
        print(f"Searching for cases similar to: {test_case}")
        results = get_similar_cases(test_case, top_k=3)
        
        if results:
            print(f"✓ Found {len(results)} similar cases")
            for i, case in enumerate(results, 1):
                print(f"  {i}. {case['case_number']} (similarity: {case['similarity_score']:.2f})")
            return True
        else:
            print("✗ No similar cases found (this may be normal if the test case doesn't exist)")
            return False
            
    except Exception as e:
        print(f"✗ Similarity search test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("CaseMatch Backend Connection Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return
    
    # Test SAS connection
    if not test_sas_connection():
        print("\n❌ SAS connection test failed.")
        print("   Check your .env file configuration")
        print("   Verify SAS Viya server is accessible")
        return
    
    # Test similarity search
    test_similarity_search()
    
    print("\n🎉 All tests completed!")
    print("Your backend is ready to use with the React frontend.")

if __name__ == "__main__":
    main()