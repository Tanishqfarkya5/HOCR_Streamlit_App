import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

# ==========================
# APP CONFIG
# ==========================
st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪶 Hindi OCR App using EasyOCR")

# ==========================
# FONT SETUP (for Hindi text in PDF)
# ==========================
FONT_PATH = "NotoSansDevanagari-Regular.ttf"

if not os.path.exists(FONT_PATH):
    st.warning("Please upload or include 'NotoSansDevanagari-Regular.ttf' in your app folder for Hindi text support in PDF.")
else:
    pdfmetrics.registerFont(TTFont('HindiFont', FONT_PATH))

# ==========================
# LOAD OCR MODEL
# ==========================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['hi'], gpu=False)

reader = load_reader()

# ==========================
# FILE UPLOAD
# ==========================
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((800, 800))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            image_np = np.array(image)
            result = reader.readtext(image_np, detail=0, paragraph=True)

        extracted_text = "\n".join(result)

        # ==========================
        # DISPLAY TEXT
        # ==========================
        st.subheader("📜 Extracted Hindi Text:")
        st.text_area("", extracted_text, height=250)

        # ==========================
        # TXT DOWNLOAD
        # ==========================
        txt_bytes = extracted_text.encode("utf-8")
        st.download_button(
            "⬇️ Download TXT",
            data=txt_bytes,
            file_name="output.txt",
            mime="text/plain"
        )

        # ==========================
        # PDF DOWNLOAD
        # ==========================
        pdf_buf = BytesIO()
        c = canvas.Canvas(pdf_buf, pagesize=A4)
        width, height = A4
        y = height - 80  # top margin

        if os.path.exists(FONT_PATH):
            c.setFont("HindiFont", 14)
        else:
            c.setFont("Helvetica", 14)

        # Maintain line spacing
        line_height = 22
        lines = extracted_text.split("\n")

        for line in lines:
            wrapped_lines = []
            if len(line) > 100:
                # wrap long lines manually
                while len(line) > 100:
                    wrapped_lines.append(line[:100])
                    line = line[100:]
                if line:
                    wrapped_lines.append(line)
            else:
                wrapped_lines.append(line)

            for l in wrapped_lines:
                if y < 80:
                    c.showPage()
                    if os.path.exists(FONT_PATH):
                        c.setFont("HindiFont", 14)
                    else:
                        c.setFont("Helvetica", 14)
                    y = height - 80
                c.drawString(70, y, l)
                y -= line_height

        c.save()
        pdf_buf.seek(0)

        st.d
