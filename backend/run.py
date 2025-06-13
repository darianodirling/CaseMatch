#!/usr/bin/env python3
"""
Standalone script to run the Flask backend server
"""
import sys
import os
import logging
from app import app
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ['flask', 'flask_cors', 'saspy', 'sklearn', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to start the Flask server"""
    try:
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        logger.info("Starting CaseMatch Flask Backend Server")
        logger.info(f"Server will run on: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
        logger.info(f"Debug mode: {Config.FLASK_DEBUG}")
        logger.info("Available endpoints:")
        logger.info("  POST /search - Search for similar cases")
        logger.info("  GET /test-connection - Test SAS Viya connection")
        logger.info("  GET /health - Health check")
        
        # Start the Flask server
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()