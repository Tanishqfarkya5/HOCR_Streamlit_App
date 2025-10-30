import streamlit as st
import easyocr
import pytesseract
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re

st.set_page_config(page_title="Hindi OCR Extractor", page_icon="🪄")

st.title("🪄 Advanced OCR for Hindi Text")
st.write("Upload handwritten or printed Hindi text image. You can choose EasyOCR or Tesseract engine.")

uploaded_file = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"])

def clean_text(text):
    text = re.sub(r'[|¦]+', '।', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    use_tesseract = st.checkbox("Use Tesseract (Better for Hindi)", value=True)

    if st.button("🔍 Extract Text"):
        with st.spinner("Extracting text..."):
            if use_tesseract:
                img_cv = np.array(image.convert('RGB'))
                gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
                text = pytesseract.image_to_string(gray, lang='hin', config="--psm 6")
            else:
                reader = easyocr.Reader(['hi', 'en'], verbose=False)
                gray = cv2.cvtColor(np.array(image.convert('RGB')), cv2.COLOR_RGB2GRAY)
                text = "\n".join(reader.readtext(gray, detail=0, paragraph=True))

        text = clean_text(text)
        st.success("✅ Text extracted successfully!")
        st.text_area("Extracted Text", text, height=200)

        # Download buttons
        def create_docx(text):
            buf = BytesIO()
            doc = Document()
            doc.add_paragraph(text)
            doc.save(buf)
            buf.seek(0)
            return buf

        def create_pdf(text):
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            t = c.beginText(40, 800)
            t.setFont("Helvetica", 12)
            for line in text.split("\n"):
                t.textLine(line)
            c.drawText(t)
            c.save()
            buf.seek(0)
            return buf

        col1, col2 = st.columns(2)
        col1.download_button("📘 Download Word", create_docx(text), "hindi_text.docx")
        col2.download_button("📄 Download PDF", create_pdf(text), "hindi_text.pdf")
