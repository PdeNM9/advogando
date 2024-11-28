import streamlit as st
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

def docx_to_pdf(docx_file):
    # Lê o arquivo DOCX
    doc = Document(docx_file)

    # Cria um buffer para o PDF
    pdf_buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Obtém o estilo padrão para o texto
    styles = getSampleStyleSheet()
    style = styles['Normal']

    # Lista para armazenar os elementos do PDF
    elements = []

    # Adiciona cada parágrafo do DOCX ao PDF
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:  # Processa apenas parágrafos não vazios
            para = Paragraph(text, style)
            elements.append(para)

    # Constrói o PDF
    doc_pdf.build(elements)

    # Retorna o buffer do PDF
    pdf_buffer.seek(0)
    return pdf_buffer

st.title("📄 Conversor de DOC para PDF")

uploaded_file = st.file_uploader(
    "Faça upload de um arquivo DOCX para gerar automaticamente um PDF:",
    type=["docx"],
    help="Faça upload de um documento do Microsoft Word (.docx)"
)

if uploaded_file is not None:
    st.info("Arquivo carregado com sucesso! Gerando PDF...")

    try:
        with st.spinner("Convertendo..."):
            # Converte o arquivo
            pdf_buffer = docx_to_pdf(uploaded_file)

        # Exibe o botão de download assim que o PDF é gerado
        st.download_button(
            label="📥 Baixar PDF",
            data=pdf_buffer,
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.pdf",
            mime="application/pdf"
        )
        st.success("PDF gerado com sucesso! Clique no botão acima para baixá-lo.")
    except Exception as e:
        st.error(f"Ocorreu um erro durante a conversão: {str(e)}")
        st.write("Certifique-se de ter enviado um arquivo DOCX válido e tente novamente.")
