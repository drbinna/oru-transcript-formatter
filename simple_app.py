"""
Minimal Flask app for testing Render deployment.
This strips down to bare essentials to identify the issue.
"""

import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# Simple in-memory storage for testing
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    """Root endpoint returns JSON for testing."""
    return jsonify({
        'status': 'ok',
        'message': 'Minimal app is running',
        'endpoints': ['/health', '/test', '/echo']
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'transcript-formatter-minimal'
    })

@app.route('/test')
def test():
    """Test endpoint."""
    return jsonify({
        'success': True,
        'message': 'Test endpoint working',
        'timestamp': str(os.environ.get('RENDER_DEPLOY_ID', 'local'))
    })

@app.route('/echo', methods=['POST', 'GET'])
def echo():
    """Echo endpoint for testing POST requests."""
    if request.method == 'GET':
        return jsonify({
            'method': 'GET',
            'message': 'Use POST to send data'
        })
    
    # For POST requests
    data = request.get_json() if request.is_json else {}
    return jsonify({
        'method': 'POST',
        'received': data,
        'content_type': request.content_type
    })

# Global error handler
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'status': 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error', 'status': 500}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)