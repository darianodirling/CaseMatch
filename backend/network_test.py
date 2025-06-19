#!/usr/bin/env python3
"""
Network connectivity test for SAS Viya server
Tests if Replit can reach the external SAS server
"""

import socket
import requests
import time
from urllib.parse import urlparse

def test_tcp_connection(host, port, timeout=10):
    """Test TCP connection to host:port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"TCP test error: {e}")
        return False

def test_http_connection(url, timeout=10):
    """Test HTTP/HTTPS connection"""
    try:
        response = requests.get(url, timeout=timeout, verify=False)
        return response.status_code < 500
    except Exception as e:
        print(f"HTTP test error: {e}")
        return False

def test_dns_resolution(hostname):
    """Test DNS resolution"""
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception as e:
        print(f"DNS resolution error: {e}")
        return False

def main():
    """Run connectivity tests for SAS Viya server"""
    host = "trck1056928.trc.sas.com"
    cas_port = 5570
    https_url = f"https://{host}"
    
    print(f"Testing connectivity to SAS Viya server: {host}")
    print("=" * 60)
    
    # Test 1: DNS Resolution
    print(f"1. Testing DNS resolution for {host}...")
    dns_ok = test_dns_resolution(host)
    print(f"   Result: {'SUCCESS' if dns_ok else 'FAILED'}")
    
    if not dns_ok:
        print("   Cannot resolve hostname. Server may not be accessible from Replit.")
        return False
    
    # Test 2: HTTPS Connection
    print(f"2. Testing HTTPS connection to {https_url}...")
    https_ok = test_http_connection(https_url)
    print(f"   Result: {'SUCCESS' if https_ok else 'FAILED'}")
    
    # Test 3: CAS Port Connection
    print(f"3. Testing CAS port connection to {host}:{cas_port}...")
    cas_ok = test_tcp_connection(host, cas_port)
    print(f"   Result: {'SUCCESS' if cas_ok else 'FAILED'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("CONNECTIVITY SUMMARY")
    print("=" * 60)
    
    if dns_ok and https_ok and cas_ok:
        print("✓ Full connectivity - CAS integration should work")
        return True
    elif dns_ok and https_ok:
        print("⚠ HTTPS works but CAS port blocked - May need VPN or firewall configuration")
        return False
    elif dns_ok:
        print("⚠ DNS works but connections blocked - Replit may not support external SAS access")
        return False
    else:
        print("✗ No connectivity - Server not reachable from Replit environment")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\nALTERNATIVE SOLUTIONS:")
        print("1. Local Development: Run the backend on your local machine with VPN access")
        print("2. SSH Tunneling: Create an SSH tunnel from Replit to your local machine")
        print("3. Mock Mode: Implement a testing mode with sample data structure")
        print("4. Hybrid Setup: Frontend on Replit, backend locally with API proxy")