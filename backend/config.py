import os
from typing import Dict, Any
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables
load_env_file()

class Config:
    """Configuration class for Flask backend"""
    
    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # SAS Viya connection settings
    SAS_CONFIG_NAME = os.getenv('SAS_CONFIG_NAME', 'default')
    SAS_HOST = os.getenv('SAS_HOST', 'trck1056928.trc.sas.com')
    SAS_PORT = os.getenv('SAS_PORT', '443')
    SAS_USERNAME = os.getenv('SAS_USERNAME', 'daodir')
    SAS_PASSWORD = os.getenv('SAS_PASSWORD', 'daodir1')
    
    # CAS settings
    CAS_HOST = os.getenv('CAS_HOST', 'trck1056928.trc.sas.com')
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
        """Get SAS configuration dictionary for SAS Viya"""
        config = {
            'url': f'https://{cls.SAS_HOST}',
            'user': cls.SAS_USERNAME,
            'pw': cls.SAS_PASSWORD,
            'context': 'SAS Studio compute context',
            'options': ['-fullstimer'],
            'encoding': 'utf8'
        }
        
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