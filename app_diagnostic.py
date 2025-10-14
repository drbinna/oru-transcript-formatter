"""
Diagnostic Flask app to identify Render deployment issues.
This app has minimal dependencies and extensive logging.
"""

import os
import sys
import json

print("=" * 50, file=sys.stderr)
print("DIAGNOSTIC APP STARTING", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {os.getcwd()}", file=sys.stderr)
print(f"PORT env var: {os.environ.get('PORT', 'NOT SET')}", file=sys.stderr)
print("=" * 50, file=sys.stderr)

try:
    from flask import Flask, jsonify, request
    print("✓ Flask imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"✗ Flask import failed: {e}", file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
print("✓ Flask app created", file=sys.stderr)

# Store request logs
request_logs = []

@app.before_request
def log_request():
    """Log every request."""
    log_entry = {
        'method': request.method,
        'path': request.path,
        'headers': dict(request.headers)
    }
    request_logs.append(log_entry)
    print(f"REQUEST: {request.method} {request.path}", file=sys.stderr)

@app.route('/')
def home():
    """Root endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Diagnostic app is running',
        'python_version': sys.version,
        'working_dir': os.getcwd(),
        'env_vars': {
            'PORT': os.environ.get('PORT'),
            'RENDER': os.environ.get('RENDER'),
            'RENDER_SERVICE_NAME': os.environ.get('RENDER_SERVICE_NAME'),
            'ANTHROPIC_API_KEY': 'SET' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'
        }
    })

@app.route('/health')
def health():
    """Health check."""
    return jsonify({'status': 'healthy'})

@app.route('/logs')
def logs():
    """Show recent request logs."""
    return jsonify(request_logs[-10:])

@app.route('/test-import')
def test_import():
    """Test if we can import the main app modules."""
    results = {}
    
    # Test imports
    imports_to_test = [
        'flask_cors',
        'anthropic',
        'docx',
        'werkzeug'
    ]
    
    for module_name in imports_to_test:
        try:
            __import__(module_name)
            results[module_name] = 'OK'
        except ImportError as e:
            results[module_name] = f'Failed: {str(e)}'
    
    return jsonify(results)

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Minimal upload endpoint."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    return jsonify({
        'success': False,
        'error': 'This is a diagnostic app - upload not implemented',
        'request_info': {
            'method': request.method,
            'content_type': request.content_type,
            'files': list(request.files.keys()) if request.files else []
        }
    })

# Error handlers that always return JSON
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error', 'details': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': 'Exception', 'type': type(e).__name__, 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting diagnostic app on port {port}", file=sys.stderr)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Failed to start app: {e}", file=sys.stderr)
        sys.exit(1)