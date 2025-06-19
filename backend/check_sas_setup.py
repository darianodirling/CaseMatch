#!/usr/bin/env python3
"""
Quick check to verify SAS configuration is working
Run this to test: python check_sas_setup.py
"""

def check_sas_config():
    print("Checking SAS configuration...")
    
    try:
        import saspy
        print("✓ SASPy available")
        
        # List available configurations
        configs = saspy.list_configs()
        print(f"Available configs: {configs}")
        
        if 'viya' in configs:
            print("✓ 'viya' config found")
            
            # Test connection
            print("Testing connection...")
            sas = saspy.SASsession(cfgname='viya')
            
            if sas:
                print("✓ Connection successful")
                result = sas.submit("proc options option=work; run;")
                
                if result and 'ERROR' not in result.get('LOG', ''):
                    print("✓ SAS session working")
                    sas.endsas()
                    return True
                else:
                    print("✗ SAS session test failed")
            else:
                print("✗ Connection failed")
        else:
            print("✗ 'viya' config not found")
            print("Check sascfg_personal.py file")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = check_sas_config()
    if success:
        print("\n🎉 SAS configuration is working correctly!")
        print("The similarity search will work with your environment.")
    else:
        print("\n⚠️ SAS configuration needs attention.")
        print("Run: python verify_sas_config.py for detailed diagnostics.")