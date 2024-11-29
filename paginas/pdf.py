import streamlit as st
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
import io
import os
from PIL import Image as PILImage

def docx_to_pdf(docx_file):
    doc = Document(docx_file)
    pdf_buffer = io.BytesIO()

    # Configurações de estilo mais detalhadas
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=black,
        leading=14
    )

    # Cria um novo canvas PDF
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Posição inicial de escrita
    y_position = height - 1 * inch
    margin = 1 * inch

    try:
        for paragraph in doc.paragraphs:
            # Lidar com parágrafos em branco
            if paragraph.text.strip():
                # Renderiza texto
                p = Paragraph(paragraph.text, custom_style)
                w, h = p.wrap(width - 2*margin, height)
                p.drawOn(c, margin, y_position - h)
                y_position -= h

            # Lidar com imagens incorporadas
            for run in paragraph.runs:
                if run.element.find('.//{http://schemas.openxmlformats.org/drawingml/2006/picture}pic') is not None:
                    for image in run.element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/picture}blipFill'):
                        # Extrai e salva imagens temporariamente
                        image_part = run.element.find('.//{http://schemas.openxmlformats.org/officeDocument/2006/relationships}imagedata')
                        if image_part is not None:
                            image_id = image_part.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                            image_part = doc.part.related_parts.get(image_id)

                            if image_part:
                                # Salva imagem temporária
                                temp_image_path = f"temp_image_{image_id}.png"
                                with open(temp_image_path, 'wb') as f:
                                    f.write(image_part._blob)

                                # Adiciona imagem ao PDF
                                img = PILImage.open(temp_image_path)
                                img_width, img_height = img.size

                                # Ajusta o tamanho da imagem para caber na página
                                max_width = width - 2*margin
                                max_height = height - 2*margin

                                if img_width > max_width:
                                    ratio = max_width / img_width
                                    img_width = max_width
                                    img_height *= ratio

                                if img_height > max_height:
                                    ratio = max_height / img_height
                                    img_height = max_height
                                    img_width *= ratio

                                c.drawImage(temp_image_path, margin, y_position - img_height, 
                                            width=img_width, height=img_height)
                                y_position -= img_height + 0.25*inch

                                # Remove imagem temporária
                                os.remove(temp_image_path)

            # Adiciona um pequeno espaço entre parágrafos
            y_position -= 0.25 * inch

            # Verifica se precisa de uma nova página
            if y_position <= margin:
                c.showPage()
                y_position = height - margin

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        st.error(f"Erro ao converter DOCX: {str(e)}")
        return None

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

    # Abre a imagem com Pillow para processamento de alta qualidade
    img = PILImage.open(image_file)

    # Cria o canvas PDF
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Calcula dimensões da imagem mantendo a proporção
    img_width, img_height = img.size
    max_width = width - 2*inch
    max_height = height - 2*inch

    # Ajusta o tamanho mantendo a proporção
    ratio = min(max_width/img_width, max_height/img_height)
    new_width = img_width * ratio
    new_height = img_height * ratio

    # Centraliza a imagem
    x_centered = (width - new_width) / 2
    y_centered = (height - new_height) / 2

    # Converte para alta qualidade
    img_path = "temp_high_quality_image.png"
    img.save(img_path, optimize=True, quality=95)

    # Desenha a imagem no PDF
    c.drawImage(img_path, x_centered, y_centered, width=new_width, height=new_height)

    # Fecha e salva o PDF
    c.showPage()
    c.save()

    # Remove imagem temporária
    os.remove(img_path)

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

        if pdf_buffer:
            st.download_button(
                label="📥 Baixar PDF",
                data=pdf_buffer,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.pdf",
                mime="application/pdf"
            )
            st.success("PDF gerado com sucesso! Clique no botão acima para baixá-lo.")
    except Exception as e:
        st.error(f"Ocorreu um erro durante a conversão: {str(e)}")