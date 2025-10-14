#!/usr/bin/env python3
"""Test which Anthropic model IDs are valid."""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

def test_model(model_id):
    """Test if a model ID is valid."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment")
        return False
    
    client = anthropic.Anthropic(api_key=api_key)
    
    print(f"\nTesting model: {model_id}")
    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'Hello'"}]
        )
        print(f"✓ SUCCESS: {model_id} is valid")
        print(f"  Response: {response.content[0].text[:50]}...")
        return True
    except anthropic.BadRequestError as e:
        print(f"✗ FAILED: {model_id} - {str(e)}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {model_id} - {type(e).__name__}: {str(e)}")
        return False

# Test various model IDs
models_to_test = [
    "claude-3-5-sonnet-20241022",  # Known working
    "claude-sonnet-4-5-20250929",  # User requested
    "claude-3-opus-20240229",      # Opus
    "claude-3-haiku-20240307",     # Haiku
    "claude-3-5-sonnet-latest",    # Latest alias
]

print("Testing Anthropic Model IDs")
print("=" * 50)

working_models = []
for model in models_to_test:
    if test_model(model):
        working_models.append(model)

print("\n" + "=" * 50)
print("Summary:")
print(f"Working models: {working_models}")
print("\nRecommendation: Use 'claude-3-5-sonnet-20241022' for best results")