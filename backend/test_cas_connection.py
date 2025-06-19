#!/usr/bin/env python3
"""
Test script to verify CAS connection functionality
Run this to test the production CAS connection
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_flask_endpoints():
    """Test the Flask endpoints for CAS connectivity"""
    base_url = f"http://{os.getenv('FLASK_HOST', '0.0.0.0')}:{os.getenv('FLASK_PORT', 5001)}"
    
    print("Testing Flask CAS endpoints...")
    print(f"Base URL: {base_url}")
    
    # Test CAS status endpoint
    try:
        print("\n1. Testing /cas-status endpoint...")
        response = requests.get(f"{base_url}/cas-status", timeout=10)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('status') == 'success':
            print("✓ CAS connection successful")
        else:
            print("⚠ CAS connection failed (expected without VPN access)")
            
    except Exception as e:
        print(f"Error testing CAS status: {e}")
    
    # Test table preview endpoint
    try:
        print("\n2. Testing /table-preview endpoint...")
        response = requests.get(f"{base_url}/table-preview", timeout=10)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✓ Table preview successful")
        else:
            print("⚠ Table preview failed (expected without VPN access)")
            
    except Exception as e:
        print(f"Error testing table preview: {e}")

def main():
    """Run CAS connection tests"""
    print("CAS Connection Test Suite")
    print("=" * 50)
    
    # Check environment variables
    cas_host = os.getenv('CAS_HOST')
    cas_username = os.getenv('CAS_USERNAME')
    
    print(f"CAS Host: {cas_host}")
    print(f"CAS Username: {cas_username}")
    print(f"CAS Port: {os.getenv('CAS_PORT')}")
    
    # Test Flask endpoints
    test_flask_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed.")
    print("If connection fails, this is expected without VPN access.")
    print("Run this test on your local machine with VPN for full functionality.")

if __name__ == "__main__":
    main()