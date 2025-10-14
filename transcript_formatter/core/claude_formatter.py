"""
Claude-powered transcript formatter using Anthropic's API.

This module provides intelligent transcript formatting using Claude AI,
including speaker name formatting, Scripture reference detection,
encoding fixes, and paragraph structuring.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import anthropic
from anthropic import Anthropic


class ClaudeFormatter:
    """
    A transcript formatter that uses Claude AI for intelligent formatting.
    
    Features:
    - Bold speaker names
    - Detect and bold Scripture references
    - Fix character encoding issues
    - Clean music symbols
    - Create proper paragraph breaks
    - Merge fragmented lines
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude formatter.
        
        Args:
            api_key: Optional API key. If not provided, will load from environment.
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set ANTHROPIC_API_KEY "
                "environment variable or pass api_key parameter."
            )
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Using Claude Sonnet 4.5 - latest model
    
    def format_transcript(self, transcript_text: str, progress_callback=None) -> str:
        """
        Format a transcript using Claude AI.
        
        Args:
            transcript_text: The raw transcript text to format
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Formatted transcript text in markdown format
            
        Raises:
            anthropic.APIError: If the API request fails
            ValueError: If the transcript text is empty
        """
        if not transcript_text or not transcript_text.strip():
            raise ValueError("Transcript text cannot be empty")
        
        if progress_callback:
            progress_callback("Preparing transcript for Claude AI...")
        
        # Prepare the formatting instructions
        system_prompt = self._get_system_prompt()
        
        try:
            if progress_callback:
                progress_callback("Sending transcript to Claude AI...")
            
            # Send request to Claude with streaming for long requests
            with self.client.messages.stream(
                model=self.model,
                max_tokens=64000,  # Maximum allowed for Claude Sonnet 4.5
                temperature=0.1,  # Low temperature for consistent formatting
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please format this transcript:\n\n{transcript_text}"
                    }
                ]
            ) as stream:
                if progress_callback:
                    progress_callback("Processing Claude AI response...")
                
                # Collect the streamed response
                formatted_text = ""
                for text in stream.text_stream:
                    formatted_text += text
            
            if progress_callback:
                progress_callback("Transcript formatting completed!")
            
            return formatted_text
            
        except Exception as e:
            if "anthropic" in str(type(e)).lower() or "api" in str(e).lower():
                error_msg = f"API error: {str(e)}"
            else:
                error_msg = f"Claude API error: {str(e)}"
            if progress_callback:
                progress_callback(f"Error: {error_msg}")
            raise RuntimeError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error during formatting: {str(e)}"
            if progress_callback:
                progress_callback(f"Error: {error_msg}")
            raise RuntimeError(error_msg) from e
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt with formatting instructions for Claude.
        
        Returns:
            The system prompt string with detailed formatting instructions
        """
        return """You are an expert transcript formatter. Transform this raw transcript into a polished, professional document matching broadcast-quality standards.

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

EXAMPLE TRANSFORMATION:

INPUT:
"Well, I wanna talk about five things I believe you need in your life in order to live successfully in the last days. The first is a counterculture mindset. We live in a culture filled..."

OUTPUT:
Well, I wanna talk about five things I believe you need in your life in order to live successfully in the last days.

**1. A Counterculture Mindset**

We live in a culture filled with dishonor and impurity and pride, a cancel culture...

Now format the transcript:"""

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Claude model being used.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model": self.model,
            "provider": "Anthropic",
            "description": "Claude Sonnet 4.5 - Latest advanced language model for text formatting"
        }


def format_with_claude(transcript_text: str, progress_callback=None) -> str:
    """
    Convenience function to format a transcript using Claude AI.
    
    Args:
        transcript_text: The raw transcript text to format
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Formatted transcript text in markdown format
        
    Raises:
        ValueError: If API key is not configured or transcript is empty
        anthropic.APIError: If the API request fails
    """
    formatter = ClaudeFormatter()
    return formatter.format_transcript(transcript_text, progress_callback)