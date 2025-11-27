"""
UI helper functions for the nb2pdf Streamlit application.

This module provides utility functions for rendering UI components,
generating cover pages, and handling file operations.
"""

import re
import html
from typing import Optional
from datetime import datetime


def safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename safe for use in file systems.
    """
    # Remove or replace characters that are invalid in filenames
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe = re.sub(r'\s+', '_', safe)
    safe = re.sub(r'_+', '_', safe)
    safe = safe.strip('._')
    
    # Limit length
    if len(safe) > 200:
        safe = safe[:200]
    
    return safe or 'document'


def make_cover_html(
    title: str,
    author: str = '',
    date: Optional[str] = None,
    theme: str = 'light'
) -> str:
    """
    Generate HTML for a cover page.
    
    Args:
        title: Document title.
        author: Author name (optional).
        date: Date string (optional, defaults to current date).
        theme: Theme for styling ('light' or 'dark').
        
    Returns:
        HTML string for the cover page.
    """
    if date is None:
        date = datetime.now().strftime('%B %d, %Y')
    
    # Escape HTML entities
    title = html.escape(title)
    author = html.escape(author)
    date = html.escape(date)
    
    # Theme colors
    bg_color = '#ffffff' if theme == 'light' else '#1a1a2e'
    text_color = '#333333' if theme == 'light' else '#e0e0e0'
    accent_color = '#0066cc' if theme == 'light' else '#4da6ff'
    
    cover_html = f"""
    <div class="cover-page" style="
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        text-align: center;
        background-color: {bg_color};
        color: {text_color};
        padding: 40px;
    ">
        <div style="
            border: 3px solid {accent_color};
            padding: 60px 40px;
            border-radius: 10px;
            max-width: 600px;
        ">
            <h1 style="
                font-size: 2.5em;
                margin-bottom: 20px;
                color: {accent_color};
                font-weight: 700;
            ">{title}</h1>
            
            {f'<p style="font-size: 1.3em; margin: 20px 0; color: {text_color};">by {author}</p>' if author else ''}
            
            <p style="
                font-size: 1em;
                margin-top: 40px;
                color: #888;
            ">{date}</p>
        </div>
        
        <div style="
            margin-top: 60px;
            font-size: 0.9em;
            color: #888;
        ">
            Generated with nb2pdf
        </div>
    </div>
    """
    return cover_html


def make_toc_html(headings: list, theme: str = 'light') -> str:
    """
    Generate HTML for a Table of Contents.
    
    Args:
        headings: List of (level, text) tuples for headings.
        theme: Theme for styling ('light' or 'dark').
        
    Returns:
        HTML string for the table of contents.
    """
    if not headings:
        return ''
    
    # Theme colors
    bg_color = '#ffffff' if theme == 'light' else '#1a1a2e'
    text_color = '#333333' if theme == 'light' else '#e0e0e0'
    accent_color = '#0066cc' if theme == 'light' else '#4da6ff'
    
    toc_items = []
    for level, text in headings:
        indent = (level - 1) * 20
        toc_items.append(f"""
            <li style="
                margin-left: {indent}px;
                margin-bottom: 8px;
                list-style: none;
            ">
                <span style="color: {accent_color};">•</span> {html.escape(text)}
            </li>
        """)
    
    toc_html = f"""
    <div class="toc-page" style="
        page-break-after: always;
        background-color: {bg_color};
        color: {text_color};
        padding: 40px;
    ">
        <h2 style="
            font-size: 1.8em;
            margin-bottom: 30px;
            color: {accent_color};
            border-bottom: 2px solid {accent_color};
            padding-bottom: 10px;
        ">Table of Contents</h2>
        
        <ul style="padding: 0; margin: 0;">
            {''.join(toc_items)}
        </ul>
    </div>
    """
    return toc_html


def extract_headings(html_content: str) -> list:
    """
    Extract headings from HTML content.
    
    Args:
        html_content: HTML string to parse.
        
    Returns:
        List of (level, text) tuples.
    """
    import re
    
    headings = []
    # Match h1-h6 tags
    pattern = r'<h([1-6])[^>]*>(.*?)</h\1>'
    
    for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
        level = int(match.group(1))
        text = match.group(2)
        # Remove nested tags from heading text
        text = re.sub(r'<[^>]+>', '', text).strip()
        if text:
            headings.append((level, text))
    
    return headings


def render_preview(html_content: str, height: int = 600) -> str:
    """
    Prepare HTML content for preview display.
    
    Args:
        html_content: HTML string to display.
        height: Height of the preview container in pixels.
        
    Returns:
        Wrapped HTML string suitable for iframe preview.
    """
    # Create a preview-friendly wrapper
    preview_html = f"""
    <div style="
        width: 100%;
        height: {height}px;
        overflow: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: white;
    ">
        {html_content}
    </div>
    """
    return preview_html


def get_file_info(filename: str) -> dict:
    """
    Get information about a file based on its name.
    
    Args:
        filename: Name of the file.
        
    Returns:
        Dictionary with file type info.
    """
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    file_types = {
        'ipynb': {
            'type': 'notebook',
            'icon': '📓',
            'description': 'Jupyter Notebook'
        },
        'py': {
            'type': 'python',
            'icon': '🐍',
            'description': 'Python Script'
        },
        'md': {
            'type': 'markdown',
            'icon': '📝',
            'description': 'Markdown Document'
        }
    }
    
    return file_types.get(ext, {
        'type': 'unknown',
        'icon': '📄',
        'description': 'Unknown File Type'
    })


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes.
        
    Returns:
        Human-readable file size string.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
