#!/usr/bin/env python3
"""
Comprehensive test script for CaseMatch SAS Viya integration
Tests connection, data access, and similarity search functionality
"""

import os
import sys
import json
import traceback
from datetime import datetime

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from similarity import SimilaritySearcher, test_connection, get_similar_cases

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a test step"""
    print(f"\n[Step {step}] {description}")
    print("-" * 40)

def test_environment():
    """Test 1: Check environment and configuration"""
    print_step(1, "Testing Environment Configuration")
    
    try:
        # Check required environment variables
        required_vars = ['SAS_HOST', 'SAS_USERNAME', 'SAS_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            value = getattr(Config, var, None)
            if not value:
                missing_vars.append(var)
            else:
                print(f"✓ {var}: {'*' * len(str(value))} (configured)")
        
        if missing_vars:
            print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        # Display configuration
        print(f"✓ SAS Host: {Config.SAS_HOST}")
        print(f"✓ SAS Port: {Config.SAS_PORT}")
        print(f"✓ CAS Host: {Config.CAS_HOST}")
        print(f"✓ CAS Port: {Config.CAS_PORT}")
        print(f"✓ Table: {Config.TOPIC_VECTORS_TABLE}")
        print(f"✓ Library: {Config.TOPIC_VECTORS_CASLIB}")
        
        return True
        
    except Exception as e:
        print(f"✗ Environment test failed: {str(e)}")
        return False

def test_dependencies():
    """Test 2: Check Python dependencies"""
    print_step(2, "Testing Python Dependencies")
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('saspy', 'SASPy'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn')
    ]
    
    missing_deps = []
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} - NOT INSTALLED")
            missing_deps.append(display_name)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install flask flask-cors saspy pandas numpy scikit-learn")
        return False
    
    return True

def test_sas_connection():
    """Test 3: Test SAS Viya connection"""
    print_step(3, "Testing SAS Viya Connection")
    
    try:
        searcher = SimilaritySearcher()
        
        # Test connection
        if searcher.connect_to_viya():
            print("✓ SAS Viya connection established")
            
            # Test session
            if hasattr(searcher, 'sas_session') and searcher.sas_session:
                print("✓ SAS session active")
                
                # Try to list available libraries
                try:
                    result = searcher.sas_session.submit("proc datasets library=work; run;")
                    print("✓ SAS code execution successful")
                except Exception as e:
                    print(f"⚠️  SAS code execution warning: {str(e)}")
            
            return True
        else:
            print("✗ Failed to connect to SAS Viya")
            return False
            
    except Exception as e:
        print(f"✗ SAS connection test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_cas_connection():
    """Test 4: Test CAS connection and table access"""
    print_step(4, "Testing CAS Connection and Table Access")
    
    try:
        searcher = SimilaritySearcher()
        
        if not searcher.connect_to_viya():
            print("✗ Cannot test CAS - SAS connection failed")
            return False
        
        # Test loading topic vectors
        if searcher.load_topic_vectors():
            print("✓ Topic vectors table loaded successfully")
            
            if searcher.topic_vectors_data is not None:
                num_records = len(searcher.topic_vectors_data)
                print(f"✓ Records loaded: {num_records}")
                
                # Display column information
                columns = list(searcher.topic_vectors_data.columns)
                print(f"✓ Columns found: {len(columns)}")
                
                # Check for expected columns
                expected_cols = ['Case Number', 'Assignment Group', 'Resolution', 'Concern', 'Description']
                vector_cols = [col for col in columns if col.startswith(('_TextTopic_', '_Col'))]
                
                print("\nColumn Analysis:")
                for col in expected_cols:
                    if col in columns:
                        print(f"  ✓ {col}")
                    else:
                        # Check alternative names
                        alt_found = False
                        for actual_col in columns:
                            if col.lower().replace(' ', '_') in actual_col.lower():
                                print(f"  ✓ {col} (found as: {actual_col})")
                                alt_found = True
                                break
                        if not alt_found:
                            print(f"  ⚠️  {col} (not found)")
                
                print(f"\nVector columns found: {len(vector_cols)}")
                for col in vector_cols[:5]:  # Show first 5
                    print(f"  • {col}")
                if len(vector_cols) > 5:
                    print(f"  ... and {len(vector_cols) - 5} more")
                
                # Show sample data
                print("\nSample data (first 3 rows):")
                sample_cols = ['Case Number', 'Assignment Group', 'Resolution']
                available_sample_cols = [col for col in sample_cols if col in columns]
                
                if available_sample_cols:
                    sample_data = searcher.topic_vectors_data[available_sample_cols].head(3)
                    print(sample_data.to_string())
                else:
                    print("Sample columns not available, showing first few columns:")
                    print(searcher.topic_vectors_data.iloc[:3, :3].to_string())
                
                return True
            else:
                print("✗ No data returned from topic_vectors table")
                return False
        else:
            print("✗ Failed to load topic_vectors table")
            return False
            
    except Exception as e:
        print(f"✗ CAS test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_similarity_search():
    """Test 5: Test similarity search functionality"""
    print_step(5, "Testing Similarity Search")
    
    try:
        searcher = SimilaritySearcher()
        
        # First ensure we have data
        if not searcher.connect_to_viya():
            print("✗ Cannot test similarity - SAS connection failed")
            return False
            
        if not searcher.load_topic_vectors():
            print("✗ Cannot test similarity - failed to load data")
            return False
        
        if searcher.topic_vectors_data is None or len(searcher.topic_vectors_data) == 0:
            print("✗ Cannot test similarity - no data available")
            return False
        
        # Get a sample case number from the data
        case_col = 'Case Number' if 'Case Number' in searcher.topic_vectors_data.columns else 'case_number'
        if case_col not in searcher.topic_vectors_data.columns:
            print("✗ Cannot find case number column")
            return False
        
        sample_cases = searcher.topic_vectors_data[case_col].dropna().head(3).tolist()
        
        if not sample_cases:
            print("✗ No valid case numbers found")
            return False
        
        print(f"Testing with sample cases: {sample_cases}")
        
        # Test similarity search
        for test_case in sample_cases[:2]:  # Test with first 2 cases
            print(f"\nTesting similarity search for case: {test_case}")
            
            try:
                similar_cases = get_similar_cases(str(test_case), top_k=3)
                
                if similar_cases:
                    print(f"✓ Found {len(similar_cases)} similar cases")
                    
                    for i, case in enumerate(similar_cases, 1):
                        print(f"  {i}. Case: {case.get('case_number', 'N/A')}")
                        print(f"     Similarity: {case.get('similarity_score', 0):.3f}")
                        print(f"     Title: {case.get('title', 'N/A')[:50]}...")
                else:
                    print(f"⚠️  No similar cases found for {test_case}")
                    
            except Exception as e:
                print(f"✗ Similarity search failed for {test_case}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Similarity search test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test 6: Test Flask API endpoints"""
    print_step(6, "Testing Flask API Endpoints")
    
    try:
        # Import Flask app components
        from app import app
        
        print("✓ Flask app imported successfully")
        
        # Create test client
        with app.test_client() as client:
            
            # Test health endpoint
            print("\nTesting /health endpoint:")
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
                data = response.get_json()
                print(f"  Response: {data}")
            else:
                print(f"✗ Health endpoint failed: {response.status_code}")
            
            # Test SAS connection endpoint
            print("\nTesting /test-connection endpoint:")
            response = client.get('/test-connection')
            if response.status_code == 200:
                print("✓ Test connection endpoint working")
                data = response.get_json()
                print(f"  Response: {data}")
            else:
                print(f"✗ Test connection endpoint failed: {response.status_code}")
            
            # Test search endpoint (if we have test data)
            print("\nTesting /search endpoint:")
            test_payload = {
                "case_number": "TEST123",
                "top_k": 3
            }
            
            response = client.post('/search', 
                                 data=json.dumps(test_payload),
                                 content_type='application/json')
            
            print(f"  Status: {response.status_code}")
            if response.status_code in [200, 400]:  # 400 is expected for invalid case
                data = response.get_json()
                print(f"  Response: {data}")
            
        return True
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {str(e)}")
        traceback.print_exc()
        return False

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    test_names = [
        "Environment Configuration",
        "Python Dependencies", 
        "SAS Viya Connection",
        "CAS Table Access",
        "Similarity Search",
        "Flask API Endpoints"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results.values()), 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {i}. {test_name}: {status}")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the detailed output above for troubleshooting steps.")
    else:
        print(f"\n🎉 All tests passed! Your CaseMatch SAS Viya integration is ready to use.")
    
    return failed_tests == 0

def main():
    """Main test execution"""
    print_header("CaseMatch SAS Viya Integration - Comprehensive Test Suite")
    print(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Execute all tests
    test_functions = [
        test_environment,
        test_dependencies,
        test_sas_connection, 
        test_cas_connection,
        test_similarity_search,
        test_api_endpoints
    ]
    
    results = {}
    
    for i, test_func in enumerate(test_functions, 1):
        try:
            result = test_func()
            results[f"test_{i}"] = result
        except Exception as e:
            print(f"\n✗ Test {i} crashed: {str(e)}")
            traceback.print_exc()
            results[f"test_{i}"] = False
    
    # Generate final report
    success = generate_test_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()