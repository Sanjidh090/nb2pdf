import streamlit as st
import nbformat
from nbconvert import HTMLExporter
from weasyprint import HTML
import io

# Page Configuration
st.set_page_config(
    page_title="Code to PDF Converter",
    page_icon="📄",
    layout="centered"
)

def convert_py_to_notebook(py_content):
    """Converts Python script content to a Notebook Node."""
    nb = nbformat.v4.new_notebook()
    code_cell = nbformat.v4.new_code_cell(py_content)
    nb.cells.append(code_cell)
    return nb

def generate_pdf(uploaded_file):
    """
    Takes a Streamlit UploadedFile, converts it to HTML, 
    and then renders it as a PDF byte stream.
    """
    try:
        # 1. Read the file content
        file_content = uploaded_file.getvalue().decode("utf-8")
        filename = uploaded_file.name
        
        nb = None
        
        # 2. Convert raw text to Notebook Node
        if filename.endswith('.py'):
            nb = convert_py_to_notebook(file_content)
            
        elif filename.endswith('.ipynb'):
            # nbformat expects a file-like object for reading
            nb = nbformat.read(io.StringIO(file_content), as_version=4)
        
        if not nb:
            return None, "Could not process file format."

        # 3. Export Notebook to HTML
        html_exporter = HTMLExporter()
        html_exporter.theme = 'light' # 'dark' is also an option
        html_exporter.exclude_input_prompt = True
        html_exporter.exclude_output_prompt = True
        
        (body, resources) = html_exporter.from_notebook_node(nb)

        # 4. Render HTML to PDF Bytes
        # We write to a variable instead of a file
        pdf_bytes = HTML(string=body).write_pdf()
        
        return pdf_bytes, None

    except Exception as e:
        return None, str(e)

# --- UI Layout ---
st.title("📄 Code to PDF Converter")
st.markdown("""
Upload your **Jupyter Notebook** (`.ipynb`) or **Python Script** (`.py`) 
to convert it into a clean PDF document.
""")

uploaded_file = st.file_uploader("Choose a file", type=['ipynb', 'py'])

if uploaded_file is not None:
    st.info(f"File **{uploaded_file.name}** uploaded successfully.")
    
    # Create a button to trigger conversion
    if st.button("Convert to PDF"):
        with st.spinner("Converting... This may take a moment."):
            pdf_data, error = generate_pdf(uploaded_file)
            
            if error:
                st.error(f"An error occurred: {error}")
            else:
                st.success("Conversion successful!")
                
                # Create the download filename
                output_filename = uploaded_file.name.rsplit('.', 1)[0] + ".pdf"
                
                # Show download button
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_data,
                    file_name=output_filename,
                    mime="application/pdf"
                )
