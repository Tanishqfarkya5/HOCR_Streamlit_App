import streamlit as st
from PIL import Image
import pytesseract
from docx import Document
import io
import tempfile
import numpy as np

st.set_page_config(page_title="Hindi OCR (Word Export)", layout="centered")
st.title("🪷 Hindi OCR (Word Export)")
st.caption("Upload an image containing Hindi or English text and download it as a Word file.")

# File upload
uploaded_file = st.file_uploader("📤 Upload image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    st.info("🔍 Extracting text, please wait...")

    # OCR using pytesseract
    extracted_text = pytesseract.image_to_string(image, lang="hin+eng")

    # Display extracted text
    st.subheader("📝 Extracted Text:")
    st.text_area("", extracted_text, height=250)

    # Generate Word File
    def generate_docx(text):
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc.save(tmp.name)
        with open(tmp.name, "rb") as f:
            return io.BytesIO(f.read())

    st.download_button(
        label="📥 Download Word File",
        data=generate_docx(extracted_text),
        file_name="extracted_text.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
