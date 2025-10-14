#!/usr/bin/env python3
"""
Debug script for testing Render deployment issues.
Run this to test if the API endpoints are returning proper JSON.
"""

import os
import requests
import json
import sys

def test_deployment(base_url):
    """Test various endpoints on the deployed application."""
    
    if not base_url.startswith('http'):
        base_url = f'https://{base_url}'
    
    base_url = base_url.rstrip('/')
    
    print(f"Testing deployment at: {base_url}")
    print("-" * 50)
    
    # Test health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Response: {response.text[:200]}")
        
        if 'json' in response.headers.get('content-type', '').lower():
            try:
                data = response.json()
                print(f"   JSON parsed successfully: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"   ERROR: Failed to parse JSON: {e}")
        else:
            print(f"   WARNING: Response is not JSON (content-type: {response.headers.get('content-type')})")
            if '<html' in response.text.lower():
                print("   ERROR: Server is returning HTML instead of JSON!")
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed: {e}")
    
    # Test debug endpoint
    print("\n2. Testing /debug/test endpoint...")
    try:
        response = requests.get(f"{base_url}/debug/test", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Response: {response.text[:200]}")
        
        if 'json' in response.headers.get('content-type', '').lower():
            try:
                data = response.json()
                print(f"   JSON parsed successfully: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"   ERROR: Failed to parse JSON: {e}")
        else:
            print(f"   WARNING: Response is not JSON")
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed: {e}")
    
    # Test upload OPTIONS (CORS preflight)
    print("\n3. Testing /upload OPTIONS (CORS preflight)...")
    try:
        response = requests.options(f"{base_url}/upload", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   CORS Headers:")
        print(f"     Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"     Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        print(f"     Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed: {e}")
    
    # Test main page
    print("\n4. Testing main page (/)...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        if response.status_code == 200:
            if '<title>' in response.text:
                print("   ✓ HTML page loaded successfully")
            else:
                print("   WARNING: Page loaded but doesn't look like HTML")
        else:
            print(f"   ERROR: Main page returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS:")
    print("-" * 50)
    print("If you're seeing HTML instead of JSON on API endpoints, check:")
    print("1. The Flask app is properly deployed and running")
    print("2. Environment variables (especially ANTHROPIC_API_KEY) are set")
    print("3. The Procfile is correctly pointing to web_app:app")
    print("4. No startup errors in Render logs")
    print("5. flask-cors is installed (check requirements.txt)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter your Render app URL (e.g., your-app.onrender.com): ").strip()
    
    test_deployment(url)