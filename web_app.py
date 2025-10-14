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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core dependencies for AI formatting
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())  # Secure secret key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Request logging (simplified)
@app.before_request
def log_request_info():
    """Log all incoming requests for debugging."""
    try:
        logger.info(f"Request: {request.method} {request.path}")
    except Exception as e:
        logger.error(f"Error in before_request: {e}")

# Global error handler to ensure JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions and return JSON."""
    app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    response = jsonify({
        'success': False,
        'error': str(e)
    })
    response.headers['Content-Type'] = 'application/json'
    return response, 500

@app.errorhandler(500)
def handle_500_error(e):
    """Handle 500 errors and return JSON."""
    app.logger.error(f"500 error: {str(e)}")
    response = jsonify({
        'success': False,
        'error': 'Internal server error'
    })
    response.headers['Content-Type'] = 'application/json'
    return response, 500

# Add more specific error handlers
@app.errorhandler(404)
def handle_404_error(e):
    """Handle 404 errors and return JSON for API endpoints."""
    if request.path.startswith('/upload') or request.path.startswith('/download') or request.path.startswith('/debug') or request.path.startswith('/health'):
        response = jsonify({
            'success': False,
            'error': 'Endpoint not found'
        })
        response.headers['Content-Type'] = 'application/json'
        return response, 404
    # For other paths, return normal 404
    return render_template('index.html'), 404

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'txt', 'docx'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Claude AI formatting functionality
def format_with_claude_inline(transcript_text):
    """Format transcript using Claude AI - inline implementation."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    system_prompt = """You are an expert transcript formatter. Transform this raw transcript into a polished, professional document matching broadcast-quality standards.

CRITICAL OUTPUT REQUIREMENTS:
- Output ONLY the formatted transcript content
- NO meta-commentary or explanations
- NO asterisks (*) - these will be converted to proper Word formatting by the export tool
- Provide complete, publication-ready content

DOCUMENT STRUCTURE:

1. TITLE
   - Extract title from context (e.g., "Living in the Last Days")
   - Place at the very top as a header

2. SPEAKER FORMATTING
   - Bold format: **Dr. Billy Wilson:** or **Billy:** or **Male Announcer:**
   - Consolidate fragmented dialogue from same speaker into flowing paragraphs
   - Use **Billy (continued):** when same speaker resumes after interruption

3. SCRIPTURE REFERENCES
   - Bold ALL Bible references: **1 John 2:18**, **2 Timothy 3:1-5**, **Mark 13:13**
   - Normalize format: "1 John chapter 2, verse 18" → **1 John 2:18**
   - Handle ranges: "verse 1 through 5" → **1-5**
   - Italicize the actual quoted scripture text: *"Dear children, we are living..."*

4. NUMBERED TEACHING SECTIONS
   - Identify main teaching points when speaker says: "The first is...", "The second thing...", "Two other things...", "most importantly..."
   - Create bold numbered headers: **1. A Counterculture Mindset**, **2. Spiritual Discernment**
   - Extract descriptive title from the content that follows
   - Place header right before the section begins

5. SPECIAL FORMATTING
   - Italicize show names: *World Impact*
   - Bold organizations on first mention: **ORU**, **Oral Roberts University**
   - Bold websites: **worldimpact.tv**
   - Italicize song titles: *"Give Me Jesus"*
   - Italicize emphasized dialogue/quotes: *"What do you do when..."*

6. SONG LYRICS
   - Format each line separately with ♪ symbols
   - Keep lyrics grouped together
   - Format: ♪ lyric line here ♪
   - Add blank line before and after song sections

7. PARAGRAPH STRUCTURE
   - Create natural 3-6 sentence paragraphs
   - Merge fragmented sentences from same speaker
   - Add blank line between different speakers
   - Keep related thoughts together

8. CLEANUP
   - Fix encoding: â™ª → ♪, â€™ → ', â€œ → ", â€ → "
   - Remove timestamps, divider lines, metadata
   - Remove "..." at beginning/end of document
   - Fix capitalization: "Vistula River" not "Vistula river"
   - Remove stutters: "we know the--we need" → "we need"

9. CLOSING ELEMENTS
   - Keep announcer closing: **Announcer:** This has been...
   - Include copyright notice if present
   - Preserve attribution information

