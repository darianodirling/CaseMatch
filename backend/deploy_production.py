#!/usr/bin/env python3
"""
Production deployment script for CaseMatch SAS Viya integration
Handles environment setup, dependency installation, and service configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Ensure Python 3.8+ is available"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    packages = [
        'flask>=2.0.0',
        'flask-cors>=3.0.0',
        'saspy>=4.0.0',
        'pandas>=1.3.0',
        'numpy>=1.20.0',
        'scikit-learn>=1.0.0'
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        result = run_command(f"pip install {package}")
        if result is None:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All dependencies installed")
    return True

def setup_environment():
    """Set up production environment configuration"""
    print("\n🔧 Setting up production environment...")
    
    # Create production .env file
    prod_env_content = """# Production Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=false

# SAS Viya Connection Settings
SAS_CONFIG_NAME=viya
SAS_HOST=trck1056928.trc.sas.com
SAS_PORT=443
SAS_USERNAME=daodir
SAS_PASSWORD=daodir1

# CAS Server Settings
CAS_HOST=trck1056928.trc.sas.com
CAS_PORT=5570
CAS_PROTOCOL=cas

# Data Table Configuration (from SAS Data Explorer)
TOPIC_VECTORS_TABLE=topic_vectors.sashdat
TOPIC_VECTORS_CASLIB=CASUSER(daodir)

# API Settings
MAX_SIMILAR_CASES=20
DEFAULT_SIMILAR_CASES=5
"""
    
    with open('.env.production', 'w') as f:
        f.write(prod_env_content)
    
    print("✅ Production environment configured")
    return True

def create_systemd_service():
    """Create systemd service file for production deployment"""
    print("\n🚀 Creating systemd service configuration...")
    
    current_dir = Path(__file__).parent.absolute()
    
    service_content = f"""[Unit]
Description=CaseMatch SAS Viya Integration Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={current_dir}
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile={current_dir}/.env.production
ExecStart=/usr/bin/python3 {current_dir}/run_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('casematch-backend.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created: casematch-backend.service")
    print("To install: sudo cp casematch-backend.service /etc/systemd/system/")
    print("To start: sudo systemctl start casematch-backend")
    print("To enable: sudo systemctl enable casematch-backend")
    
    return True

def create_production_runner():
    """Create production runner script"""
    print("\n📝 Creating production runner...")
    
    runner_content = """#!/usr/bin/env python3
\"\"\"
Production runner for CaseMatch SAS Viya integration
Uses production configuration and logging
\"\"\"

import os
import sys
import logging
from pathlib import Path

# Set up production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('casematch-backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    \"\"\"Main production entry point\"\"\"
    try:
        # Load production environment
        env_file = Path(__file__).parent / '.env.production'
        if env_file.exists():
            logger.info("Loading production environment")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        
        # Import and run Flask app
        from app import app
        from config import Config
        
        logger.info(f"Starting CaseMatch backend on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
        logger.info(f"SAS Host: {Config.SAS_HOST}")
        logger.info(f"Table: {Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE}")
        
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open('run_production.py', 'w') as f:
        f.write(runner_content)
    
    # Make executable
    os.chmod('run_production.py', 0o755)
    
    print("✅ Production runner created")
    return True

def create_nginx_config():
    """Create nginx configuration for reverse proxy"""
    print("\n🌐 Creating nginx configuration...")
    
    nginx_content = """# CaseMatch Backend - Nginx Configuration
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;  # Replace with your domain
    
    # SSL configuration (replace with your certificates)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy to Flask backend
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
    
    # Serve static files (React frontend)
    location / {
        root /var/www/casematch/dist;
        try_files $uri $uri/ /index.html;
    }
}
"""
    
    with open('nginx-casematch.conf', 'w') as f:
        f.write(nginx_content)
    
    print("✅ Nginx configuration created: nginx-casematch.conf")
    print("To install: sudo cp nginx-casematch.conf /etc/nginx/sites-available/")
    print("To enable: sudo ln -s /etc/nginx/sites-available/nginx-casematch.conf /etc/nginx/sites-enabled/")
    
    return True

def test_production_setup():
    """Test production configuration"""
    print("\n🧪 Testing production setup...")
    
    try:
        # Test imports
        import flask
        import flask_cors
        import saspy
        import pandas
        import numpy
        import sklearn
        print("✅ All dependencies available")
        
        # Test configuration
        from config import Config
        print(f"✅ Configuration loaded")
        print(f"   SAS Host: {Config.SAS_HOST}")
        print(f"   Table: {Config.TOPIC_VECTORS_CASLIB}.{Config.TOPIC_VECTORS_TABLE}")
        
        # Test Flask app
        from app import app
        print("✅ Flask app loads successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        return False

def main():
    """Main deployment script"""
    print("🚀 CaseMatch SAS Viya Integration - Production Deployment")
    print("=" * 60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating systemd service", create_systemd_service),
        ("Creating production runner", create_production_runner),
        ("Creating nginx config", create_nginx_config),
        ("Testing setup", test_production_setup)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed")
            return False
    
    print("\n🎉 Production deployment setup complete!")
    print("\nNext steps:")
    print("1. Copy systemd service: sudo cp casematch-backend.service /etc/systemd/system/")
    print("2. Start service: sudo systemctl start casematch-backend")
    print("3. Enable service: sudo systemctl enable casematch-backend")
    print("4. Configure nginx: sudo cp nginx-casematch.conf /etc/nginx/sites-available/")
    print("5. Enable nginx site: sudo ln -s /etc/nginx/sites-available/nginx-casematch.conf /etc/nginx/sites-enabled/")
    print("6. Test service: curl http://localhost:5001/health")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)