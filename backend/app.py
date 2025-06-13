from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from similarity import get_similar_cases

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes to allow React frontend connections
CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5000"])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running'
    }), 200

@app.route('/search', methods=['POST'])
def search_similar_cases():
    """
    Search for similar cases based on case number
    
    Expected JSON payload:
    {
        "case_number": "CS10023856",
        "top_k": 5  // optional, defaults to 5
    }
    
    Returns:
    {
        "success": true,
        "case_number": "CS10023856",
        "similar_cases": [
            {
                "case_number": "CS13458729",
                "similarity_score": 0.87,
                "title": "User reported intermittent performance lags",
                "resolution": "Confirmed system resources and adjusted configuration",
                "assignment_group": "performance",
                "case_type": "performance",
                "status": "resolved"
            },
            ...
        ]
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'case_number' not in data:
            return jsonify({
                'success': False,
                'error': 'case_number is required'
            }), 400
        
        case_number = data['case_number'].strip()
        top_k = data.get('top_k', 5)
        
        # Validate inputs
        if not case_number:
            return jsonify({
                'success': False,
                'error': 'case_number cannot be empty'
            }), 400
        
        if not isinstance(top_k, int) or top_k <= 0 or top_k > 20:
            return jsonify({
                'success': False,
                'error': 'top_k must be an integer between 1 and 20'
            }), 400
        
        logger.info(f"Searching for similar cases to: {case_number}")
        
        # Get similar cases using SAS Viya integration
        similar_cases = get_similar_cases(case_number, top_k)
        
        # Format response
        response = {
            'success': True,
            'case_number': case_number,
            'similar_cases': similar_cases,
            'total_found': len(similar_cases)
        }
        
        logger.info(f"Found {len(similar_cases)} similar cases for {case_number}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error occurred while searching for similar cases'
        }), 500

@app.route('/test-connection', methods=['GET'])
def test_viya_connection():
    """
    Test endpoint to verify SAS Viya connection
    """
    try:
        from similarity import test_connection
        
        success = test_connection()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'SAS Viya connection successful'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'SAS Viya connection failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )