import streamlit as st
import easyocr
from PIL import Image
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
import numpy as np
import tempfile
import os

# Streamlit page setup
st.set_page_config(page_title="Hindi OCR App", layout="centered")

st.title("🪷 Hindi OCR App - Extract Text from Images")
st.write("Upload an image containing Hindi text. The app will extract and allow you to download it as PDF or Word.")

# File uploader
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Initialize EasyOCR
    reader = easyocr.Reader(['hi', 'en'])  # Hindi + English
    st.write("Extracting text... please wait ⏳")

    # Perform OCR
    result = reader.readtext(np.array(image), detail=0)
    extracted_text = "\n".join(result)

    st.subheader("📝 Extracted Text:")
    st.text_area("Text Output", extracted_text, height=250)

    # Generate PDF
    def generate_pdf(text):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        text_object = pdf.beginText(50, height - 50)
        text_object.setFont("Helvetica", 12)
        for line in text.split("\n"):
            text_object.textLine(line)
        pdf.drawText(text_object)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

    # Generate Word file
    def generate_docx(text):
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc.save(temp_path.name)
        with open(temp_path.name, "rb") as f:
            return io.BytesIO(f.read())

    # Download buttons
    pdf_bytes = generate_pdf(extracted_text)
    st.download_button(
        label="📄 Download as PDF",
        data=pdf_bytes,
        file_name="extracted_text.pdf",
        mime="application/pdf"
    )

    docx_bytes = generate_docx(extracted_text)
    st.download_button(
        label="📝 Download as Word (.docx)",
        data=docx_bytes,
        file_name="extracted_text.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
