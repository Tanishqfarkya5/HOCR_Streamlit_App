import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document

st.set_page_config(page_title="Hindi OCR App", layout="centered")

st.title("🪶 Hindi OCR App using EasyOCR")

# Initialize EasyOCR Reader
@st.cache_resource
def load_reader():
    return easyocr.Reader(['hi', 'en'])  # Hindi + English

reader = load_reader()

uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Extracting text... Please wait ⏳"):
        image_np = np.array(image)
        result = reader.readtext(image_np, detail=0)

    extracted_text = "\n".join(result)

    st.subheader("📜 Extracted Text")
    st.text_area("Detected Hindi Text", extracted_text, height=250)

    # Convert to bytes for downloads
    txt_bytes = extracted_text.encode("utf-8")

    # --- PDF Download ---
    def create_pdf(text):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont("Helvetica", 12)
        width, height = A4
        y = height - 50
        for line in text.split("\n"):
            if y <= 50:
                p.showPage()
                p.setFont("Helvetica", 12)
                y = height - 50
            p.drawString(50, y, line)
            y -= 20
        p.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf(extracted_text)

    # --- Word (DOCX) Download ---
    def create_docx(text):
        doc = Document()
        doc.add_heading("Hindi OCR Extracted Text", level=1)
        doc.add_paragraph(text)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    docx_buffer = create_docx(extracted_text)

    # Download Buttons
    st.download_button(
        "📥 Download as TXT",
        data=txt_bytes,
        file_name="hindi_text.txt",
        mime="text/plain"
    )

    st.download_button(
        "📄 Download as PDF",
        data=pdf_buffer,
        file_name="hindi_text.pdf",
        mime="application/pdf"
    )

    st.download_button(
        "📝 Download as Word (DOCX)",
        data=docx_buffer,
        file_name="hindi_text.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

else:
    st.info("👆 Please upload an image to start OCR.")
