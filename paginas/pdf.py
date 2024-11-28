import streamlit as st
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
import io

def docx_to_pdf(docx_file):
    doc = Document(docx_file)
    pdf_buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles['Normal']
    elements = [Paragraph(p.text.strip(), style) for p in doc.paragraphs if p.text.strip()]
    doc_pdf.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

def txt_to_pdf(txt_file):
    pdf_buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles['Normal']
    content = txt_file.read().decode("utf-8").splitlines()
    elements = [Paragraph(line.strip(), style) for line in content if line.strip()]
    doc_pdf.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

def image_to_pdf(image_file):
    pdf_buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    img = Image(image_file, width=400, height=300)  # Ajuste as dimensões conforme necessário
    doc_pdf.build([img])
    pdf_buffer.seek(0)
    return pdf_buffer

st.title("📄 Conversor Universal para PDF")

uploaded_file = st.file_uploader(
    "Faça upload de um arquivo para converter em PDF:",
    type=["docx", "txt", "jpg", "png"],
    help="Suporte para arquivos DOCX, TXT, JPG e PNG."
)

if uploaded_file is not None:
    st.info("Arquivo carregado com sucesso! Gerando PDF...")

    try:
        with st.spinner("Convertendo..."):
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                pdf_buffer = docx_to_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                pdf_buffer = txt_to_pdf(uploaded_file)
            elif uploaded_file.type in ["image/jpeg", "image/png"]:
                pdf_buffer = image_to_pdf(uploaded_file)
            else:
                st.error("Tipo de arquivo não suportado.")
                st.stop()

        st.download_button(
            label="📥 Baixar PDF",
            data=pdf_buffer,
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.pdf",
            mime="application/pdf"
        )
        st.success("PDF gerado com sucesso! Clique no botão acima para baixá-lo.")
    except Exception as e:
        st.error(f"Ocorreu um erro durante a conversão: {str(e)}")
