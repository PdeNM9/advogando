import streamlit as st
from docx import Document
from reportlab.pdfgen import canvas
import io

def docx_to_pdf(docx_file):
    # Read the DOCX file
    doc = Document(docx_file)

    # Create a PDF buffer
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    # Extract text and write to PDF
    y_position = 800  # Start from top of page
    for paragraph in doc.paragraphs:
        if y_position <= 50:  # Check if we need a new page
            pdf.showPage()
            y_position = 800

        text = paragraph.text
        if text.strip():  # Only process non-empty paragraphs
            pdf.drawString(50, y_position, text)
            y_position -= 20  # Move down for next line

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer


st.title("📄 Conversor de DOC para PDF")
st.write("Upload um arquivo DOCX e converta para PDF")

uploaded_file = st.file_uploader(
        "Escolha o arquivo DOCX",
        type=["docx"],
        help="Upload a Microsoft Word document (.docx)"
    )

if uploaded_file is not None:
    st.info("File uploaded successfully!")

    if st.button("Convert to PDF"):
        try:
            with st.spinner("Converting..."):
                    # Convert the file
                    pdf_buffer = docx_to_pdf(uploaded_file)

                    # Create download button
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_buffer,
                        file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.pdf",
                        mime="application/pdf"
                    )
            st.success("Conversion completed! Click the button above to download your PDF.")

        except Exception as e:
            st.error(f"An error occurred during conversion: {str(e)}")
            st.write("Please make sure you've uploaded a valid DOCX file and try again.")
