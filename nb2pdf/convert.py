"""
Conversion utilities for nb2pdf.

This module provides functions to convert Jupyter notebooks, Python scripts,
and Markdown files to HTML and PDF using multiple backends.
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
    Load a file and return its content and type.
    
    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Name of the file with extension.
        
    Returns:
        Tuple of (decoded content string, file type: 'notebook', 'python', or 'markdown')
        
    Raises:
        ValueError: If file type is not supported.
    """
    content = file_content.decode("utf-8")
    
    if filename.endswith('.ipynb'):
        return content, 'notebook'
    elif filename.endswith('.py'):
        return content, 'python'
    elif filename.endswith('.md'):
        return content, 'markdown'
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def python_to_notebook(py_content: str) -> nbformat.NotebookNode:
    """
    Convert Python script content to a Notebook Node.
    
    Args:
        py_content: Python script content as string.
        
    Returns:
        A NotebookNode object containing the Python code.
    """
    nb = nbformat.v4.new_notebook()
    
    # Split by cell markers if present, otherwise single cell
    if "# %%" in py_content or "# In[" in py_content:
        # Split on common cell markers
        import re
        cells = re.split(r'(?:^# %%.*$|^# In\[\d*\]:.*$)', py_content, flags=re.MULTILINE)
        for cell_content in cells:
            cell_content = cell_content.strip()
            if cell_content:
                code_cell = nbformat.v4.new_code_cell(cell_content)
                nb.cells.append(code_cell)
    else:
        code_cell = nbformat.v4.new_code_cell(py_content)
        nb.cells.append(code_cell)
    
    return nb


def markdown_to_html(md_content: str, theme: str = 'light') -> str:
    """
    Convert Markdown content to HTML.
    
    Args:
        md_content: Markdown content as string.
        theme: Theme for styling ('light' or 'dark').
        
    Returns:
        HTML string with styling.
    """
    # Convert markdown to HTML
    html_body = md.markdown(
        md_content,
        extensions=['fenced_code', 'tables', 'toc', 'codehilite', 'nl2br']
    )
    
    # Apply theme-based styling
    bg_color = '#ffffff' if theme == 'light' else '#1e1e1e'
    text_color = '#333333' if theme == 'light' else '#e0e0e0'
    code_bg = '#f5f5f5' if theme == 'light' else '#2d2d2d'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
                background-color: {bg_color};
                color: {text_color};
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                border-bottom: 1px solid #eee;
                padding-bottom: 0.3em;
            }}
            code {{
                background-color: {code_bg};
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
            pre {{
                background-color: {code_bg};
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            pre code {{
                padding: 0;
                background: none;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background-color: {code_bg};
            }}
            blockquote {{
                border-left: 4px solid #0066cc;
                margin: 1em 0;
                padding-left: 1em;
                color: #666;
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
    </html>
    """
    return html


def python_to_html(py_content: str, theme: str = 'light') -> str:
    """
    Convert Python script to syntax-highlighted HTML using Pygments.
    
    Args:
        py_content: Python script content.
        theme: Theme for styling ('light' or 'dark').
        
    Returns:
        HTML string with syntax highlighting.
    """
    style = 'default' if theme == 'light' else 'monokai'
    formatter = HtmlFormatter(
        style=style,
        linenos=True,
        cssclass='source',
        full=True,
        lineanchors='line'
    )
    
    html = highlight(py_content, PythonLexer(), formatter)
    return html


def notebook_to_html(
    nb_content: str,
    theme: str = 'light',
    exclude_input: bool = False,
    exclude_output: bool = False
) -> str:
    """
    Convert a Jupyter notebook to HTML.
    
    Args:
        nb_content: Notebook content as JSON string.
        theme: Theme for export ('light' or 'dark').
        exclude_input: Whether to exclude code input cells.
        exclude_output: Whether to exclude code output cells.
        
    Returns:
        HTML string representation of the notebook.
    """
    nb = nbformat.read(io.StringIO(nb_content), as_version=4)
    
    html_exporter = HTMLExporter()
    html_exporter.theme = theme
    html_exporter.exclude_input_prompt = True
    html_exporter.exclude_output_prompt = True
    html_exporter.exclude_input = exclude_input
    html_exporter.exclude_output = exclude_output
    
    body, resources = html_exporter.from_notebook_node(nb)
    return body


def html_to_pdf_weasy(html_content: str, page_size: str = 'A4') -> bytes:
    """
    Convert HTML to PDF using WeasyPrint.
    
    Args:
        html_content: HTML string to convert.
        page_size: Page size (e.g., 'A4', 'Letter').
        
    Returns:
        PDF content as bytes.
        
    Raises:
        ImportError: If weasyprint is not installed.
        Exception: If conversion fails.
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise ImportError(
            "WeasyPrint is not installed. Install it with: pip install weasyprint"
        )
    
    # Add page size CSS
    page_css = CSS(string=f"""
        @page {{
            size: {page_size};
            margin: 2cm;
        }}
    """)
    
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[page_css])
    return pdf_bytes


def html_to_pdf_xhtml2pdf(html_content: str, page_size: str = 'A4') -> bytes:
    """
    Convert HTML to PDF using xhtml2pdf.
    
    Args:
        html_content: HTML string to convert.
        page_size: Page size (e.g., 'A4', 'Letter').
        
    Returns:
        PDF content as bytes.
        
    Raises:
        ImportError: If xhtml2pdf is not installed.
        Exception: If conversion fails.
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        raise ImportError(
            "xhtml2pdf is not installed. Install it with: pip install xhtml2pdf"
        )
    
    # Add page size meta
    page_sizes = {
        'A4': '@page { size: A4; margin: 2cm; }',
        'Letter': '@page { size: letter; margin: 1in; }',
        'Legal': '@page { size: legal; margin: 1in; }',
    }
    
    page_style = page_sizes.get(page_size, page_sizes['A4'])
    
    # Inject page style into HTML
    if '<style>' in html_content:
        html_content = html_content.replace('<style>', f'<style>{page_style}')
    else:
        html_content = html_content.replace(
            '</head>',
            f'<style>{page_style}</style></head>'
        )
    
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        io.StringIO(html_content),
        dest=result,
        encoding='utf-8'
    )
    
    if pisa_status.err:
        raise Exception(f"xhtml2pdf conversion failed with {pisa_status.err} errors")
    
    return result.getvalue()


def try_html_to_pdf(
    html_content: str,
    page_size: str = 'A4'
) -> Tuple[Optional[bytes], str, list]:
    """
    Attempt to convert HTML to PDF using available backends.
    
    Tries weasyprint first, then xhtml2pdf as fallback.
    
    Args:
        html_content: HTML string to convert.
        page_size: Page size (e.g., 'A4', 'Letter').
        
    Returns:
        Tuple of (pdf_bytes or None, backend_used, list of warnings)
    """
    warnings = []
    
    # Try WeasyPrint first
    try:
        pdf_bytes = html_to_pdf_weasy(html_content, page_size)
        return pdf_bytes, 'weasyprint', warnings
    except ImportError as e:
        warnings.append(f"WeasyPrint not available: {e}")
    except Exception as e:
        warnings.append(f"WeasyPrint failed: {e}")
    
    # Try xhtml2pdf as fallback
    try:
        pdf_bytes = html_to_pdf_xhtml2pdf(html_content, page_size)
        return pdf_bytes, 'xhtml2pdf', warnings
    except ImportError as e:
        warnings.append(f"xhtml2pdf not available: {e}")
    except Exception as e:
        warnings.append(f"xhtml2pdf failed: {e}")
    
    # No backends available
    return None, 'none', warnings
