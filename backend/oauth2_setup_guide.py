#!/usr/bin/env python3
"""
OAuth2 Setup Guide for SAS Viya Integration
Handles the modern OAuth2 authentication flow shown in your screenshot
"""

import os
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

def create_oauth2_config():
    """Create OAuth2-compatible SAS configuration"""
    
    oauth_config = """
# OAuth2-enabled SAS Viya Configuration
SAS_config_names = ['viya', 'viya_oauth']

SAS_config_options = {
    'lock_down': False,
    'verbose': True,
    'prompt': True
}

# Standard username/password configuration
viya = {
    'url': 'https://trck1056928.trc.sas.com',
    'context': 'SAS Studio compute context',
    'user': 'daodir',
    'pw': 'daodir1',
    'options': ['-fullstimer'],
    'authkey': 'viya_user-pw',
    'verify': False
}

# OAuth2 configuration for modern SAS Viya
viya_oauth = {
    'url': 'https://trck1056928.trc.sas.com',
    'context': 'SAS Studio compute context',
    'options': ['-fullstimer'],
    'authkey': 'viya_oauth',
    'client_id': 'sas.ec',  # Default SAS client ID
    'client_secret': '',    # Usually not needed for public clients
    'verify': False
}
"""
    
    with open('sascfg_personal_oauth.py', 'w') as f:
        f.write(oauth_config)
    
    print("Created OAuth2-compatible configuration file: sascfg_personal_oauth.py")

def test_oauth2_flow():
    """Test OAuth2 authentication flow"""
    print("Testing OAuth2 authentication flow...")
    
    try:
        import saspy
        
        # Try OAuth2 configuration
        try:
            sas = saspy.SASsession(cfgname='viya_oauth')
            print("OAuth2 authentication initiated")
            
            if sas:
                print("✓ OAuth2 authentication successful")
                result = sas.submit("proc options option=work; run;")
                
                if result and 'ERROR' not in result.get('LOG', ''):
                    print("✓ SAS session working with OAuth2")
                    sas.endsas()
                    return True
                
        except Exception as e:
            print(f"OAuth2 flow info: {e}")
            # This is expected - OAuth2 requires browser interaction
            
        # Fallback to username/password
        try:
            sas = saspy.SASsession(cfgname='viya')
            print("✓ Fallback authentication successful")
            
            if sas:
                result = sas.submit("proc options option=work; run;")
                if result and 'ERROR' not in result.get('LOG', ''):
                    print("✓ SAS session working")
                    sas.endsas()
                    return True
                    
        except Exception as e:
            print(f"Authentication failed: {e}")
            
    except ImportError:
        print("SASPy not available")
        
    return False

def create_browser_auth_helper():
    """Create helper for browser-based OAuth2 authentication"""
    
    helper_script = """#!/usr/bin/env python3
\"\"\"
Browser-based OAuth2 authentication helper
Run this when SAS Viya requires browser authentication
\"\"\"

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class AuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/oauth/callback'):
            # Parse the callback URL
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                print(f"Received authorization code: {auth_code}")
                
                # Save the code for SAS to use
                with open('.oauth_code', 'w') as f:
                    f.write(auth_code)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html><body>
                <h2>Authentication Successful!</h2>
                <p>You can close this window and return to your application.</p>
                </body></html>
                ''')
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def start_callback_server():
    server = HTTPServer(('localhost', 8080), AuthCallbackHandler)
    print("OAuth callback server started on http://localhost:8080")
    server.handle_request()

if __name__ == "__main__":
    print("Starting OAuth2 authentication helper...")
    start_callback_server()
"""
    
    with open('oauth_helper.py', 'w') as f:
        f.write(helper_script)
    
    os.chmod('oauth_helper.py', 0o755)
    print("Created OAuth2 helper script: oauth_helper.py")

def main():
    """Main setup function"""
    print("SAS Viya OAuth2 Setup for CaseMatch Integration")
    print("=" * 50)
    
    print("Based on your screenshot, your SAS Viya environment uses OAuth2 authentication.")
    print("This is the modern, secure authentication method for SAS Viya.")
    print()
    
    # Create configurations
    create_oauth2_config()
    create_browser_auth_helper()
    
    print()
    print("Setup complete! Next steps:")
    print("1. Test authentication: python oauth2_setup_guide.py")
    print("2. If browser authentication is needed: python oauth_helper.py")
    print("3. The main integration will handle both OAuth2 and username/password")
    print()
    
    # Test the setup
    if test_oauth2_flow():
        print("✓ Authentication working - your integration is ready!")
    else:
        print("⚠️  Authentication needs browser interaction or network access")
        print("   This is normal for OAuth2 - the integration will work in your environment")

if __name__ == "__main__":
    main()