Now format the transcript:"""
    
    try:
        # Send request to Claude with streaming for long requests
        with client.messages.stream(
            model="claude-sonnet-4-5-20250929",
            max_tokens=64000,
            temperature=0.1,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Please format this transcript:\n\n{transcript_text}"
                }
            ]
        ) as stream:
            # Collect the streamed response
            formatted_text = ""
            for text in stream.text_stream:
                formatted_text += text
            
            return formatted_text
            
    except Exception as e:
        raise RuntimeError(f"Claude API error: {str(e)}")

def create_word_document(formatted_text, title, output_path):
    """Create a basic Word document using python-docx."""
    try:
        from docx import Document
        from docx.shared import Inches
        
        # Create document
        doc = Document()
        
        # Add title
        title_para = doc.add_heading(title, level=1)
        
        # Process formatted text and add to document
        lines = formatted_text.split('\n')
        for line in lines:
            if line.strip():
                doc.add_paragraph(line)
            else:
                doc.add_paragraph('')  # Empty line
        
        # Save document
        doc.save(output_path)
        
    except ImportError:
        # Fallback to text file if python-docx not available
        with open(output_path.replace('.docx', '.txt'), 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n\n")
            f.write(formatted_text)

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    try:
        logger.info("=== UPLOAD REQUEST START ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Files in request: {list(request.files.keys()) if request.files else 'None'}")
        
        
        if 'file' not in request.files:
            logger.warning("No file in request")
            response = jsonify({'success': False, 'error': 'No file selected'})
            response.headers['Content-Type'] = 'application/json'
            return response, 400
        
        file = request.files['file']
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            upload_path = None
            try:
                # Save uploaded file
                logger.info("=== FILE PROCESSING START ===")
                filename = secure_filename(file.filename)
                upload_path = os.path.join(UPLOAD_FOLDER, filename)
                logger.info(f"Saving file to: {upload_path}")
                
                try:
                    file.save(upload_path)
                    logger.info("File saved successfully")
                except Exception as save_error:
                    logger.error(f"File save failed: {save_error}")
                    response = jsonify({'success': False, 'error': f'File save failed: {str(save_error)}'})
                    response.headers['Content-Type'] = 'application/json'
                    return response, 500
                
                # Read file content
                logger.info("Reading file content")
                try:
                    with open(upload_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.info(f"File content length: {len(content)} characters")
                except Exception as read_error:
                    logger.error(f"File read failed: {read_error}")
                    # Try different encodings
                    try:
                        with open(upload_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                        logger.info(f"File read with latin-1 encoding, length: {len(content)} characters")
                    except Exception as read_error2:
                        logger.error(f"File read failed with latin-1: {read_error2}")
                        if upload_path and os.path.exists(upload_path):
                            os.remove(upload_path)
                        response = jsonify({'success': False, 'error': f'File read failed: {str(read_error)}'})
                        response.headers['Content-Type'] = 'application/json'
                        return response, 500
                
                # Format the transcript using AI
                logger.info("Starting AI formatting")
                try:
                    formatted_text = format_with_claude_inline(content)
                    formatter_used = 'Claude Sonnet 4.5'
                    logger.info("AI formatting completed successfully")
                except Exception as e:
                    logger.error(f"AI formatting failed: {str(e)}")
                    logger.error(f"AI formatting traceback: {traceback.format_exc()}")
                    # Clean up uploaded file on error
                    if upload_path and os.path.exists(upload_path):
                        os.remove(upload_path)
                    response = jsonify({'success': False, 'error': f'AI formatting failed: {str(e)}'})
                    response.headers['Content-Type'] = 'application/json'
                    return response, 500
                
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
                response = jsonify({
                    'success': True,
                    'filename': output_filename,
                    'formatter': formatter_used,
                    'preview': formatted_text[:500] + '...' if len(formatted_text) > 500 else formatted_text
                })
                response.headers['Content-Type'] = 'application/json'
                return response
                
            except Exception as e:
                logger.error(f"Processing error: {str(e)}")
                logger.error(f"Processing traceback: {traceback.format_exc()}")
                # Clean up uploaded file on any error
                if upload_path and os.path.exists(upload_path):
                    os.remove(upload_path)
                return jsonify({'success': False, 'error': f'Processing failed: {str(e)}'}), 500
        
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({'success': False, 'error': 'Invalid file type. Please upload .txt or .docx files.'}), 400
    
    except Exception as e:
        logger.error(f"Unhandled upload error: {str(e)}")
        logger.error(f"Unhandled upload traceback: {traceback.format_exc()}")
        # Catch all unhandled exceptions and return JSON
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file."""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Download failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'transcript-formatter'})

@app.route('/debug')
def debug_env():
    """Minimal debug endpoint."""
    response = jsonify({
        'success': True,
        'message': 'Debug endpoint working',
        'version': 'minimal',
        'env_count': len(os.environ.keys())
    })
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/test')
def test_endpoint():
    """Simple test endpoint to verify JSON responses."""
    try:
        return jsonify({
            'success': True,
            'message': 'Test successful',
            'timestamp': str(os.environ.get('REQUEST_ID', 'unknown'))
        })
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(debug=False, host='0.0.0.0', port=port)