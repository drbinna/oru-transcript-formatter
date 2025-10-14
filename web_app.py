"""
Flask web application for the transcript formatter.
Provides a modern HTML interface for uploading and formatting transcripts.
"""

import os
import tempfile
import traceback
import logging
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from transcript_formatter.core.claude_formatter import format_with_claude
from transcript_formatter.exporters.word_exporter import WordExporter
# Removed Python formatter imports - AI-only now
import anthropic
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global error handler to ensure JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions and return JSON."""
    logger.error(f"Unhandled exception on {request.path}: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Check if it's an API endpoint (not the main page)
    if request.path.startswith('/upload') or request.path.startswith('/download') or request.path.startswith('/debug') or request.path.startswith('/health'):
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500
    # For the main page, return normal error handling
    raise e

# Handle 500 errors specifically  
@app.errorhandler(500)
def handle_500_error(e):
    """Handle 500 errors and return JSON for API endpoints."""
    logger.error(f"500 error on {request.path}: {str(e)}")
    
    # Check if it's an API endpoint
    if request.path.startswith('/upload') or request.path.startswith('/download') or request.path.startswith('/debug') or request.path.startswith('/health'):
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    # For the main page, return normal error handling
    raise e

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'txt', 'docx'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_word_document(formatted_text, title, output_path):
    """Create a Word document from formatted text using professional WordExporter."""
    exporter = WordExporter()
    exporter.export(formatted_text, output_path)

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    try:
        logger.info(f"Upload request received: {request.method} {request.path}")
        logger.info(f"Files in request: {list(request.files.keys())}")
        
        if 'file' not in request.files:
            logger.warning("No file in request")
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            upload_path = None
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                upload_path = os.path.join(UPLOAD_FOLDER, filename)
                logger.info(f"Saving file to: {upload_path}")
                file.save(upload_path)
                
                # Read file content
                logger.info("Reading file content")
                with open(upload_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"File content length: {len(content)} characters")
                
                # Format the transcript using AI
                logger.info("Starting AI formatting")
                try:
                    formatted_text = format_with_claude(content)
                    formatter_used = 'AI Formatter'
                    logger.info("AI formatting completed successfully")
                except Exception as e:
                    logger.error(f"AI formatting failed: {str(e)}")
                    logger.error(f"AI formatting traceback: {traceback.format_exc()}")
                    # Clean up uploaded file on error
                    if upload_path and os.path.exists(upload_path):
                        os.remove(upload_path)
                    return jsonify({'error': f'AI formatting failed: {str(e)}'}), 500
                
                # Create output filename
                base_name = Path(filename).stem
                output_filename = f"{base_name}_formatted.docx"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                logger.info(f"Creating Word document: {output_path}")
                
                # Create Word document
                title = base_name.replace('_', ' ').replace('-', ' ')
                create_word_document(formatted_text, title, output_path)
                
                # Clean up uploaded file
                if upload_path and os.path.exists(upload_path):
                    os.remove(upload_path)
                
                logger.info("Upload processing completed successfully")
                return jsonify({
                    'success': True,
                    'filename': output_filename,
                    'formatter': formatter_used,
                    'preview': formatted_text[:500] + '...' if len(formatted_text) > 500 else formatted_text
                })
                
            except Exception as e:
                logger.error(f"Processing error: {str(e)}")
                logger.error(f"Processing traceback: {traceback.format_exc()}")
                # Clean up uploaded file on any error
                if upload_path and os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({'error': f'Processing failed: {str(e)}', 'traceback': traceback.format_exc()}), 500
        
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'Invalid file type. Please upload .txt or .docx files.'}), 400
    
    except Exception as e:
        logger.error(f"Unhandled upload error: {str(e)}")
        logger.error(f"Unhandled upload traceback: {traceback.format_exc()}")
        # Catch all unhandled exceptions and return JSON
        return jsonify({'error': f'Server error: {str(e)}', 'traceback': traceback.format_exc()}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file."""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'transcript-formatter'})

@app.route('/debug')
def debug_env():
    """Debug endpoint to check environment variables."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    return jsonify({
        'api_key_exists': bool(api_key),
        'api_key_length': len(api_key) if api_key else 0,
        'api_key_prefix': api_key[:10] + '...' if api_key else 'None',
        'all_env_keys': list(os.environ.keys())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(debug=False, host='0.0.0.0', port=port)