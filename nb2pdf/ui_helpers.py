"""
UI helper functions for the nb2pdf Streamlit application.

Provides utilities for rendering previews, generating cover pages,
and handling filenames safely.
"""

import re
import html
from datetime import datetime
from typing import Optional


def safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing or replacing unsafe characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove path components
    filename = filename.replace("\\", "/").split("/")[-1]

    # Remove or replace unsafe characters
    # Keep alphanumeric, dash, underscore, and dot
    safe = re.sub(r'[^\w\-.]', '_', filename)

    # Remove multiple consecutive underscores
    safe = re.sub(r'_+', '_', safe)

    # Remove leading/trailing underscores and dots
    safe = safe.strip('_.')

    # Ensure we have a valid filename
    if not safe:
        safe = "document"

    return safe


def make_cover_html(
    title: str,
    author: Optional[str] = None,
    date: Optional[str] = None,
    theme: str = "light"
) -> str:
    """
    Generate HTML for a cover page.

    Args:
        title: Document title
        author: Author name (optional)
        date: Date string (optional, defaults to current date)
        theme: Color theme ('light' or 'dark')

    Returns:
        HTML string for the cover page
    """
    if date is None:
        date = datetime.now().strftime("%B %d, %Y")

    # Escape HTML entities to prevent XSS
    title_safe = html.escape(title)
    author_safe = html.escape(author) if author else ""
    date_safe = html.escape(date)

    # Theme-based colors
    if theme == "dark":
        bg_color = "#1a1a2e"
        text_color = "#eaeaea"
        accent_color = "#4a9eff"
        subtitle_color = "#b0b0b0"
    else:
        bg_color = "#ffffff"
        text_color = "#1a1a1a"
        accent_color = "#2563eb"
        subtitle_color = "#666666"

    cover = f"""
<div class="cover-page" style="
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 3rem;
    background-color: {bg_color};
    color: {text_color};
    text-align: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
">
    <div style="
        border-top: 4px solid {accent_color};
        border-bottom: 4px solid {accent_color};
        padding: 2rem 0;
        margin: 2rem 0;
    ">
        <h1 style="
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            color: {text_color};
        ">{title_safe}</h1>
    </div>
    {f'<p style="font-size: 1.25rem; color: {subtitle_color}; margin: 0.5rem 0;">{author_safe}</p>' if author else ""}
    <p style="font-size: 1rem; color: {subtitle_color}; margin: 0.5rem 0;">{date_safe}</p>
</div>
"""
    return cover


def make_toc_html(headings: list, theme: str = "light") -> str:
    """
    Generate HTML for a table of contents.

    Args:
        headings: List of tuples (level, text) for each heading
        theme: Color theme ('light' or 'dark')

    Returns:
        HTML string for the table of contents
    """
    if not headings:
        return ""

    # Theme-based colors
    if theme == "dark":
        bg_color = "#1a1a2e"
        text_color = "#eaeaea"
        link_color = "#4a9eff"
    else:
        bg_color = "#ffffff"
        text_color = "#1a1a1a"
        link_color = "#2563eb"

    toc_items = ""
    for level, heading_text in headings:
        indent = (level - 1) * 20
        safe_text = html.escape(heading_text)
        toc_items += f"""
        <li style="margin-left: {indent}px; margin-bottom: 0.5rem;">
            <span style="color: {link_color};">{safe_text}</span>
        </li>
"""

    toc = f"""
<div class="toc-page" style="
    page-break-after: always;
    padding: 3rem;
    background-color: {bg_color};
    color: {text_color};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
">
    <h2 style="
        font-size: 1.75rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: {text_color};
        border-bottom: 2px solid {link_color};
        padding-bottom: 0.5rem;
    ">Table of Contents</h2>
    <ul style="list-style-type: none; padding: 0; margin: 0;">
        {toc_items}
    </ul>
</div>
"""
    return toc


def extract_headings_from_html(html_content: str) -> list:
    """
    Extract headings from HTML content for table of contents.

    Args:
        html_content: HTML string

    Returns:
        List of tuples (level, text) for each heading found
    """
    headings = []
    # Simple regex to find h1-h6 tags
    pattern = r'<h([1-6])[^>]*>(.*?)</h\1>'
    matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)

    for level_str, text in matches:
        level = int(level_str)
        # Remove HTML tags from heading text
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if clean_text:
            headings.append((level, clean_text))

    return headings


def render_preview_html(html_content: str, max_height: int = 500) -> str:
    """
    Wrap HTML content for preview in an iframe-like container.

    Args:
        html_content: HTML string to preview
        max_height: Maximum height of preview container in pixels

    Returns:
        HTML for the preview container
    """
    # We'll use streamlit's components.html for actual rendering
    # This just provides some styling wrapper
    return html_content


def get_backend_status() -> dict:
    """
    Check which PDF backends are available.

    Returns:
        Dictionary with backend names as keys and availability info as values
    """
    status = {}

    # Check WeasyPrint
    try:
        from weasyprint import HTML
        status["weasyprint"] = {"available": True, "message": "Available"}
    except ImportError as e:
        status["weasyprint"] = {
            "available": False,
            "message": f"Not available: {str(e)[:100]}"
        }

    # Check xhtml2pdf
    try:
        from xhtml2pdf import pisa
        status["xhtml2pdf"] = {"available": True, "message": "Available"}
    except ImportError as e:
        status["xhtml2pdf"] = {
            "available": False,
            "message": f"Not available: {str(e)[:100]}"
        }

    return status


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
