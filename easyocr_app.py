import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from docx import Document
import io
import tempfile

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪷 Hindi OCR App (Word Output Only)")
st.caption("Extract Hindi or English text from images and download it as a Word file.")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    st.info("🔍 Extracting text, please wait...")

    # --- OCR ---
    reader = easyocr.Reader(["hi", "en"])
    result = reader.readtext(np.array(image), detail=0)
    extracted_text = "\n".join(result)

    # --- Display Extracted Text ---
    st.subheader("📝 Extracted Text:")
    st.text_area("", extracted_text, height=250)

    # --- Generate Word File ---
    def generate_docx(text):
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc.save(tmp.name)
        with open(tmp.name, "rb") as f:
            return io.BytesIO(f.read())

    # --- Download Button ---
    st.download_button(
        label="📝 Download as Word",
        data=generate_docx(extracted_text),
        file_name="hindi_text.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
