import streamlit as st
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
import requests
import os

# ======================
# APP CONFIG
# ======================
st.set_page_config(page_title="Hindi OCR App using PaddleOCR", layout="centered")
st.title("🪶 Hindi OCR App using PaddleOCR")

# ======================
# DOWNLOAD HINDI FONT
# ======================
FONT_PATH = "NotoSansDevanagari-Regular.ttf"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf"

if not os.path.exists(FONT_PATH):
    with st.spinner("Downloading Hindi font..."):
        try:
            r = requests.get(FONT_URL)
            if r.status_code == 200:
                with open(FONT_PATH, "wb") as f:
                    f.write(r.content)
                st.success("✅ Hindi font downloaded successfully!")
            else:
                st.warning("⚠️ Could not download Hindi font. PDF may not render properly.")
        except Exception as e:
            st.warning(f"⚠️ Font download failed: {e}")

# Register Hindi font for PDF
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("NotoHindi", FONT_PATH))
else:
    st.warning("⚠️ Hindi font not found. Using default font (may show boxes in PDF).")

# ======================
# LOAD OCR MODEL
# ======================
@st.cache_resource
def load_ocr():
    return PaddleOCR(lang='hi', use_angle_cls=True)

ocr = load_ocr()

# ======================
# UPLOAD SECTION
# ======================
st.subheader("📤 Upload an image (JPG, PNG, JPEG)")
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Hindi Text"):
        with st.spinner("Extracting text using PaddleOCR..."):
            result = ocr.ocr(np.array(image), cls=True)
            extracted_text = ""
            for line in result[0]:
                extracted_text += line[1][0] + " "

        # ======================
        # DISPLAY RESULTS
        # ======================
        st.success("✅ Text extraction completed!")
        st.text_area("📜 Extracted Hindi Text", extracted_text, height=250)

        # ======================
        # DOWNLOAD WORD DOC
        # ======================
        def convert_to_docx(text):
            doc = Document()
            doc.add_paragraph(text)
            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)
            return buf

        # ======================
        # DOWNLOAD PDF
        # ======================
        def convert_to_pdf(text):
            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            width, height = A4
            text_obj = c.beginText(50, height - 50)
            text_obj.setFont("NotoHindi", 14)
            for line in text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)
            c.save()
            buf.seek(0)
            return buf

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📘 Download as Word (.docx)",
                data=convert_to_docx(extracted_text),
                file_name="Hindi_OCR_Output.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        with col2:
            st.download_button(
                "📄 Download as PDF",
                data=convert_to_pdf(extracted_text),
                file_name="Hindi_OCR_Output.pdf",
                mime="application/pdf"
            )

# ======================
# FOOTER
# ======================
st.markdown("---")
st.markdown("🔠 Developed by **Tanishq Farkya** — Hindi OCR powered by PaddleOCR")
