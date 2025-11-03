#!/usr/bin/env python3
"""
Test script to verify the transcript formatter generates a DOCX file
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set working directory to backend for template resolution
os.chdir(backend_path)

from formatter import format_transcript

def test_format():
    """Test formatting with the sample transcript"""
    sample_file = Path(__file__).parent / "samples" / "WI0110-2448_-_Last_Days.txt"
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    print(f"📄 Reading sample transcript: {sample_file}")
    with open(sample_file, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    print(f"📊 Transcript length: {len(transcript_text)} characters")
    print("🔄 Formatting transcript (this may take a few minutes)...")
    
    try:
        # Format the transcript
        docx_bytes = format_transcript(transcript_text)
        
        # Save output
        output_file = Path(__file__).parent / "test_local_output.docx"
        with open(output_file, 'wb') as f:
            f.write(docx_bytes)
        
        file_size = len(docx_bytes)
        print(f"✅ Success! Generated DOCX file: {output_file}")
        print(f"📦 File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        
        # Verify it's a valid DOCX (starts with ZIP signature)
        if docx_bytes[:2] == b'PK':
            print("✅ File format verified: Valid DOCX (ZIP archive)")
        else:
            print("⚠️  Warning: File doesn't appear to be a valid DOCX")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during formatting: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_format()
    sys.exit(0 if success else 1)

