import os
from typing import Dict, Any

class Config:
    """Configuration class for Flask backend"""
    
    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # SAS Viya connection settings
    SAS_CONFIG_NAME = os.getenv('SAS_CONFIG_NAME', 'default')
    SAS_HOST = os.getenv('SAS_HOST', 'localhost')
    SAS_PORT = os.getenv('SAS_PORT', '8561')
    SAS_USERNAME = os.getenv('SAS_USERNAME', '')
    SAS_PASSWORD = os.getenv('SAS_PASSWORD', '')
    
    # CAS settings
    CAS_HOST = os.getenv('CAS_HOST', 'localhost')
    CAS_PORT = int(os.getenv('CAS_PORT', 5570))
    CAS_PROTOCOL = os.getenv('CAS_PROTOCOL', 'cas')
    
    # Data settings
    TOPIC_VECTORS_TABLE = os.getenv('TOPIC_VECTORS_TABLE', 'topic_vectors')
    TOPIC_VECTORS_CASLIB = os.getenv('TOPIC_VECTORS_CASLIB', 'casuser')
    
    # API settings
    MAX_SIMILAR_CASES = int(os.getenv('MAX_SIMILAR_CASES', 20))
    DEFAULT_SIMILAR_CASES = int(os.getenv('DEFAULT_SIMILAR_CASES', 5))
    
    @classmethod
    def get_sas_config(cls) -> Dict[str, Any]:
        """Get SAS configuration dictionary"""
        config = {
            'saspath': '/opt/sasinside/SASHome/SASFoundation/9.4/bin/sas_u8',
            'options': ['-fullstimer', '-log', '/tmp'],
            'encoding': 'utf8'
        }
        
        # Add authentication if provided
        if cls.SAS_USERNAME and cls.SAS_PASSWORD:
            config.update({
                'host': cls.SAS_HOST,
                'port': cls.SAS_PORT,
                'username': cls.SAS_USERNAME,
                'password': cls.SAS_PASSWORD
            })
        
        return config
    
    @classmethod
    def get_cas_config(cls) -> Dict[str, Any]:
        """Get CAS configuration dictionary"""
        return {
            'hostname': cls.CAS_HOST,
            'port': cls.CAS_PORT,
            'protocol': cls.CAS_PROTOCOL,
            'username': cls.SAS_USERNAME,
            'password': cls.SAS_PASSWORD
        }