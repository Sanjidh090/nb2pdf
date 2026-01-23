# nb2pdf 📄

A Streamlit web application that converts Jupyter notebooks (`.ipynb`), Python scripts (`.py`), and Markdown files (`.md`) into high-quality PDF documents.

![nb2pdf Logo](assets/logo.svg)

🚀 **Try it now:** 
**[Launch nb2pdf](https://nb2pdf.streamlit.app/)**
## ✨ Features

- **Multiple Input Formats**: Support for Jupyter Notebooks, Python scripts, and Markdown files
- **GitHub Gist Support**: Fetch files directly from GitHub Gist URLs
- **Cover Page**: Add a customizable cover page with title, author, and date
- **Table of Contents**: Automatically generate a table of contents from headings
- **Theme Selection**: Choose between light and dark themes
- **Page Size Options**: Support for A4, Letter, and Legal page sizes
- **Multi-Backend PDF Generation**: Uses WeasyPrint with xhtml2pdf as fallback
- **Live Preview**: Preview the HTML output before generating PDF
- **Always-Available HTML Download**: Download HTML even if PDF backends are unavailable

## Screenshots
<img width="480" height="260" alt="image" src="https://github.com/user-attachments/assets/a38136cc-ab92-45d4-a0cc-c6f056a9abda" />
<img width="450" height="240" alt="image" src="https://github.com/user-attachments/assets/590e25c1-f3f9-4452-a663-e3d3f8e1c960" />
<img width="934" height="380" alt="image" src="https://github.com/user-attachments/assets/c50c0d49-c616-461d-8838-bbc181c79571" />


## 🌐 Get started

Click **Try nb2pdf now** above, upload your file, and download your PDF.  
**[Launch nb2pdf](https://nb2pdf.streamlit.app/)**
That’s it — no setup, no installs.
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

3. **Install system dependencies for WeasyPrint** (optional but recommended):
   
   On Ubuntu/Debian:
   ```bash
   sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libglib2.0-0
   ```
   
   On macOS:
   ```bash
   brew install pango cairo
   ```
   
   On Windows:
   - WeasyPrint installation may require GTK. See [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

4. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser** at `http://localhost:8501`

### Deploy on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your forked repository
5. Set the main file path to `streamlit_app.py`
6. Click "Deploy"

**Note**: For Streamlit Cloud deployment, you may need to create a `packages.txt` file with system dependencies:

```
libpango-1.0-0
libpangoft2-1.0-0
libglib2.0-0
libcairo2
```

## 📖 Usage

### Upload a File

1. Use the **"Upload File"** tab
2. Drag and drop or browse to select your file
3. Configure options in the sidebar:
   - Choose theme (light/dark)
   - Set page size
   - Add cover page (optional)
   - Include table of contents (optional)
4. Click **"Generate PDF"** to create the PDF
5. Download the PDF or HTML file

### Fetch from URL

1. Use the **"From URL"** tab
2. Enter a GitHub Gist URL or direct file URL:
   - `https://gist.github.com/username/gist_id`
   - `https://raw.githubusercontent.com/user/repo/branch/file.ipynb`
3. Click **"Fetch File"**
4. Follow the same conversion steps as above

## ⚙️ Configuration Options

| Option | Description |
|--------|-------------|
| **Theme** | Light or Dark mode for the output |
| **Page Size** | A4, Letter, or Legal |
| **Cover Page** | Add a title page with title, author, and date |
| **Table of Contents** | Auto-generate TOC from headings |
| **Pygments Highlighting** | Use Pygments for Python syntax highlighting |

## 🔧 PDF Backend Configuration

nb2pdf supports multiple PDF generation backends with automatic fallback:

1. **WeasyPrint** (recommended): High-quality PDF output with CSS support
2. **xhtml2pdf**: Pure Python fallback, no system dependencies required

### Installing PDF Backends

**WeasyPrint** (recommended):
```bash
pip install weasyprint
```

**xhtml2pdf** (fallback):
```bash
pip install xhtml2pdf
```

If no PDF backends are available, the app will still allow you to download the HTML file.

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

## 🐛 Known Limitations

- **LaTeX Rendering**: Complex LaTeX equations may not render perfectly in PDF
- **Large Files**: Very large notebooks may take longer to process
- **System Dependencies**: WeasyPrint requires system libraries (cairo, pango)
- **External Images**: Images referenced by URL may not appear in PDF if inaccessible

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - The amazing framework for building data apps
- [nbconvert](https://nbconvert.readthedocs.io/) - For notebook conversion
- [WeasyPrint](https://weasyprint.org/) - For PDF generation
- [Pygments](https://pygments.org/) - For syntax highlighting

---

Made with ❤️ by the nb2pdf contributors
