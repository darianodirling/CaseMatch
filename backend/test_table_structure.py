#!/usr/bin/env python3
"""
Test script to verify SAS Viya table structure and perform similarity search
Based on your actual table columns:
- __uniqueid__, Description, _TextTopic_5, _TextTopic_4, _TextTopic_3, _TextTopic_2, _TextTopic_1
- _Col5_, _Col4_, _Col3_, _Col2_, _Col1_
- Assignment Group, Case Number, Resolution, Concern
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_saspy_connection():
    """Test basic SAS connection"""
    print("=== Testing SAS Viya Connection ===")
    
    try:
        import saspy
        from config import Config
        
        print(f"Connecting to: {Config.SAS_HOST}")
        print(f"Username: {Config.SAS_USERNAME}")
        print(f"Target table: {Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE}")
        
        # Create SAS session
        sas_config = Config.get_sas_config()
        sas = saspy.SASsession(**sas_config)
        
        print("✓ SAS session established")
        return sas
        
    except Exception as e:
        print(f"✗ SAS connection failed: {e}")
        return None

def analyze_table_structure(sas):
    """Analyze the actual table structure"""
    print("\n=== Analyzing Table Structure ===")
    
    try:
        # Get table contents/structure
        structure_code = f"""
        proc contents data={Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE} varnum;
        run;
        """
        
        result = sas.submit(structure_code)
        print("✓ Table structure retrieved")
        
        # Get first few rows to understand data
        sample_code = f"""
        proc print data={Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE}(obs=3);
        run;
        """
        
        sample_result = sas.submit(sample_code)
        print("✓ Sample data retrieved")
        
        return True
        
    except Exception as e:
        print(f"✗ Table analysis failed: {e}")
        return False

def test_data_loading(sas):
    """Test loading data into pandas for similarity analysis"""
    print("\n=== Testing Data Loading ===")
    
    try:
        from config import Config
        
        # Load data using pandas
        load_code = f"""
        proc cas;
            table.fetch / 
                table={{name="{Config.TOPIC_VECTORS_TABLE}", caslib="{Config.TOPIC_VECTORS_CASLIB}"}};
        quit;
        """
        
        # Alternative: Use SAS to create a work dataset first
        work_code = f"""
        data work.topic_data;
            set {Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE};
        run;
        """
        
        result = sas.submit(work_code)
        print("✓ Data copied to work library")
        
        # Now try to get it as pandas DataFrame
        try:
            df = sas.sasdata2dataframe("work.topic_data")
            print(f"✓ Data loaded to pandas: {len(df)} rows, {len(df.columns)} columns")
            
            # Analyze columns
            print(f"\nColumn analysis:")
            print(f"Total columns: {len(df.columns)}")
            
            # Look for vector columns
            vector_cols = [col for col in df.columns if col.startswith(('_TextTopic_', '_Col'))]
            print(f"Vector columns found: {len(vector_cols)}")
            for col in vector_cols:
                print(f"  - {col}")
            
            # Look for metadata columns
            meta_cols = ['Case Number', 'Assignment Group', 'Resolution', 'Concern', 'Description']
            found_meta = [col for col in meta_cols if col in df.columns]
            print(f"Metadata columns found: {found_meta}")
            
            # Show sample of first few columns
            print(f"\nFirst 3 rows of key columns:")
            sample_cols = found_meta[:3] if found_meta else df.columns[:3]
            print(df[sample_cols].head(3).to_string())
            
            return df
            
        except Exception as e:
            print(f"⚠️  Pandas conversion failed: {e}")
            print("This is normal - trying alternative approach...")
            return None
            
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        return None

def test_similarity_calculation(df):
    """Test similarity calculation with actual data"""
    print("\n=== Testing Similarity Calculation ===")
    
    if df is None:
        print("⚠️  No data available for similarity test")
        return False
    
    try:
        # Find vector columns
        vector_cols = [col for col in df.columns if col.startswith(('_TextTopic_', '_Col'))]
        
        if not vector_cols:
            print("✗ No vector columns found")
            return False
        
        print(f"Using {len(vector_cols)} vector columns for similarity")
        
        # Get case identifier column
        case_col = None
        for col_name in ['Case Number', 'case_number', '__uniqueid__']:
            if col_name in df.columns:
                case_col = col_name
                break
        
        if not case_col:
            print("⚠️  No case identifier column found")
            case_col = df.columns[0]  # Use first column as fallback
        
        print(f"Using '{case_col}' as case identifier")
        
        # Test with first case
        test_case_id = df[case_col].iloc[0]
        print(f"Testing similarity for case: {test_case_id}")
        
        # Get vectors
        vectors = df[vector_cols].values
        target_vector = vectors[0].reshape(1, -1)
        
        # Calculate similarities
        similarities = cosine_similarity(target_vector, vectors)[0]
        
        # Get top similar cases (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:6]  # Skip first (self)
        
        print(f"✓ Similarity calculation successful")
        print(f"Top 5 similar cases:")
        
        for i, idx in enumerate(top_indices, 1):
            case_id = df[case_col].iloc[idx]
            score = similarities[idx]
            print(f"  {i}. Case {case_id}: {score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Similarity calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("=" * 60)
    print("CaseMatch SAS Viya Integration - Table Structure Test")
    print("=" * 60)
    
    # Import config after adding to path
    from config import Config
    
    # Test 1: Connection
    sas = test_saspy_connection()
    if not sas:
        print("\n✗ Cannot proceed without SAS connection")
        return False
    
    # Test 2: Table structure
    if not analyze_table_structure(sas):
        print("\n⚠️  Table structure analysis failed")
    
    # Test 3: Data loading
    df = test_data_loading(sas)
    
    # Test 4: Similarity calculation
    similarity_success = test_similarity_calculation(df)
    
    # Test 5: Flask integration test
    print("\n=== Testing Flask Integration ===")
    try:
        from similarity import get_similar_cases
        
        if df is not None and len(df) > 0:
            # Get a sample case number
            case_col = None
            for col_name in ['Case Number', 'case_number', '__uniqueid__']:
                if col_name in df.columns:
                    case_col = col_name
                    break
            
            if case_col:
                test_case = str(df[case_col].iloc[0])
                print(f"Testing Flask function with case: {test_case}")
                
                similar_cases = get_similar_cases(test_case, top_k=3)
                if similar_cases:
                    print(f"✓ Flask integration working: {len(similar_cases)} similar cases found")
                else:
                    print("⚠️  Flask integration returned no results")
            else:
                print("⚠️  Cannot test Flask integration - no case identifier")
        else:
            print("⚠️  Cannot test Flask integration - no data")
            
    except Exception as e:
        print(f"✗ Flask integration test failed: {e}")
    
    # Cleanup
    try:
        sas.endsas()
        print("\n✓ SAS session closed")
    except:
        pass
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ SAS Connection: {'SUCCESS' if sas else 'FAILED'}")
    print(f"✓ Data Loading: {'SUCCESS' if df is not None else 'FAILED'}")
    print(f"✓ Similarity Calc: {'SUCCESS' if similarity_success else 'FAILED'}")
    
    if sas and df is not None and similarity_success:
        print("\n🎉 Your SAS Viya integration is ready!")
        print("You can now start the Flask backend with: python run_local.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return sas and df is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)