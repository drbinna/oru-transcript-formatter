"""
Fast transcript summarizer using Claude Haiku.
Single API call, no chunking - processes the whole transcript at once.
"""

import os
import io
from anthropic import Anthropic
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from dotenv import load_dotenv

load_dotenv()

SUMMARIZE_PROMPT = """You are a professional transcript summarizer. Your job is to read a raw meeting or video transcript and produce a clean, readable summary document.

Structure your output EXACTLY like this:

TITLE: [A concise title for this transcript]

OVERVIEW:
[2-3 sentence summary of what this transcript is about]

KEY POINTS:
- [Key point 1]
- [Key point 2]
- [Key point 3]
- [Add more as needed, each on its own line starting with -]

MAIN DISCUSSION:
[3-5 paragraphs summarizing the main content in clear, professional prose. Capture the essential ideas, decisions, and discussion in a logical flow.]

ACTION ITEMS (if any):
- [Action item 1, or write "None identified" if there are no action items]

Keep the summary concise, professional, and easy to read. Remove filler words, repetition, and irrelevant chatter."""


def format_transcript(text: str, title: str = None) -> bytes:
    """Summarize a transcript using a single Claude Haiku call. Returns .docx bytes."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")

    client = Anthropic(api_key=api_key, timeout=55, max_retries=1)

    # Truncate very long transcripts to stay within token limits
    # Claude Haiku can handle ~150k tokens, but keep it reasonable for speed
    max_chars = 80000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Transcript truncated for processing]"

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        temperature=0.2,
        system=SUMMARIZE_PROMPT,
        messages=[{"role": "user", "content": f"Please summarize this transcript:\n\n{text}"}]
    )

    summary_text = response.content[0].text

    # Build a clean Word document from the summary
    return _build_docx(summary_text)


def _build_docx(summary_text: str) -> bytes:
    """Convert the plain-text summary into a formatted .docx file."""
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    lines = summary_text.strip().split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('TITLE:'):
            title_text = line.replace('TITLE:', '').strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(title_text)
            run.bold = True
            run.font.size = Pt(18)
            run.font.name = 'Calibri'
            p.paragraph_format.space_after = Pt(12)

        elif line in ('OVERVIEW:', 'KEY POINTS:', 'MAIN DISCUSSION:', 'ACTION ITEMS (if any):'):
            p = doc.add_paragraph()
            run = p.add_run(line.rstrip(':'))
            run.bold = True
            run.font.size = Pt(13)
            run.font.name = 'Calibri'
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)

        elif line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            run = p.add_run(line[2:])
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
            p.paragraph_format.space_after = Pt(3)

        elif line:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(6)

        i += 1

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()
