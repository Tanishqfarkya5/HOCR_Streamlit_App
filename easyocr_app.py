import streamlit as st
import pytesseract
from PIL import Image
import io
from docx import Document
import tempfile

st.set_page_config(page_title="Hindi OCR App", layout="centered")

st.title("🪷 Hindi OCR App")
st.caption("Upload an image with Hindi or English text — extract and download as Word file.")

uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    st.info("🔍 Extracting text using Tesseract (please wait...)")

    # Perform OCR using pytesseract
    extracted_text = pytesseract.image_to_string(image, lang="hin+eng")

    st.subheader("📝 Extracted Text:")
    st.text_area("Recognized text:", extracted_text, height=250)

    # Generate Word file
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

st.markdown("---")
st.caption("✨ Built with Streamlit + Pytesseract")
