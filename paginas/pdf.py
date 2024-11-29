import streamlit as st
import io
from docx2html import convert
from weasyprint import HTML
import base64
import imghdr

def docx_to_pdf(docx_bytes):
    # Convert DOCX to HTML with embedded images
    html_content = convert(docx_bytes)
    # Convert HTML to PDF
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def txt_to_pdf(txt_bytes):
    # Read text and create HTML content
    text = txt_bytes.decode("utf-8")
    html_content = f"<html><body><pre>{text}</pre></body></html>"
    # Convert HTML to PDF
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def image_to_pdf(image_bytes):
    # Detect image type
    img_type = imghdr.what(None, h=image_bytes)
    if img_type not in ['jpeg', 'png']:
        raise ValueError("Unsupported image type.")
    # Read image and embed as base64 in HTML
    img_data = base64.b64encode(image_bytes).decode("utf-8")
    # Create HTML content with correct MIME type
    mime_type = f"image/{img_type}"
    html_content = f"<html><body><img src='data:{mime_type};base64,{img_data}'></body></html>"
    # Convert HTML to PDF
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

st.title("📄 Universal PDF Converter")
uploaded_file = st.file_uploader(
    "Upload a file to convert to PDF:",
    type=["docx", "txt", "jpg", "png"],
    help="Supports DOCX, TXT, JPG, and PNG files."
)

if uploaded_file is not None:
    st.info("File uploaded successfully! Generating PDF...")
    try:
        with st.spinner("Converting..."):
            file_type = uploaded_file.type
            if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                pdf_buffer = docx_to_pdf(uploaded_file.read())
            elif file_type == "text/plain":
                pdf_buffer = txt_to_pdf(uploaded_file.read())
            elif file_type in ["image/jpeg", "image/png"]:
                pdf_buffer = image_to_pdf(uploaded_file.read())
            else:
                st.error("Unsupported file type.")
                st.stop()
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.pdf",
            mime="application/pdf"
        )
        st.success("PDF generated successfully! Click above to download.")
    except Exception as e:
        st.error(f"An error occurred during conversion: {str(e)}")