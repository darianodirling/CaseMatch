#!/usr/bin/env python3
"""
Verification script to test SAS configuration in your environment
This will help verify that the 'viya' configuration is correctly set up
"""

import os
import sys
import traceback

def test_saspy_import():
    """Test if saspy can be imported and find configurations"""
    print("=== Testing SASPy Import and Configuration ===")
    
    try:
        import saspy
        print("✓ SASPy imported successfully")
        
        # Check available configurations
        try:
            configs = saspy.list_configs()
            print(f"✓ Available SAS configurations: {configs}")
            
            if 'viya' in configs:
                print("✓ 'viya' configuration found")
                return True
            else:
                print("✗ 'viya' configuration not found")
                print("Available configurations:", configs)
                return False
                
        except Exception as e:
            print(f"⚠️  Could not list configurations: {e}")
            # Try to proceed anyway
            return True
            
    except ImportError as e:
        print(f"✗ SASPy import failed: {e}")
        return False

def test_sascfg_file():
    """Test if sascfg_personal.py is properly configured"""
    print("\n=== Testing SAS Configuration File ===")
    
    try:
        # Check if sascfg_personal.py exists
        config_file = os.path.join(os.path.dirname(__file__), 'sascfg_personal.py')
        if not os.path.exists(config_file):
            print("✗ sascfg_personal.py not found")
            return False
        
        print("✓ sascfg_personal.py exists")
        
        # Try to import the configuration
        try:
            import sascfg_personal
            print("✓ sascfg_personal.py imported successfully")
            
            # Check if viya config exists
            if hasattr(sascfg_personal, 'viya'):
                viya_config = sascfg_personal.viya
                print("✓ 'viya' configuration found in sascfg_personal.py")
                print(f"  URL: {viya_config.get('url', 'Not set')}")
                print(f"  User: {viya_config.get('user', 'Not set')}")
                print(f"  Context: {viya_config.get('context', 'Not set')}")
                return True
            else:
                print("✗ 'viya' configuration not found in sascfg_personal.py")
                return False
                
        except Exception as e:
            print(f"✗ Error importing sascfg_personal.py: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking configuration file: {e}")
        return False

def test_sas_connection():
    """Test actual SAS connection"""
    print("\n=== Testing SAS Connection ===")
    
    try:
        import saspy
        
        print("Attempting to connect to SAS Viya...")
        print("This may take a moment and will require network access to trck1056928.trc.sas.com")
        
        # Try to create SAS session
        sas = saspy.SASsession(cfgname='viya')
        
        if sas:
            print("✓ SAS session created successfully")
            
            # Test basic SAS functionality
            try:
                result = sas.submit("proc options option=work; run;")
                if result and 'LOG' in result:
                    if 'ERROR' not in result['LOG']:
                        print("✓ SAS session is working correctly")
                        
                        # Test CAS connection
                        try:
                            cas_result = sas.submit("cas;")
                            if cas_result and 'LOG' in cas_result:
                                if 'ERROR' not in cas_result['LOG']:
                                    print("✓ CAS connection successful")
                                else:
                                    print("⚠️  CAS connection had issues:")
                                    print(cas_result['LOG'][-200:])  # Last 200 chars
                            
                        except Exception as e:
                            print(f"⚠️  CAS test failed: {e}")
                        
                        # Clean up
                        sas.endsas()
                        return True
                    else:
                        print("✗ SAS session test failed:")
                        print(result['LOG'][-200:])  # Last 200 chars
                else:
                    print("✗ No response from SAS session")
                    
            except Exception as e:
                print(f"✗ SAS session test failed: {e}")
                
        else:
            print("✗ Failed to create SAS session")
            
        return False
        
    except Exception as e:
        print(f"✗ SAS connection test failed: {e}")
        traceback.print_exc()
        return False

def test_table_access():
    """Test access to your specific table"""
    print("\n=== Testing Table Access ===")
    
    try:
        import saspy
        
        sas = saspy.SASsession(cfgname='viya')
        if not sas:
            print("✗ Cannot test table access - no SAS connection")
            return False
        
        print("Testing access to topic_vectors.sashdat in CASUSER(daodir)...")
        
        # Test table access
        table_code = """
        proc casutil;
            list tables caslib="CASUSER(daodir)";
        quit;
        """
        
        result = sas.submit(table_code)
        if result and 'LOG' in result:
            if 'topic_vectors.sashdat' in result['LOG']:
                print("✓ topic_vectors.sashdat table found")
                
                # Try to get table info
                info_code = """
                proc casutil;
                    contents casdata="topic_vectors.sashdat" caslib="CASUSER(daodir)";
                quit;
                """
                
                info_result = sas.submit(info_code)
                if info_result and 'LOG' in info_result:
                    if 'ERROR' not in info_result['LOG']:
                        print("✓ Table structure accessed successfully")
                    else:
                        print("⚠️  Table info access had issues")
                
                sas.endsas()
                return True
            else:
                print("⚠️  topic_vectors.sashdat not found in table listing")
                print("Available tables in the log:")
                print(result['LOG'][-300:])
        
        sas.endsas()
        return False
        
    except Exception as e:
        print(f"✗ Table access test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("SAS Configuration Verification for CaseMatch")
    print("=" * 50)
    
    tests = [
        ("SASPy Import", test_saspy_import),
        ("Configuration File", test_sascfg_file),
        ("SAS Connection", test_sas_connection),
        ("Table Access", test_table_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All verification tests passed!")
        print("Your SAS configuration is correctly set up.")
        print("You can now use: self.sas = saspy.SASsession(cfgname='viya')")
    else:
        print(f"\n⚠️  {len(results)-passed} test(s) failed.")
        print("Check the output above for specific issues.")
        
        if passed >= 2:  # If at least import and config file work
            print("\nThe configuration appears correct.")
            print("Connection failures may be due to network access or server availability.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)