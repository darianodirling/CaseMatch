#!/usr/bin/env python3
"""
Local development script to run the Flask backend with SAS Viya integration
Use this script when running on your local machine with SAS Viya access
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if running environment is suitable for SAS Viya connection"""
    try:
        import socket
        
        # Try to resolve SAS Viya hostname
        hostname = "trck1056928.trc.sas.com"
        try:
            socket.gethostbyname(hostname)
            logger.info(f"✓ SAS Viya hostname {hostname} is resolvable")
            return True
        except socket.gaierror:
            logger.warning(f"⚠️  Cannot resolve hostname {hostname}")
            logger.info("This is normal if running outside your organization's network")
            logger.info("The Flask backend will still start and can be tested with mock responses")
            return False
            
    except Exception as e:
        logger.error(f"Environment check failed: {e}")
        return False

def start_server():
    """Start the Flask server"""
    try:
        from app import app
        from config import Config
        
        # Check environment
        has_viya_access = check_environment()
        
        if not has_viya_access:
            logger.info("Running in demo mode - SAS Viya features may not work")
        
        logger.info(f"Starting Flask server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
        logger.info("Available endpoints:")
        logger.info("  GET  /health - Health check")
        logger.info("  GET  /test-connection - Test SAS Viya connection")
        logger.info("  POST /search - Search for similar cases")
        logger.info("")
        logger.info("Frontend integration:")
        logger.info("  React app should connect to: http://localhost:5001")
        
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()