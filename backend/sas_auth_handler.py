#!/usr/bin/env python3
"""
SAS Viya OAuth2 Authentication Handler
Handles modern SAS Viya authentication with OAuth2 flows
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SASVilyaAuthHandler:
    """Handle SAS Viya authentication including OAuth2 flows"""
    
    def __init__(self):
        self.auth_cache_file = os.path.join(os.path.dirname(__file__), '.sas_auth_cache.json')
        self.cached_auth = self._load_cached_auth()
    
    def _load_cached_auth(self) -> Optional[Dict]:
        """Load cached authentication tokens if available"""
        try:
            if os.path.exists(self.auth_cache_file):
                with open(self.auth_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load cached auth: {e}")
        return None
    
    def _save_auth_cache(self, auth_data: Dict):
        """Save authentication data for reuse"""
        try:
            with open(self.auth_cache_file, 'w') as f:
                json.dump(auth_data, f)
        except Exception as e:
            logger.warning(f"Could not save auth cache: {e}")
    
    def get_sas_config_with_auth(self) -> Dict[str, Any]:
        """Get SAS configuration with appropriate authentication method"""
        from config import Config
        
        base_config = {
            'url': f'https://{Config.SAS_HOST}',
            'context': 'SAS Studio compute context',
            'options': ['-fullstimer'],
            'encoding': 'utf8'
        }
        
        # Try OAuth2 authentication first
        oauth_config = self._try_oauth2_config(base_config)
        if oauth_config:
            return oauth_config
        
        # Fallback to username/password
        return self._get_userpass_config(base_config)
    
    def _try_oauth2_config(self, base_config: Dict) -> Optional[Dict]:
        """Try OAuth2 authentication configuration"""
        if self.cached_auth and 'access_token' in self.cached_auth:
            logger.info("Using cached OAuth2 authentication")
            config = base_config.copy()
            config.update({
                'authkey': 'oauth',
                'access_token': self.cached_auth['access_token']
            })
            
            if 'refresh_token' in self.cached_auth:
                config['refresh_token'] = self.cached_auth['refresh_token']
            
            return config
        
        return None
    
    def _get_userpass_config(self, base_config: Dict) -> Dict:
        """Get username/password configuration"""
        from config import Config
        
        config = base_config.copy()
        config.update({
            'user': Config.SAS_USERNAME,
            'pw': Config.SAS_PASSWORD,
            'authkey': 'viya_user-pw'
        })
        
        return config
    
    def handle_auth_callback(self, auth_data: Dict):
        """Handle OAuth2 authentication callback data"""
        if 'access_token' in auth_data:
            logger.info("Received OAuth2 authentication data")
            self._save_auth_cache(auth_data)
            return True
        return False
    
    def clear_auth_cache(self):
        """Clear cached authentication data"""
        try:
            if os.path.exists(self.auth_cache_file):
                os.remove(self.auth_cache_file)
                logger.info("Authentication cache cleared")
        except Exception as e:
            logger.warning(f"Could not clear auth cache: {e}")

def get_sas_session_with_auth():
    """Create SAS session with proper authentication handling"""
    import saspy
    
    auth_handler = SASVilyaAuthHandler()
    
    try:
        # Try the configured 'viya' setup first
        sas = saspy.SASsession(cfgname='viya')
        logger.info("Connected using 'viya' configuration")
        return sas
    except Exception as e:
        logger.info(f"Standard config failed: {e}")
        
        try:
            # Try with OAuth2/auth-aware configuration
            config = auth_handler.get_sas_config_with_auth()
            sas = saspy.SASsession(**config)
            logger.info("Connected using auth-aware configuration")
            return sas
        except Exception as e:
            logger.error(f"Auth-aware connection failed: {e}")
            raise

if __name__ == "__main__":
    # Test authentication handler
    try:
        sas = get_sas_session_with_auth()
        if sas:
            print("✓ SAS connection successful")
            result = sas.submit("proc options option=work; run;")
            if result and 'ERROR' not in result.get('LOG', ''):
                print("✓ SAS session working")
            sas.endsas()
        else:
            print("✗ Connection failed")
    except Exception as e:
        print(f"✗ Error: {e}")