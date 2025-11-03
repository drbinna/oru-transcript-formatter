#!/usr/bin/env python3
"""
Test script to verify the API endpoint generates a DOCX file
"""
import requests
import sys
from pathlib import Path

def test_api():
    """Test the /format API endpoint"""
    api_url = "http://localhost:8000/format"
    sample_file = Path(__file__).parent / "samples" / "WI0110-2448_-_Last_Days.txt"
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    print(f"📄 Testing API endpoint: {api_url}")
    print(f"📄 Using sample file: {sample_file}")
    
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file.name, f, 'text/plain')}
            print("🔄 Sending request to API (this may take a few minutes)...")
            
            # Use a longer timeout for Claude AI processing
            response = requests.post(api_url, files=files, timeout=600)
        
        if response.status_code == 200:
            # Save the response
            output_file = Path(__file__).parent / "test_api_output.docx"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Success! Generated DOCX file via API: {output_file}")
            print(f"📦 File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            
            # Verify it's a valid DOCX
            if response.content[:2] == b'PK':
                print("✅ File format verified: Valid DOCX (ZIP archive)")
                return True
            else:
                print("⚠️  Warning: File doesn't appear to be a valid DOCX")
                return False
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The API may still be processing.")
        print("   Try checking the server logs or increase the timeout.")
        return False
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)

