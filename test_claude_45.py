#!/usr/bin/env python3
"""
Test Claude Sonnet 4.5 with detailed error reporting.
This will help identify why it works locally but fails on Render.
"""

import os
import sys
import json
import traceback
from dotenv import load_dotenv
import anthropic

load_dotenv()

def test_claude_45_detailed():
    """Test Claude Sonnet 4.5 with detailed diagnostics."""
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        return False
    
    print("Testing Claude Sonnet 4.5 Connection")
    print("=" * 50)
    print(f"API Key Length: {len(api_key)} characters")
    print(f"API Key Preview: {api_key[:8]}...")
    print(f"Python Version: {sys.version}")
    print(f"Anthropic SDK Version: {anthropic.__version__}")
    
    # Create client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Test 1: Simple message with Claude Sonnet 4.5
    print("\n1. Testing Claude Sonnet 4.5...")
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print(f"✓ SUCCESS: Claude Sonnet 4.5 works!")
        print(f"Response: {response.content[0].text}")
        
        # Get usage info if available
        if hasattr(response, 'usage'):
            print(f"Tokens used: {response.usage}")
            
    except anthropic.APIError as e:
        print(f"✗ API ERROR: {e}")
        print(f"Status Code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
        print(f"Response Body: {e.response if hasattr(e, 'response') else 'N/A'}")
        print(f"Full Error: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        print(f"Full Traceback: {traceback.format_exc()}")
    
    # Test 2: Try with different max_tokens values
    print("\n2. Testing different max_tokens values...")
    for max_tokens in [100, 1000, 4096, 8192]:
        try:
            print(f"   Testing max_tokens={max_tokens}...", end=" ")
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": "Count to 5"}]
            )
            print("✓")
        except Exception as e:
            print(f"✗ Failed: {str(e)[:50]}")
    
    # Test 3: Compare with Claude 3.5 Sonnet
    print("\n3. Comparing with Claude 3.5 Sonnet...")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print(f"✓ Claude 3.5 Sonnet works as fallback")
    except Exception as e:
        print(f"✗ Claude 3.5 Sonnet also failed: {e}")
    
    # Test 4: Check API headers and version
    print("\n4. Testing with explicit API version...")
    try:
        # Create client with explicit version
        client_with_version = anthropic.Anthropic(
            api_key=api_key,
            default_headers={
                "anthropic-version": "2023-06-01"
            }
        )
        response = client_with_version.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=100,
            messages=[{"role": "user", "content": "Test"}]
        )
        print(f"✓ Works with explicit API version")
    except Exception as e:
        print(f"✗ Failed with explicit version: {e}")
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC COMPLETE")
    
    # Environment check for Render
    print("\nEnvironment Variables (Render-specific):")
    render_vars = ['RENDER', 'RENDER_SERVICE_NAME', 'RENDER_SERVICE_TYPE', 'IS_PULL_REQUEST']
    for var in render_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")

if __name__ == "__main__":
    test_claude_45_detailed()