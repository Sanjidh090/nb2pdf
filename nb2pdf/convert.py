"""
Conversion utilities for nb2pdf.

Provides functions to convert Jupyter notebooks (.ipynb), Python scripts (.py),
and Markdown files (.md) to HTML and PDF using multiple backends.
"""

import io
from typing import Tuple, Optional, Union
import nbformat
from nbconvert import HTMLExporter
import markdown as md
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


def load_file(file_content: bytes, filename: str) -> Tuple[str, str]:
    """
    Load and decode file content, determining file type.

    Args:
        file_content: Raw bytes of the uploaded file
        filename: Name of the file including extension

    Returns:
        Tuple of (decoded content as string, file extension)

    Raises:
        ValueError: If file cannot be decoded as UTF-8
    """
    try:
        content = file_content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to decode file as UTF-8: {e}")

    # Get file extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return content, ext


def python_to_notebook(py_content: str) -> nbformat.NotebookNode:
    """
    Convert Python script content to a Jupyter Notebook Node.

    Args:
        py_content: Python code as a string

    Returns:
        A NotebookNode containing the code in a single cell
    """
    nb = nbformat.v4.new_notebook()
    code_cell = nbformat.v4.new_code_cell(py_content)
    nb.cells.append(code_cell)
    return nb


def markdown_to_notebook(md_content: str) -> nbformat.NotebookNode:
    """
    Convert Markdown content to a Jupyter Notebook Node.

    Args:
        md_content: Markdown text as a string

    Returns:
        A NotebookNode containing the markdown in a single cell
    """
    nb = nbformat.v4.new_notebook()
    md_cell = nbformat.v4.new_markdown_cell(md_content)
    nb.cells.append(md_cell)
    return nb


def python_to_html_pygments(py_content: str) -> str:
    """
    Convert Python code to syntax-highlighted HTML using Pygments.

    Args:
        py_content: Python code as a string

    Returns:
        HTML string with syntax highlighting
    """
    formatter = HtmlFormatter(
        full=True,
        style="friendly",
        linenos=True,
        cssclass="source",
        title="Python Script"
    )
    return highlight(py_content, PythonLexer(), formatter)


