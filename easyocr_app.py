import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import io
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# Set Streamlit page config
st.set_page_config(page_title="Hindi OCR App", layout="centered")

# App title
st.title("📖 Hindi OCR Text Extractor")
st.write("Upload an image containing Hindi text and extract it as editable text.")

# Upload image
uploaded_image = st.file_uploader("📤 Upload an Image", type=["png", "jpg", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Text"):
        with st.spinner("Extracting text... Please wait..."):
            reader = easyocr.Reader(['hi', 'en'])
            result = reader.readtext(np.array(image), detail=0, paragraph=True)

            extracted_text = "\n".join(result)
            st.success("✅ Text extracted successfully!")

            st.text_area("📝 Extracted Text:", extracted_text, height=250)

            # --- Download buttons ---
            # TXT
            txt_bytes = extracted_text.encode("utf-8")
            st.download_button("📄 Download TXT", data=txt_bytes, file_name="extracted_text.txt")

            # DOCX
            doc = Document()
            doc.add_paragraph(extracted_text)
            docx_io = io.BytesIO()
            doc.save(docx_io)
            docx_io.seek(0)
            st.download_button("🗒️ Download DOCX", data=docx_io, file_name="extracted_text.docx")

            # PDF
            pdf_io = io.BytesIO()
            pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
            c = canvas.Canvas(pdf_io, pagesize=A4)
            c.setFont("HeiseiMin-W3", 14)
            y = 800
            for line in extracted_text.split("\n"):
                c.drawString(50, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    c.setFont("HeiseiMin-W3", 14)
                    y = 800
            c.save()
            pdf_io.seek(0)
            st.download_button("📘 Download PDF", data=pdf_io, file_name="extracted_text.pdf")
