"""
Vercel serverless handler for transcript formatting.
Synchronous - processes the file and returns the result directly.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import io
import cgi
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            content_type = self.headers.get('content-type', '')
            content_length = int(self.headers.get('content-length', 0))

            if content_length == 0:
                self._send_error(400, 'No data received')
                return

            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
                'CONTENT_LENGTH': str(content_length),
            }

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ=environ
            )

            if 'file' not in form:
                self._send_error(400, 'No file field found')
                return

            file_item = form['file']
            if not hasattr(file_item, 'filename') or not file_item.filename:
                self._send_error(400, 'No file uploaded')
                return

            filename = file_item.filename
            if not filename.lower().endswith('.txt'):
                self._send_error(400, 'Only .txt files are supported')
                return

            file_content = file_item.file.read()
            try:
                text_content = file_content.decode('utf-8', errors='ignore')
            except Exception as e:
                self._send_error(400, f'Error reading file: {str(e)}')
                return

            if not text_content.strip():
                self._send_error(400, 'File is empty')
                return

            # Import and call the backend formatter
            from formatter import format_transcript
            docx_bytes = format_transcript(text_content)

            # Send the .docx file back as the response
            output_filename = filename.replace('.txt', '_formatted.docx')
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="{output_filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(docx_bytes)))
            self.end_headers()
            self.wfile.write(docx_bytes)

        except Exception as e:
            self._send_error(500, f'Server error: {str(e)}')

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_error(self, code, message):
        self.send_response(code)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