def markdown_to_html(md_content: str) -> str:
    """
    Convert Markdown content to HTML using Python-Markdown.

    Args:
        md_content: Markdown text as a string

    Returns:
        HTML string
    """
    # Enable common extensions for better output
    extensions = [
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite",
        "markdown.extensions.toc",
        "markdown.extensions.nl2br",
    ]
    html_body = md.markdown(md_content, extensions=extensions)

    # Wrap in a full HTML document with styling
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Markdown Document</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #1a1a1a;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }}
        th {{
            background-color: #f4f4f4;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
        }}
        a {{
            color: #0366d6;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
    return html


def notebook_to_html(
    nb: nbformat.NotebookNode,
    theme: str = "light",
    exclude_input: bool = False,
    exclude_output: bool = False
) -> str:
    """
    Convert a Jupyter Notebook to HTML using nbconvert.

    Args:
        nb: A NotebookNode object
        theme: Theme for the HTML output ('light' or 'dark')
        exclude_input: Whether to exclude code cell inputs
        exclude_output: Whether to exclude code cell outputs

    Returns:
        HTML string representation of the notebook
    """
    html_exporter = HTMLExporter()
    html_exporter.theme = theme
    html_exporter.exclude_input_prompt = True
    html_exporter.exclude_output_prompt = True
    html_exporter.exclude_input = exclude_input
    html_exporter.exclude_output = exclude_output

    body, _ = html_exporter.from_notebook_node(nb)
    return body


def html_to_pdf_weasy(html_content: str) -> bytes:
    """
    Convert HTML to PDF using WeasyPrint.

    Args:
        html_content: HTML string to convert

    Returns:
        PDF as bytes

    Raises:
        ImportError: If WeasyPrint is not available
        Exception: If conversion fails
    """
    try:
        from weasyprint import HTML
    except ImportError as e:
        raise ImportError(
            "WeasyPrint is not installed or system dependencies are missing. "
            "Install with: pip install weasyprint. "
            "Also ensure system dependencies are installed (pango, cairo). "
            "See README for platform-specific instructions."
        ) from e

    try:
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except Exception as e:
        raise RuntimeError(f"WeasyPrint conversion failed: {e}") from e


def html_to_pdf_xhtml2pdf(html_content: str) -> bytes:
    """
    Convert HTML to PDF using xhtml2pdf.

    Args:
        html_content: HTML string to convert

    Returns:
        PDF as bytes

    Raises:
        ImportError: If xhtml2pdf is not available
        Exception: If conversion fails
    """
    try:
        from xhtml2pdf import pisa
    except ImportError as e:
        raise ImportError(
            "xhtml2pdf is not installed. Install with: pip install xhtml2pdf"
        ) from e

    try:
        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=result)

        if pisa_status.err:
            raise RuntimeError(f"xhtml2pdf reported {pisa_status.err} errors")

        return result.getvalue()
    except Exception as e:
        raise RuntimeError(f"xhtml2pdf conversion failed: {e}") from e


def try_html_to_pdf(html_content: str) -> Tuple[Optional[bytes], str, Optional[str]]:
    """
    Attempt to convert HTML to PDF using available backends.

    Tries WeasyPrint first, then xhtml2pdf as a fallback.

    Args:
        html_content: HTML string to convert

    Returns:
        Tuple of (PDF bytes or None, backend used, error message or None)
    """
    errors = []

    # Try WeasyPrint first (higher quality output)
    try:
        pdf_bytes = html_to_pdf_weasy(html_content)
        return pdf_bytes, "weasyprint", None
    except (ImportError, RuntimeError) as e:
        errors.append(f"WeasyPrint: {e}")

    # Try xhtml2pdf as fallback
    try:
        pdf_bytes = html_to_pdf_xhtml2pdf(html_content)
        return pdf_bytes, "xhtml2pdf", None
    except (ImportError, RuntimeError) as e:
        errors.append(f"xhtml2pdf: {e}")

    # Both backends failed
    error_msg = "No PDF backend available. Errors: " + "; ".join(errors)
    return None, "none", error_msg


def convert_file_to_html(
    file_content: bytes,
    filename: str,
    theme: str = "light",
    use_pygments_for_py: bool = False
) -> Tuple[str, str]:
    """
    Convert an uploaded file to HTML.

    Args:
        file_content: Raw bytes of the uploaded file
        filename: Name of the file including extension
        theme: Theme for notebook conversion ('light' or 'dark')
        use_pygments_for_py: Use Pygments highlighting for .py files instead of notebook

    Returns:
        Tuple of (HTML string, file type description)

    Raises:
        ValueError: If file type is not supported
    """
    content, ext = load_file(file_content, filename)

    if ext == "ipynb":
        nb = nbformat.read(io.StringIO(content), as_version=4)
        html = notebook_to_html(nb, theme=theme)
        return html, "Jupyter Notebook"

    elif ext == "py":
        if use_pygments_for_py:
            html = python_to_html_pygments(content)
        else:
            nb = python_to_notebook(content)
            html = notebook_to_html(nb, theme=theme)
        return html, "Python Script"

    elif ext == "md":
        html = markdown_to_html(content)
        return html, "Markdown"

    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def full_conversion_pipeline(
    file_content: bytes,
    filename: str,
    theme: str = "light",
    cover_html: Optional[str] = None,
    toc_html: Optional[str] = None
) -> Tuple[Optional[bytes], str, str, Optional[str]]:
    """
    Full conversion pipeline from file to PDF.

    Args:
        file_content: Raw bytes of the uploaded file
        filename: Name of the file including extension
        theme: Theme for conversion ('light' or 'dark')
        cover_html: Optional HTML for cover page
        toc_html: Optional HTML for table of contents

    Returns:
        Tuple of (PDF bytes or None, HTML content, backend used, error message or None)
    """
    # Convert to HTML
    html, file_type = convert_file_to_html(file_content, filename, theme)

    # Add cover page and TOC if provided
    if cover_html or toc_html:
        # Insert cover and TOC before the body content
        insert_content = ""
        if cover_html:
            insert_content += cover_html
        if toc_html:
            insert_content += toc_html

        # Find body tag and insert after it
        if "<body" in html:
            # Find end of body opening tag
            body_start = html.find("<body")
            body_end = html.find(">", body_start) + 1
            html = html[:body_end] + insert_content + html[body_end:]
        else:
            html = insert_content + html

    # Convert HTML to PDF
    pdf_bytes, backend, error = try_html_to_pdf(html)

    return pdf_bytes, html, backend, error
