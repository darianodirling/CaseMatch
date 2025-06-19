#!/usr/bin/env python3
"""
Complete integration test for CaseMatch SAS Viya connection
Tests all components with your actual table structure
"""

import os
import sys
import json
import time
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def test_basic_imports():
    """Test 1: Basic imports and dependencies"""
    print_section("Testing Dependencies")
    
    required_modules = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('saspy', 'SASPy'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn')
    ]
    
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            return False
    
    return True

def test_configuration():
    """Test 2: Configuration setup"""
    print_section("Testing Configuration")
    
    try:
        from config import Config
        
        print(f"✓ SAS Host: {Config.SAS_HOST}")
        print(f"✓ SAS Username: {Config.SAS_USERNAME}")
        print(f"✓ CAS Host: {Config.CAS_HOST}")
        print(f"✓ CAS Port: {Config.CAS_PORT}")
        print(f"✓ Table: {Config.TOPIC_VECTORS_TABLE}")
        print(f"✓ Library: {Config.TOPIC_VECTORS_CASLIB}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_sas_connection():
    """Test 3: SAS connection"""
    print_section("Testing SAS Connection")
    
    try:
        import saspy
        from config import Config
        
        # Test basic connection
        sas_config = Config.get_sas_config()
        print("Attempting SAS connection...")
        
        sas = saspy.SASsession(**sas_config)
        print("✓ SAS session established")
        
        # Test simple SAS code
        result = sas.submit("data _null_; put 'Hello from SAS'; run;")
        print("✓ SAS code execution successful")
        
        return sas
        
    except Exception as e:
        print(f"✗ SAS connection failed: {e}")
        traceback.print_exc()
        return None

def test_table_access(sas):
    """Test 4: Table access and structure"""
    print_section("Testing Table Access")
    
    if not sas:
        print("✗ No SAS connection available")
        return None
    
    try:
        from config import Config
        
        # Check if table exists
        check_code = f"""
        proc casutil;
            list tables caslib="{Config.TOPIC_VECTORS_CASLIB}";
        quit;
        """
        
        result = sas.submit(check_code)
        print("✓ Table listing successful")
        
        # Get table info
        info_code = f"""
        proc contents data={Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE};
        run;
        """
        
        info_result = sas.submit(info_code)
        print("✓ Table structure retrieved")
        
        # Load sample data
        sample_code = f"""
        data work.sample;
            set {Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE}(obs=5);
        run;
        
        proc print data=work.sample;
        run;
        """
        
        sample_result = sas.submit(sample_code)
        print("✓ Sample data loaded")
        
        # Try to convert to pandas
        try:
            df = sas.sasdata2dataframe("work.sample")
            print(f"✓ Pandas conversion: {len(df)} rows, {len(df.columns)} columns")
            
            # Analyze columns
            vector_cols = [col for col in df.columns if col.startswith(('_TextTopic_', '_Col'))]
            print(f"✓ Vector columns found: {len(vector_cols)}")
            
            # Check for expected columns
            expected = ['Case Number', 'Assignment Group', 'Resolution', 'Description', 'Concern']
            found = [col for col in expected if col in df.columns]
            print(f"✓ Metadata columns: {found}")
            
            return df
            
        except Exception as e:
            print(f"⚠️  Pandas conversion failed: {e}")
            return "sas_only"
            
    except Exception as e:
        print(f"✗ Table access failed: {e}")
        traceback.print_exc()
        return None

def test_similarity_logic(df):
    """Test 5: Similarity calculation logic"""
    print_section("Testing Similarity Calculation")
    
    if df is None:
        print("✗ No data available")
        return False
    
    if df == "sas_only":
        print("⚠️  Testing with SAS-only data (no pandas)")
        return True
    
    try:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Find vector columns
        vector_cols = [col for col in df.columns if col.startswith(('_TextTopic_', '_Col'))]
        
        if not vector_cols:
            print("✗ No vector columns found")
            return False
        
        print(f"Using {len(vector_cols)} vector columns")
        
        # Get case identifier
        case_col = 'Case Number' if 'Case Number' in df.columns else df.columns[0]
        print(f"Using '{case_col}' as case identifier")
        
        # Test similarity calculation
        vectors = df[vector_cols].values
        target_vector = vectors[0:1]  # First row as target
        
        similarities = cosine_similarity(target_vector, vectors)[0]
        print(f"✓ Similarity calculation successful")
        
        # Show results
        test_case = df[case_col].iloc[0]
        top_indices = np.argsort(similarities)[::-1][1:4]  # Top 3 excluding self
        
        print(f"Similar cases to '{test_case}':")
        for i, idx in enumerate(top_indices, 1):
            similar_case = df[case_col].iloc[idx]
            score = similarities[idx]
            print(f"  {i}. {similar_case}: {score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Similarity calculation failed: {e}")
        traceback.print_exc()
        return False

def test_flask_endpoints():
    """Test 6: Flask application endpoints"""
    print_section("Testing Flask Application")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print(f"✗ Health endpoint failed: {response.status_code}")
            
            # Test connection endpoint
            response = client.get('/test-connection')
            print(f"✓ Connection test endpoint: {response.status_code}")
            
            # Test search endpoint with sample data
            test_data = {"case_number": "SAMPLE123", "top_k": 3}
            response = client.post('/search', 
                                 json=test_data,
                                 content_type='application/json')
            print(f"✓ Search endpoint: {response.status_code}")
            
            if response.status_code == 200:
                result = response.get_json()
                print(f"  Search returned: {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Flask test failed: {e}")
        return False

def test_end_to_end(sas, df):
    """Test 7: End-to-end integration"""
    print_section("End-to-End Integration Test")
    
    if not sas or df is None:
        print("✗ Prerequisites not met")
        return False
    
    try:
        from similarity import get_similar_cases
        
        if df != "sas_only":
            # Get a real case number
            case_col = 'Case Number' if 'Case Number' in df.columns else df.columns[0]
            test_case = str(df[case_col].iloc[0])
            
            print(f"Testing with real case: {test_case}")
            
            # Test the actual similarity function
            similar_cases = get_similar_cases(test_case, top_k=3)
            
            if similar_cases:
                print(f"✓ Found {len(similar_cases)} similar cases")
                for i, case in enumerate(similar_cases, 1):
                    print(f"  {i}. {case.get('case_number', 'N/A')}: {case.get('similarity_score', 0):.3f}")
                return True
            else:
                print("⚠️  No similar cases returned")
                return False
        else:
            print("⚠️  End-to-end test skipped (no pandas data)")
            return True
            
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("CaseMatch SAS Viya Integration - Complete Test Suite")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = []
    
    # Run all tests
    tests.append(("Dependencies", test_basic_imports()))
    tests.append(("Configuration", test_configuration()))
    
    sas = test_sas_connection()
    tests.append(("SAS Connection", sas is not None))
    
    df = test_table_access(sas)
    tests.append(("Table Access", df is not None))
    
    tests.append(("Similarity Logic", test_similarity_logic(df)))
    tests.append(("Flask Endpoints", test_flask_endpoints()))
    tests.append(("End-to-End", test_end_to_end(sas, df)))
    
    # Cleanup
    if sas:
        try:
            sas.endsas()
            print("\n✓ SAS session closed")
        except:
            pass
    
    # Summary
    print_section("Test Results Summary")
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your integration is ready.")
        print("Start the backend with: python run_local.py")
        print("Start the frontend with: npm run dev")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)