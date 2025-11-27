"""
nb2pdf - Streamlit Web Application

A web application for converting Jupyter notebooks (.ipynb), Python scripts (.py),
and Markdown files (.md) into high-quality PDF documents.

Features:
- Upload files or provide GitHub gist URLs
- Multi-backend PDF conversion (WeasyPrint, xhtml2pdf)
- Cover page customization
- Table of contents generation
- Light/Dark theme support
- Live HTML preview
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import io
import re
from pathlib import Path

# Import our conversion modules
from nb2pdf.convert import (
    convert_file_to_html,
    try_html_to_pdf,
)
from nb2pdf.ui_helpers import (
    safe_filename,
    make_cover_html,
    make_toc_html,
    extract_headings_from_html,
    get_backend_status,
    format_file_size,
)


# ============================================================================
# Constants
# ============================================================================
MAX_PREVIEW_LENGTH = 5000  # Maximum characters to show in HTML preview

# Allowed URL hosts for fetching content (security measure)
ALLOWED_HOSTS = frozenset([
    "gist.github.com",
    "github.com",
    "raw.githubusercontent.com",
    "gist.githubusercontent.com",
    "api.github.com",
])


# ============================================================================
# Page Configuration
# ============================================================================
st.set_page_config(
    page_title="nb2pdf - Code to PDF Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# Custom CSS Styling
# ============================================================================
def load_custom_css():
    """Inject custom CSS for enhanced UI styling."""
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .app-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 0;
        border-bottom: 2px solid #4a9eff;
        margin-bottom: 2rem;
    }
    
    .app-header h1 {
        margin: 0;
        color: #1a1a1a;
        font-size: 2rem;
    }
    
    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4a9eff;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff7e6 0%, #fff3db 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    .success-card {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    /* Backend status indicators */
    .backend-available {
        color: #10b981;
        font-weight: 600;
    }
    
    .backend-unavailable {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Preview container */
    .preview-container {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    /* File upload area styling */
    .stFileUploader > div > div {
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def load_logo():
    """Load and display the app logo."""
    logo_path = Path(__file__).parent / "assets" / "logo.svg"
    if logo_path.exists():
        with open(logo_path, "r") as f:
            svg_content = f.read()
        return svg_content
    return None


# ============================================================================
# URL/Gist Handling
# ============================================================================
def is_allowed_url(url: str) -> bool:
    """
    Check if a URL is from an allowed host.
    
    Args:
        url: The URL to check
        
    Returns:
        True if the URL host is in the allowed list
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        # Ensure scheme is https and host is in allowed list
        return parsed.scheme == "https" and parsed.netloc in ALLOWED_HOSTS
    except Exception:
        return False


def fetch_from_url(url: str) -> tuple:
    """
    Fetch file content from a URL (supports GitHub gists and raw files).
    
    Only fetches from allowed GitHub domains for security.
    
    Args:
        url: The URL to fetch from
        
    Returns:
        Tuple of (content bytes, filename, error message or None)
    """
    from urllib.parse import urlparse
    
    try:
        # Validate URL format
        if not url or not url.startswith("https://"):
            return None, None, "Only HTTPS URLs are supported"
        
        parsed = urlparse(url)
        host = parsed.netloc
        
        # Security check: only allow specific GitHub domains
        if host not in ALLOWED_HOSTS:
            return None, None, (
                f"URL host '{host}' is not allowed. "
                "Only GitHub URLs (github.com, gist.github.com, raw.githubusercontent.com) are supported."
            )
        
        # Handle GitHub gist URLs
        if host == "gist.github.com":
            # Extract gist ID from the path
            gist_match = re.search(r'/([a-f0-9]+)(?:/|$)', parsed.path)
            if gist_match:
                gist_id = gist_match.group(1)
                # Fetch gist API to get files
                api_url = f"https://api.github.com/gists/{gist_id}"
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                gist_data = response.json()
                
                # Get the first file from the gist
                files = gist_data.get("files", {})
                if files:
                    first_file = list(files.values())[0]
                    content = first_file.get("content", "").encode("utf-8")
                    filename = first_file.get("filename", "document.txt")
                    return content, filename, None
                return None, None, "No files found in gist"
            return None, None, "Invalid gist URL format"
        
        # Handle GitHub blob URLs - convert to raw
        if host == "github.com" and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            # Re-validate the new URL
            parsed = urlparse(url)
            if parsed.netloc not in ALLOWED_HOSTS:
                return None, None, "Invalid GitHub URL transformation"
        
        # Fetch raw content from allowed hosts only
        # Note: This is intentional SSRF-like behavior, but mitigated by:
        # 1. ALLOWED_HOSTS allowlist restricting to GitHub domains only
        # 2. HTTPS-only requirement
        # 3. Timeout to prevent slow loris attacks
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Try to get filename from URL path
        filename = parsed.path.split("/")[-1].split("?")[0]
        if not filename or "." not in filename:
            filename = "document.txt"
            
        return response.content, filename, None
        
    except requests.RequestException as e:
        return None, None, f"Failed to fetch URL: {str(e)}"
    except Exception as e:
        return None, None, f"Error: {str(e)}"


