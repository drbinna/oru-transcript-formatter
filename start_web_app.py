#!/usr/bin/env python3
"""
Startup script for the transcript formatter web application.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the web app
from web_app import app

if __name__ == '__main__':
    print("🚀 Starting Transcript Formatter Web Application")
    print("📍 ORU Transcript Formatter - AI Powered")
    print("🌐 Access the application at: http://localhost:8080")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        print("⚠️  Warning: .env file not found. AI features may not work.")
        print("   Please create a .env file with your ANTHROPIC_API_KEY")
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)