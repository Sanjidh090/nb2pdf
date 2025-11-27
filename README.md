# nb2pdf - Code to PDF Converter

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

A Streamlit-based web application that converts **Jupyter Notebooks** (`.ipynb`), **Python Scripts** (`.py`), and **Markdown Files** (`.md`) into high-quality PDF documents.

![nb2pdf Screenshot](assets/logo.svg)

## ✨ Features

- **Multi-format Support**: Convert Jupyter notebooks, Python scripts, and Markdown files
- **Multiple PDF Backends**: Uses WeasyPrint (high quality) with xhtml2pdf fallback
- **Cover Page**: Add a customizable cover page with title, author, and date
- **Table of Contents**: Auto-generate TOC from document headings
- **Theme Support**: Light and dark themes for output documents
- **Live Preview**: Preview HTML output before conversion
- **URL/Gist Support**: Fetch files directly from GitHub gists or raw URLs
- **Graceful Fallbacks**: If PDF backends aren't available, download HTML instead

## 🚀 Quick Start

### Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sanjidh090/nb2pdf.git
   cd nb2pdf
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies** (for WeasyPrint):
   
   **Ubuntu/Debian**:
   ```bash
   sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libglib2.0-0 libcairo2
   ```
   
   **macOS**:
   ```bash
   brew install pango cairo
   ```
   
   **Windows**:
   Follow the [WeasyPrint Windows installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)

4. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

5. Open your browser to `http://localhost:8501`

### Deploy to Streamlit Cloud

1. Fork this repository to your GitHub account

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Connect your GitHub account and select the repository

4. Set the main file path to `streamlit_app.py`

5. Add `packages.txt` for system dependencies (already included):
   ```
   libpango-1.0-0
   libpangoft2-1.0-0
   libglib2.0-0
   libcairo2
   ```

6. Click **Deploy**!

## 📖 Usage

### Upload a File

1. Click the **Upload File** tab
2. Drag and drop or browse for a `.ipynb`, `.py`, or `.md` file
3. Configure options in the sidebar (theme, cover page, TOC)
4. Click **Convert to PDF** or **Preview HTML**

### Fetch from URL

1. Click the **From URL** tab
2. Paste a GitHub gist URL or raw file URL
3. Click **Fetch File**
4. Convert as usual

### Customization Options

- **Theme**: Choose between light and dark output themes
- **Cover Page**: Add a title page with custom title, author, and date
- **Table of Contents**: Auto-generate from document headings

## 🔧 PDF Backends

The application supports multiple PDF conversion backends:

### WeasyPrint (Recommended)
- High-quality PDF output
- Good CSS support
- Requires system libraries (pango, cairo)
- Best for complex layouts

### xhtml2pdf (Fallback)
- Pure Python implementation
- No system dependencies
- Works on most platforms
- May have limited CSS support

### HTML Download (Last Resort)
If no PDF backend is available, you can:
- Download the HTML file
- Open in a browser and print to PDF
- Use an online converter

## 📁 Project Structure

```
nb2pdf/
├── streamlit_app.py      # Main Streamlit application
├── nb2pdf/
│   ├── __init__.py       # Package initialization
│   ├── convert.py        # Conversion utilities
│   └── ui_helpers.py     # UI helper functions
├── assets/
│   └── logo.svg          # Application logo
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── requirements.txt      # Python dependencies
├── packages.txt          # System dependencies (Streamlit Cloud)
└── README.md             # This file
```

## ⚠️ Known Limitations

1. **LaTeX Support**: Complex LaTeX equations may not render perfectly in PDF
2. **Large Files**: Very large notebooks may take longer to convert
3. **Images**: External images in notebooks may not be included if they require authentication
4. **Code Output**: Some rich outputs (interactive widgets, complex HTML) may not convert well

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) - The amazing framework for building data apps
- [nbconvert](https://nbconvert.readthedocs.io) - Jupyter notebook conversion
- [WeasyPrint](https://weasyprint.org) - High-quality PDF generation
- [xhtml2pdf](https://xhtml2pdf.readthedocs.io) - Pure Python PDF conversion
