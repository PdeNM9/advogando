import streamlit as st
import io
import os
from docx2pdf import convert
from PIL import Image

def docx_to_pdf(docx_file):
    try:
        # Salva o arquivo DOCX temporariamente
        with open("temp_document.docx", "wb") as temp_docx:
            temp_docx.write(docx_file.getbuffer())

        # Cria um buffer de saída para o PDF
        pdf_buffer = io.BytesIO()

        # Converte o documento usando docx2pdf
        convert("temp_document.docx", "temp_document.pdf")

        # Lê o PDF gerado
        with open("temp_document.pdf", "rb") as pdf_file:
            pdf_buffer.write(pdf_file.read())

        # Limpa arquivos temporários
        os.remove("temp_document.docx")
        os.remove("temp_document.pdf")

        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        st.error(f"Erro na conversão do DOCX: {str(e)}")
        return None

def txt_to_pdf(txt_file):
    pdf_buffer = io.BytesIO()
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch

    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Configurações de texto
    c.setFont("Helvetica", 12)

    # Posição inicial
    text = txt_file.read().decode("utf-8")
    lines = text.split('\n')

    y = height - inch  # Começa um pouco abaixo do topo
    for line in lines:
        c.drawString(inch, y, line)
        y -= 14  # Espaçamento entre linhas

        # Adiciona nova página se necessário
        if y <= inch:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - inch

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def image_to_pdf(image_file):
    pdf_buffer = io.BytesIO()
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch

    # Abre a imagem
    img = Image.open(image_file)

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

    # Salva imagem temporária
    temp_path = "temp_image.png"
    img.save(temp_path)

    # Desenha a imagem
    c.drawImage(temp_path, x_centered, y_centered, width=new_width, height=new_height)

    # Fecha o PDF
    c.showPage()
    c.save()

    # Remove imagem temporária
    os.remove(temp_path)

    pdf_buffer.seek(0)
    return pdf_buffer

# Configuração do Streamlit
st.title("📄 Conversor Universal para PDF")

# Adiciona bibliotecas necessárias
try:
    import docx2pdf
except ImportError:
    st.warning("Instalando bibliotecas necessárias...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'docx2pdf'])
    import docx2pdf

# Upload de arquivo
uploaded_file = st.file_uploader(
    "Faça upload de um arquivo para converter em PDF:",
    type=["docx", "txt", "jpg", "png"],
    help="Suporte para arquivos DOCX, TXT, JPG e PNG."
)

# Processamento do arquivo
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