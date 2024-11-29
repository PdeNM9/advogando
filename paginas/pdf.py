import io
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# Function to extract text and images from DOCX
def extract_docx_content(docx_file):
    doc = Document(docx_file)
    content = []
    # Extract images and save them temporarily
    for rel in doc.part.relationships:
        if "image" in rel.type:
            image = rel._target
            image_bytes = image.blob
            image_path = f"temp_image_{len(content)}.png"
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            content.append(('image', image_path))
    # Extract text from paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content.append(('text', text))
    return content

# Function to create PDF from content
def create_pdf(content, pdf_path):
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for item in content:
        if item[0] == 'text':
            p = Paragraph(item[1], styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))
        elif item[0] == 'image':
            img = Image(item[1])
            # Scale image to fit within the page width
            img_width, img_height = img._width, img._height
            if img_width > letter[0]:
                ratio = letter[0] / img_width
                img._width = letter[0]
                img._height = img_height * ratio
            story.append(img)
            story.append(Spacer(1, 12))
    pdf.build(story)
    # Clean up temporary image files
    for item in content:
        if item[0] == 'image':
            os.remove(item[1])

# Main function to handle file upload and conversion
def main():
    # Assume 'uploaded_file' is the DOCX file from Streamlit file uploader
    # For demonstration, use a sample DOCX file
    uploaded_file = "sample.docx"
    content = extract_docx_content(uploaded_file)
    pdf_buffer = io.BytesIO()
    create_pdf(content, pdf_buffer)
    # In Streamlit, use pdf_buffer to provide the PDF for download
    # st.download_button(...)

if __name__ == "__main__":
    main()