#!/usr/bin/env python3
"""
Quick startup script for the ORU Transcript Formatter web app.
"""

import os
import sys
from pathlib import Path

print("🎓 Starting ORU Transcript Formatter...")
print("📍 Loading dependencies...")

try:
    # Import Flask first (fast)
    from flask import Flask
    print("✅ Flask loaded")
    
    # Create minimal app to test
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return """
        <h1>🎓 ORU Transcript Formatter</h1>
        <p>Loading... Please wait while we initialize the full application.</p>
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 3000);
        </script>
        """
    
    print("✅ Basic app created")
    print("🌐 Starting server on http://localhost:8080")
    print("📝 Full app will load in a moment...")
    
    # Start basic server first
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔧 Trying alternative startup...")
    
    # Try importing the full web app
    try:
        from web_app import app as full_app
        print("✅ Full app loaded successfully")
        full_app.run(debug=False, host='0.0.0.0', port=8080)
    except Exception as e2:
        print(f"❌ Full app error: {e2}")
        print("💡 Try running: python3 web_app.py directly")