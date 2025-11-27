"""
nb2pdf - Convert Jupyter notebooks, Python scripts, and Markdown to PDF.

This module provides utilities for converting various code file formats
to PDF documents with support for multiple PDF backends.
"""

from .convert import (
    load_file,
    notebook_to_html,
    html_to_pdf_weasy,
    html_to_pdf_xhtml2pdf,
    try_html_to_pdf,
    markdown_to_html,
    python_to_notebook,
)

from .ui_helpers import (
    render_preview,
    make_cover_html,
    make_toc_html,
    safe_filename,
)

__version__ = "1.0.0"
__all__ = [
    "load_file",
    "notebook_to_html",
    "html_to_pdf_weasy",
    "html_to_pdf_xhtml2pdf",
    "try_html_to_pdf",
    "markdown_to_html",
    "python_to_notebook",
    "render_preview",
    "make_cover_html",
    "make_toc_html",
    "safe_filename",
]
