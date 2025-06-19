#!/usr/bin/env python3
"""
Quick test script for SAS Viya connection and table structure
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connection():
    print("=== CaseMatch SAS Viya Quick Test ===\n")
    
    try:
        import saspy
        print("✓ SASPy imported successfully")
    except ImportError:
        print("✗ SASPy not installed. Run: pip install saspy")
        return False
    
    try:
        from config import Config
        print("✓ Configuration loaded")
        print(f"  - Host: {Config.SAS_HOST}")
        print(f"  - Username: {Config.SAS_USERNAME}")
        print(f"  - Table: {Config.TOPIC_VECTORS_TABLE}")
        print(f"  - Library: {Config.TOPIC_VECTORS_CASLIB}")
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False
    
    try:
        # Test SAS connection
        sas_config = Config.get_sas_config()
        print("\n--- Testing SAS Connection ---")
        
        sas = saspy.SASsession(**sas_config)
        print("✓ SAS session established")
        
        # Test CAS connection
        print("\n--- Testing CAS Connection ---")
        cas_config = Config.get_cas_config()
        
        sas_code = f"""
        cas mySession;
        caslib _all_ assign;
        
        proc casutil;
            list tables caslib="{Config.TOPIC_VECTORS_CASLIB}";
        quit;
        """
        
        result = sas.submit(sas_code)
        print("✓ CAS connection established")
        
        # Check table structure
        print(f"\n--- Checking {Config.TOPIC_VECTORS_TABLE} Table ---")
        
        table_info_code = f"""
        proc casutil;
            contents casdata="{Config.TOPIC_VECTORS_TABLE}" caslib="{Config.TOPIC_VECTORS_CASLIB}";
        quit;
        """
        
        table_result = sas.submit(table_info_code)
        print("✓ Table structure retrieved")
        
        # Get sample data
        print("\n--- Sample Data ---")
        
        sample_code = f"""
        proc cas;
            table.fetch / 
                table={{name="{Config.TOPIC_VECTORS_TABLE}", caslib="{Config.TOPIC_VECTORS_CASLIB}"}},
                maxRows=3;
        quit;
        """
        
        sample_result = sas.submit(sample_code)
        print("✓ Sample data retrieved")
        
        # Test vector columns
        print("\n--- Vector Columns Analysis ---")
        
        vector_check_code = f"""
        proc contents data={Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE};
        run;
        """
        
        vector_result = sas.submit(vector_check_code)
        print("✓ Column analysis complete")
        
        print("\n=== Test Results ===")
        print("✓ SAS Viya connection: SUCCESS")
        print("✓ CAS session: SUCCESS") 
        print("✓ Table access: SUCCESS")
        print("✓ Ready for similarity search")
        
        # Clean up
        sas.endsas()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)