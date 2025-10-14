import click
import os
from pathlib import Path
from docx import Document
from docx.shared import Inches
from .core.claude_formatter import ClaudeFormatter, format_with_claude
from .exporters.word_exporter import WordExporter
import anthropic


@click.group()
def cli():
    """Transcript formatter CLI tools."""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, readable=True))
@click.option('-o', '--output', 'output_file', 
              type=click.Path(), 
              help='Output file path (supports .docx)')
@click.option('--format', 'output_format', 
              type=click.Choice(['docx'], case_sensitive=False),
              default='docx',
              help='Output format (default: docx)')
def format(input_file, output_file, output_format):
    """Convert raw transcript text files into formatted documents using Claude AI."""
    
    # Determine output file if not provided
    if not output_file:
        input_path = Path(input_file)
        output_file = input_path.with_suffix(f'.{output_format.lower()}')
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    # Use Claude AI formatter
    try:
        click.echo("Using Claude AI formatter...")
        
        def progress_callback(message):
            click.echo(f"  {message}")
        
        formatted_text = format_with_claude(raw_text, progress_callback)
        
    except (anthropic.APIError, ValueError, RuntimeError) as e:
        click.echo(f"Claude AI formatting failed: {e}")
        click.echo("Please check your ANTHROPIC_API_KEY environment variable and try again.")
        raise
    
    # Export to desired format
    if output_format.lower() == 'docx':
        # Use the professional WordExporter
        exporter = WordExporter()
        exporter.export(formatted_text, output_file)
    
    click.echo(f"Successfully converted {input_file} to {output_file}")


@cli.command()
@click.argument('input_path', type=click.Path(exists=True, readable=True))
def display(input_path):
    """Display formatted content from Word documents in the input folder."""
    path = Path(input_path)
    
    if path.is_file() and path.suffix.lower() == '.docx':
        # Display single Word document
        _display_word_document(path)
    elif path.is_dir():
        # Display all Word documents in directory
        docx_files = list(path.glob('*.docx'))
        if not docx_files:
            click.echo(f"No Word documents found in {input_path}")
            return
        
        for docx_file in docx_files:
            click.echo(f"\n{'='*60}")
            click.echo(f"Document: {docx_file.name}")
            click.echo(f"{'='*60}")
            _display_word_document(docx_file)
    else:
        click.echo("Please provide a .docx file or directory containing .docx files")


def _display_word_document(docx_path):
    """Display the content of a Word document with formatting indicators."""
    try:
        doc = Document(docx_path)
        
        for i, paragraph in enumerate(doc.paragraphs):
            if not paragraph.text.strip():
                continue
                
            # Analyze paragraph formatting
            alignment = ""
            if paragraph.alignment == 1:  # CENTER
                alignment = "[CENTER] "
            
            # Analyze run formatting
            formatted_text = ""
            for run in paragraph.runs:
                text = run.text
                if run.bold:
                    text = f"**{text}**"
                if run.italic:
                    text = f"*{text}*"
                formatted_text += text
            
            # Display with formatting indicators
            if alignment or any(run.bold for run in paragraph.runs):
                click.echo(f"{alignment}{formatted_text}")
            else:
                click.echo(formatted_text)
        
    except Exception as e:
        click.echo(f"Error reading {docx_path}: {e}")


def main():
    """Entry point for backward compatibility."""
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ['format', 'display', '--help']:
        # Old-style usage - treat as format command
        sys.argv.insert(1, 'format')
    cli()


if __name__ == '__main__':
    cli()