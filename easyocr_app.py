import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import requests

# ----------------------------------------------------------
# 🪶 APP SETUP
# ----------------------------------------------------------
st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪶 Hindi OCR App using EasyOCR")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['hi'], gpu=False)

reader = load_reader()

# ----------------------------------------------------------
# 🪶 FONT SETUP (auto-download from multiple mirrors)
# ----------------------------------------------------------
FONT_PATH = "NotoSansDevanagari-Regular.ttf"

FONT_URLS = [
    # Official Google Fonts raw link
    "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf",
    # Alternative CDN mirror
    "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",
    # Backup Google Drive mirror (for safety)
    "https://drive.google.com/uc?id=1Yniw4aVtK7bUak9XkZahgR7oWjF4gZnK"
]

def download_font():
    for url in FONT_URLS:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 100000:  # sanity check: ~150 KB+
                with open(FONT_PATH, "wb") as f:
                    f.write(r.content)
                return True
        except Exception:
            continue
    return False

if not os.path.exists(FONT_PATH):
    with st.spinner("Downloading Hindi font..."):
        success = download_font()
        if success:
            st.success("✅ Hindi font downloaded successfully!")
        else:
            st.warning("⚠️ Could not download Hindi font. PDF may not render properly.")

# Register the Hindi font for PDF rendering
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("NotoHindi", FONT_PATH))
else:
    st.warning("⚠️ Hindi font not found. Using default font (may show boxes in PDF).")

# ----------------------------------------------------------
# 🪶 FILE UPLOAD SECTION
# ----------------------------------------------------------
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((800, 800))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # ------------------------------------------------------
    # 🪶 TEXT EXTRACTION
    # ------------------------------------------------------
    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            image_np = np.array(image)
            result = reader.readtext(image_np, detail=0, paragraph=True)

        extracted_text = "\n".join(result)
        st.subheader("📝 Extracted Text")
        st.text_area("", extracted_text, height=200)

        # ------------------------------------------------------
        # 🪶 DOWNLOAD AS TXT
        # ------------------------------------------------------
        txt_bytes = extracted_text.encode("utf-8")
        st.download_button("📄 Download TXT", data=txt_bytes,
                           file_name="output.txt", mime="text/plain")

        # ------------------------------------------------------
        # 🪶 DOWNLOAD AS DOCX
        # ------------------------------------------------------
        doc = Document()
        doc.add_paragraph(extracted_text)
        docx_buf = BytesIO()
        doc.save(docx_buf)
        docx_buf.seek(0)
        st.download_button("📘 Download DOCX", data=docx_buf,
                           file_name="output.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # ------------------------------------------------------
        # 🪶 DOWNLOAD AS PDF (with Hindi font)
        # ------------------------------------------------------
        pdf_buf = BytesIO()
        c = canvas.Canvas(pdf_buf, pagesize=A4)
        width, height = A4
        y = height - 70

        if os.path.exists(FONT_PATH):
            c.setFont("NotoHindi", 14)
        else:
            c.setFont("Helvetica", 14)

        for line in extracted_text.split("\n"):
            if y < 50:
                c.showPage()
                if os.path.exists(FONT_PATH):
                    c.setFont("NotoHindi", 14)
                else:
                    c.setFont("Helvetica", 14)
                y = height - 70
            c.drawString(50, y, line)
            y -= 25

        c.save()
        pdf_buf.seek(0)
        st.download_button("🧾 Download PDF", data=pdf_buf,
                           file_name="output.pdf", mime="application/pdf")

else:
    st.info("📤 Upload an image to start Hindi OCR.")