# ============================================================================
# Main Application
# ============================================================================
def main():
    """Main application entry point."""
    load_custom_css()
    
    # ========================================================================
    # Header
    # ========================================================================
    logo_svg = load_logo()
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if logo_svg:
            st.markdown(logo_svg, unsafe_allow_html=True)
    with col2:
        st.title("📄 nb2pdf - Code to PDF Converter")
    
    st.markdown("""
    Convert your **Jupyter Notebooks** (`.ipynb`), **Python Scripts** (`.py`), 
    and **Markdown Files** (`.md`) into polished PDF documents with ease.
    """)
    
    # ========================================================================
    # Sidebar - Configuration Options
    # ========================================================================
    with st.sidebar:
        st.header("⚙️ Options")
        
        # Theme selection
        theme = st.selectbox(
            "🎨 Theme",
            options=["light", "dark"],
            index=0,
            help="Choose the color theme for the output document"
        )
        
        st.divider()
        
        # Cover page options
        st.subheader("📖 Cover Page")
        include_cover = st.checkbox("Include cover page", value=False)
        
        if include_cover:
            cover_title = st.text_input(
                "Title",
                placeholder="Document Title",
                help="Title to display on the cover page"
            )
            cover_author = st.text_input(
                "Author",
                placeholder="Author Name",
                help="Author name for the cover page"
            )
            cover_date = st.text_input(
                "Date",
                placeholder="Leave empty for today's date",
                help="Date for the cover page"
            )
        else:
            cover_title = cover_author = cover_date = None
        
        st.divider()
        
        # Table of contents
        st.subheader("📑 Table of Contents")
        include_toc = st.checkbox(
            "Include table of contents",
            value=False,
            help="Generate a table of contents from document headings"
        )
        
        st.divider()
        
        # Backend status
        st.subheader("🔧 PDF Backend Status")
        backend_status = get_backend_status()
        
        for backend, status in backend_status.items():
            if status["available"]:
                st.markdown(f"✅ **{backend}**: Available")
            else:
                st.markdown(f"❌ **{backend}**: Not available")
        
        if not any(s["available"] for s in backend_status.values()):
            st.warning(
                "⚠️ No PDF backends available. "
                "You can still download the HTML output."
            )
    
    # ========================================================================
    # Main Content Area
    # ========================================================================
    
    # File input section
    st.header("📤 Upload or Link")
    
    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 From URL"])
    
    file_content = None
    filename = None
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["ipynb", "py", "md"],
            help="Supported formats: Jupyter Notebook (.ipynb), Python Script (.py), Markdown (.md)"
        )
        
        if uploaded_file:
            file_content = uploaded_file.getvalue()
            filename = uploaded_file.name
            st.success(f"✅ Uploaded: **{filename}** ({format_file_size(len(file_content))})")
    
    with tab2:
        url_input = st.text_input(
            "Enter URL",
            placeholder="https://gist.github.com/user/... or raw file URL",
            help="Supports GitHub gists and raw file URLs"
        )
        
        if url_input:
            if st.button("🔄 Fetch File"):
                with st.spinner("Fetching file from URL..."):
                    content, fname, error = fetch_from_url(url_input)
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        file_content = content
                        filename = fname
                        st.session_state["url_content"] = content
                        st.session_state["url_filename"] = fname
                        st.success(f"✅ Fetched: **{fname}** ({format_file_size(len(content))})")
            
            # Check if we have cached content from URL
            if "url_content" in st.session_state and not uploaded_file:
                file_content = st.session_state["url_content"]
                filename = st.session_state["url_filename"]
    
    # ========================================================================
    # Conversion Section
    # ========================================================================
    if file_content and filename:
        st.divider()
        st.header("⚡ Convert")
        
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            convert_btn = st.button("🔄 Convert to PDF", type="primary", use_container_width=True)
        
        with col2:
            preview_btn = st.button("👁️ Preview HTML", use_container_width=True)
        
        if convert_btn or preview_btn:
            with st.spinner("Converting document..."):
                try:
                    # Convert to HTML
                    html_content, file_type = convert_file_to_html(
                        file_content,
                        filename,
                        theme=theme
                    )
                    
                    # Add cover page if requested
                    final_html = html_content
                    if include_cover and cover_title:
                        cover_html = make_cover_html(
                            title=cover_title,
                            author=cover_author,
                            date=cover_date if cover_date else None,
                            theme=theme
                        )
                        # Insert cover after body tag
                        if "<body" in final_html:
                            body_start = final_html.find("<body")
                            body_end = final_html.find(">", body_start) + 1
                            final_html = final_html[:body_end] + cover_html + final_html[body_end:]
                        else:
                            final_html = cover_html + final_html
                    
                    # Add table of contents if requested
                    if include_toc:
                        headings = extract_headings_from_html(html_content)
                        if headings:
                            toc_html = make_toc_html(headings, theme=theme)
                            # Insert TOC after cover (or at start if no cover)
                            if include_cover and cover_title:
                                # Find end of cover div
                                cover_pos = final_html.find("cover-page")
                                if cover_pos != -1:
                                    cover_end = final_html.find("</div>", cover_pos) + 6
                                    final_html = final_html[:cover_end] + toc_html + final_html[cover_end:]
                                else:
                                    # Fallback if cover-page not found
                                    final_html = toc_html + final_html
                            elif "<body" in final_html:
                                body_start = final_html.find("<body")
                                body_end = final_html.find(">", body_start) + 1
                                final_html = final_html[:body_end] + toc_html + final_html[body_end:]
                            else:
                                final_html = toc_html + final_html
                    
                    st.success(f"✅ Successfully converted {file_type}")
                    
                    # Show preview if requested
                    if preview_btn:
                        st.subheader("📄 HTML Preview")
                        with st.expander("View HTML Source", expanded=False):
                            preview_html = final_html[:MAX_PREVIEW_LENGTH]
                            if len(final_html) > MAX_PREVIEW_LENGTH:
                                preview_html += "..."
                            st.code(preview_html, language="html")
                        
                        st.markdown("**Rendered Preview:**")
                        components.html(final_html, height=600, scrolling=True)
                    
                    # Convert to PDF if requested
                    if convert_btn:
                        pdf_bytes, backend, error = try_html_to_pdf(final_html)
                        
                        if pdf_bytes:
                            st.success(f"✅ PDF generated using **{backend}** backend")
                            
                            # Generate output filename
                            output_filename = safe_filename(filename.rsplit(".", 1)[0]) + ".pdf"
                            
                            # Download buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=pdf_bytes,
                                    file_name=output_filename,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            with col2:
                                st.download_button(
                                    label="📄 Download HTML",
                                    data=final_html,
                                    file_name=output_filename.replace(".pdf", ".html"),
                                    mime="text/html",
                                    use_container_width=True
                                )
                            
                            st.info(f"📊 PDF size: {format_file_size(len(pdf_bytes))}")
                        else:
                            st.warning(f"⚠️ {error}")
                            st.markdown("""
                            <div class="warning-card">
                            <h4>💡 PDF Backend Not Available</h4>
                            <p>No PDF conversion backend is currently available. 
                            You can still download the HTML file and convert it manually using:</p>
                            <ul>
                                <li>Open the HTML in a web browser and print to PDF</li>
                                <li>Use an online HTML to PDF converter</li>
                                <li>Install WeasyPrint or xhtml2pdf locally</li>
                            </ul>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Offer HTML download
                            html_filename = safe_filename(filename.rsplit(".", 1)[0]) + ".html"
                            st.download_button(
                                label="📄 Download HTML Instead",
                                data=final_html,
                                file_name=html_filename,
                                mime="text/html",
                                use_container_width=True
                            )
                
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.exception(e)
    
    # ========================================================================
    # Footer
    # ========================================================================
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem 0;">
        <p><strong>nb2pdf</strong> - Convert notebooks and scripts to PDF with ease</p>
        <p style="font-size: 0.85rem;">
            Supports: Jupyter Notebooks (.ipynb) • Python Scripts (.py) • Markdown (.md)
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
