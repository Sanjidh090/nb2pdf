"""
nb2pdf - Streamlit Web Application

A web application for converting Jupyter notebooks (.ipynb), Python scripts (.py),
and Markdown files (.md) to high-quality PDF documents.

Features:
- File upload support for .ipynb, .py, .md files
- GitHub Gist/URL support for fetching files
- Cover page customization (title, author, date)
- Table of Contents generation
- Theme selection (light/dark)
- Page size and margin options
- Multi-backend PDF conversion with fallbacks
- Live HTML preview

Author: nb2pdf contributors
"""

import streamlit as st
import io
import base64
import requests
import re
from datetime import datetime
from pathlib import Path

# Import conversion utilities
from nb2pdf.convert import (
    load_file,
    notebook_to_html,
    markdown_to_html,
    python_to_notebook,
    python_to_html,
    try_html_to_pdf,
)
from nb2pdf.ui_helpers import (
    make_cover_html,
    make_toc_html,
    extract_headings,
    safe_filename,
    get_file_info,
    format_file_size,
)

import nbformat
from nbconvert import HTMLExporter


# --- Page Configuration ---
st.set_page_config(
    page_title="nb2pdf - Code to PDF Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Custom CSS ---
def load_custom_css():
    """Load custom CSS for enhanced styling."""
    st.markdown("""
    <style>
        /* Main header styling */
        .main-header {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 10px 0;
            margin-bottom: 20px;
            border-bottom: 2px solid #0066cc;
        }
        
        .main-header h1 {
            color: #0066cc;
            margin: 0;
            font-size: 2em;
        }
        
        /* Card styling */
        .info-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #0066cc;
        }
        
        /* Success message styling */
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 15px;
            color: #155724;
        }
        
        /* Warning message styling */
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 8px;
            padding: 15px;
            color: #856404;
        }
        
        /* Preview container */
        .preview-container {
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            padding: 20px;
            margin: 10px 0;
            max-height: 600px;
            overflow: auto;
        }
        
        /* File info badge */
        .file-badge {
            display: inline-block;
            background: #0066cc;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 5px 0;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 1rem;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Download button specific */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #28a745 0%, #20853a 100%);
            color: white;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)


def get_logo_svg():
    """Load and return the logo SVG."""
    logo_path = Path(__file__).parent / "assets" / "logo.svg"
    try:
        with open(logo_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback inline SVG
        return """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40" width="120" height="40">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#4da6ff;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#0066cc;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect x="5" y="5" width="22" height="30" rx="2" fill="url(#grad1)" />
            <rect x="9" y="12" width="14" height="2" rx="1" fill="white" />
            <rect x="9" y="17" width="14" height="2" rx="1" fill="white" />
            <rect x="9" y="22" width="10" height="2" rx="1" fill="white" />
            <path d="M32 20 L42 20 L38 15 M42 20 L38 25" stroke="url(#grad1)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            <rect x="47" y="5" width="22" height="30" rx="2" fill="#e74c3c" />
            <text x="58" y="25" font-family="Arial" font-size="10" font-weight="bold" fill="white" text-anchor="middle">PDF</text>
            <text x="78" y="27" font-family="Arial" font-size="16" font-weight="bold" fill="url(#grad1)">nb2pdf</text>
        </svg>
        """


def render_header():
    """Render the application header with logo."""
    logo_svg = get_logo_svg()
    st.markdown(f"""
    <div class="main-header">
        {logo_svg}
        <div>
            <h1>Code to PDF Converter</h1>
            <p style="margin: 0; color: #666;">Convert notebooks, scripts, and markdown to beautiful PDFs</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def fetch_from_url(url: str) -> tuple:
    """
    Fetch file content from a URL (GitHub Gist or raw file).
    
    Args:
        url: URL to fetch from.
        
    Returns:
        Tuple of (content bytes, filename, error message or None)
    """
    try:
        # Handle GitHub Gist URLs
        if 'gist.github.com' in url:
            # Convert to raw URL
            gist_match = re.search(r'gist\.github\.com/([^/]+)/([a-f0-9]+)', url)
            if gist_match:
                gist_id = gist_match.group(2)
                api_url = f"https://api.github.com/gists/{gist_id}"
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                gist_data = response.json()
                
                # Get the first file from the gist
                files = gist_data.get('files', {})
                if files:
                    first_file = list(files.values())[0]
                    content = first_file['content'].encode('utf-8')
                    filename = first_file['filename']
                    return content, filename, None
                else:
                    return None, None, "No files found in gist"
        
        # Handle raw GitHub URLs or other direct URLs
        elif 'raw.githubusercontent.com' in url or url.endswith(('.ipynb', '.py', '.md')):
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.content
            
            # Extract filename from URL
            filename = url.split('/')[-1].split('?')[0]
            if not any(filename.endswith(ext) for ext in ['.ipynb', '.py', '.md']):
                filename = 'downloaded_file.ipynb'  # Default
            
            return content, filename, None
        
        else:
            # Try direct download
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content, 'downloaded_file.ipynb', None
            
    except requests.RequestException as e:
        return None, None, f"Failed to fetch URL: {str(e)}"
    except Exception as e:
        return None, None, f"Error processing URL: {str(e)}"


def convert_to_html(
    content: bytes,
    filename: str,
    theme: str = 'light',
    use_pygments: bool = False
) -> tuple:
    """
    Convert file content to HTML based on file type.
    
    Args:
        content: File content as bytes.
        filename: Name of the file.
        theme: Theme for styling.
        use_pygments: Whether to use Pygments for Python files.
        
    Returns:
        Tuple of (html_content, error_message or None)
    """
    try:
        text_content, file_type = load_file(content, filename)
        
        if file_type == 'notebook':
            html_content = notebook_to_html(text_content, theme=theme)
        elif file_type == 'python':
            if use_pygments:
                html_content = python_to_html(text_content, theme=theme)
            else:
                # Convert to notebook first, then to HTML
                nb = python_to_notebook(text_content)
                html_exporter = HTMLExporter()
                html_exporter.theme = theme
                html_exporter.exclude_input_prompt = True
                html_exporter.exclude_output_prompt = True
                html_content, _ = html_exporter.from_notebook_node(nb)
        elif file_type == 'markdown':
            html_content = markdown_to_html(text_content, theme=theme)
        else:
            return None, f"Unsupported file type: {file_type}"
        
        return html_content, None
        
    except Exception as e:
        return None, f"Conversion error: {str(e)}"


def add_cover_and_toc(
    html_content: str,
    include_cover: bool,
    cover_title: str,
    cover_author: str,
    cover_date: str,
    include_toc: bool,
    theme: str
) -> str:
    """Add cover page and table of contents to HTML content."""
    
    prefix_html = ""
    
    if include_cover:
        prefix_html += make_cover_html(
            title=cover_title,
            author=cover_author,
            date=cover_date if cover_date else None,
            theme=theme
        )
    
    if include_toc:
        headings = extract_headings(html_content)
        if headings:
            prefix_html += make_toc_html(headings, theme=theme)
    
    if prefix_html:
        # Insert after <body> tag if it exists
        if '<body' in html_content:
            html_content = re.sub(
                r'(<body[^>]*>)',
                r'\1' + prefix_html,
                html_content,
                count=1
            )
        else:
            html_content = prefix_html + html_content
    
    return html_content


def main():
    """Main application function."""
    
    # Load custom CSS
    load_custom_css()
    
    # Render header
    render_header()
    
    # --- Sidebar Options ---
    with st.sidebar:
        st.header("⚙️ Options")
        
        # Theme selection
        st.subheader("🎨 Appearance")
        theme = st.selectbox(
            "Theme",
            options=['light', 'dark'],
            index=0,
            help="Choose the color theme for the output"
        )
        
        # Page settings
        st.subheader("📄 Page Settings")
        page_size = st.selectbox(
            "Page Size",
            options=['A4', 'Letter', 'Legal'],
            index=0,
            help="Select the page size for PDF output"
        )
        
        # Cover page options
        st.subheader("📕 Cover Page")
        include_cover = st.checkbox("Include Cover Page", value=False)
        
        cover_title = ""
        cover_author = ""
        cover_date = ""
        
        if include_cover:
            cover_title = st.text_input(
                "Title",
                value="",
                placeholder="Document Title"
            )
            cover_author = st.text_input(
                "Author",
                value="",
                placeholder="Author Name"
            )
            cover_date = st.text_input(
                "Date",
                value=datetime.now().strftime('%B %d, %Y'),
                help="Leave empty for current date"
            )
        
        # Table of Contents
        st.subheader("📑 Table of Contents")
        include_toc = st.checkbox(
            "Include Table of Contents",
            value=False,
            help="Generate TOC from headings"
        )
        
        # Python-specific options
        st.subheader("🐍 Python Options")
        use_pygments = st.checkbox(
            "Use Pygments Highlighting",
            value=False,
            help="Use Pygments for syntax highlighting instead of notebook format"
        )
        
        # About section
        st.divider()
        st.caption("""
        **nb2pdf** v1.0.0
        
        Convert Jupyter notebooks, Python scripts, and Markdown files to PDF.
        
        [GitHub Repository](https://github.com/Sanjidh090/nb2pdf)
        """)
    
    # --- Main Content Area ---
    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 From URL"])
    
    with tab1:
        st.markdown("""
        <div class="info-card">
            <strong>📤 Upload your file</strong><br>
            Supported formats: Jupyter Notebook (.ipynb), Python Script (.py), Markdown (.md)
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['ipynb', 'py', 'md'],
            help="Upload a Jupyter notebook, Python script, or Markdown file"
        )
        
        if uploaded_file is not None:
            file_content = uploaded_file.getvalue()
            filename = uploaded_file.name
            process_file(
                file_content, filename, theme, page_size,
                include_cover, cover_title, cover_author, cover_date,
                include_toc, use_pygments
            )
    
    with tab2:
        st.markdown("""
        <div class="info-card">
            <strong>🌐 Fetch from URL</strong><br>
            Enter a GitHub Gist URL or raw file URL
        </div>
        """, unsafe_allow_html=True)
        
        url_input = st.text_input(
            "Enter URL",
            placeholder="https://gist.github.com/username/gist_id",
            help="GitHub Gist URL or direct link to .ipynb/.py/.md file"
        )
        
        fetch_button = st.button("🔍 Fetch File", use_container_width=True)
        
        if fetch_button and url_input:
            with st.spinner("Fetching file from URL..."):
                file_content, filename, error = fetch_from_url(url_input)
                
                if error:
                    st.error(f"❌ {error}")
                elif file_content and filename:
                    st.success(f"✅ Fetched: **{filename}**")
                    process_file(
                        file_content, filename, theme, page_size,
                        include_cover, cover_title, cover_author, cover_date,
                        include_toc, use_pygments
                    )


def process_file(
    file_content: bytes,
    filename: str,
    theme: str,
    page_size: str,
    include_cover: bool,
    cover_title: str,
    cover_author: str,
    cover_date: str,
    include_toc: bool,
    use_pygments: bool
):
    """Process the uploaded/fetched file and display conversion options."""
    
    # Display file info
    file_info = get_file_info(filename)
    file_size = format_file_size(len(file_content))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File", filename)
    with col2:
        st.metric("Type", f"{file_info['icon']} {file_info['description']}")
    with col3:
        st.metric("Size", file_size)
    
    st.divider()
    
    # Convert to HTML
    with st.spinner("Converting to HTML..."):
        html_content, error = convert_to_html(
            file_content, filename, theme, use_pygments
        )
    
    if error:
        st.error(f"❌ {error}")
        return
    
    # Add cover page and TOC if requested
    if include_cover or include_toc:
        title = cover_title if cover_title else filename.rsplit('.', 1)[0]
        html_content = add_cover_and_toc(
            html_content,
            include_cover, title, cover_author, cover_date,
            include_toc, theme
        )
    
    # Store HTML in session state for preview
    st.session_state['html_content'] = html_content
    st.session_state['filename'] = filename
    
    # Preview and Download section
    col_preview, col_download = st.columns([2, 1])
    
    with col_preview:
        st.subheader("👁️ Preview")
        
        # Create expandable preview
        with st.expander("Show HTML Preview", expanded=True):
            st.components.v1.html(html_content, height=500, scrolling=True)
    
    with col_download:
        st.subheader("📥 Download")
        
        # Convert to PDF button
        if st.button("🔄 Generate PDF", use_container_width=True, type="primary"):
            with st.spinner("Generating PDF..."):
                pdf_bytes, backend_used, warnings = try_html_to_pdf(
                    html_content, page_size
                )
            
            # Show warnings if any
            for warning in warnings:
                st.warning(f"⚠️ {warning}")
            
            if pdf_bytes:
                st.success(f"✅ PDF generated using **{backend_used}**")
                
                # Create download filename
                output_filename = safe_filename(filename.rsplit('.', 1)[0]) + '.pdf'
                
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=output_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Show PDF size
                pdf_size = format_file_size(len(pdf_bytes))
                st.caption(f"PDF Size: {pdf_size}")
            else:
                st.error("❌ PDF generation failed. No backends available.")
                st.markdown("""
                <div class="warning-box">
                    <strong>No PDF backends available!</strong><br><br>
                    To generate PDFs, install one of these packages:
                    <ul>
                        <li><code>pip install weasyprint</code> (recommended)</li>
                        <li><code>pip install xhtml2pdf</code> (fallback)</li>
                    </ul>
                    WeasyPrint may require system libraries. See 
                    <a href="https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation" target="_blank">installation docs</a>.
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # HTML download option (always available)
        html_filename = safe_filename(filename.rsplit('.', 1)[0]) + '.html'
        st.download_button(
            label="📄 Download HTML",
            data=html_content.encode('utf-8'),
            file_name=html_filename,
            mime="text/html",
            use_container_width=True
        )
        st.caption("HTML download is always available as a fallback")


if __name__ == "__main__":
    main()
