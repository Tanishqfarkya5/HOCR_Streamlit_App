import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
import io
import tempfile
import os

# --- Page Config ---
st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪷 Hindi OCR App using EasyOCR")
st.caption("Extract Hindi or English text from images and download it as PDF or Word file.")

# --- Load Hindi Font ---
font_path = "NotoSansDevanagari-Regular.ttf"
if not os.path.exists(font_path):
    st.info("📥 Downloading Hindi font...")
    import requests
    url = "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf"
    r = requests.get(url)
    with open(font_path, "wb") as f:
        f.write(r.content)
pdfmetrics.registerFont(TTFont("HindiFont", font_path))

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    st.info("🔍 Extracting text, please wait...")

    # OCR Processing
    reader = easyocr.Reader(["hi", "en"])
    result = reader.readtext(np.array(image), detail=0)
    extracted_text = "\n".join(result)

    st.subheader("📝 Extracted Text:")
    st.text_area("", extracted_text, height=250)

    # --- Generate PDF ---
    def generate_pdf(text):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        text_obj = pdf.beginText(50, height - 50)
        text_obj.setFont("HindiFont", 14)
        line_height = 18
        for line in text.split("\n"):
            text_obj.textLine(line)
        pdf.drawText(text_obj)
        pdf.save()
        buffer.seek(0)
        return buffer

    # --- Generate DOCX ---
    def generate_docx(text):
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc.save(tmp.name)
        with open(tmp.name, "rb") as f:
            return io.BytesIO(f.read())

    # --- Download Buttons ---
    st.download_button("📄 Download as PDF", generate_pdf(extracted_text),
                       file_name="hindi_text.pdf", mime="application/pdf")

    st.download_button("📝 Download as Word", generate_docx(extracted_text),
                       file_name="hindi_text.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
