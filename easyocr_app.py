import streamlit as st
import easyocr
import pytesseract
from PIL import Image
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


# ------------------------------------------------------------
# ⚙️ APP CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪷 Hindi Handwritten OCR (Tesseract + EasyOCR Fallback)")
st.markdown("Upload an image with **Hindi or English handwritten text**, and extract it accurately.")


# ------------------------------------------------------------
# 🧠 CACHED OCR LOADERS
# ------------------------------------------------------------
@st.cache_resource
def load_easyocr():
    return easyocr.Reader(['hi', 'en'], gpu=False)

@st.cache_resource
def load_tesseract():
    return pytesseract


# ------------------------------------------------------------
# 🧩 FUNCTIONS
# ------------------------------------------------------------
def extract_with_tesseract(image):
    try:
        text = pytesseract.image_to_string(image, lang='hin+eng')
        return text.strip()
    except Exception as e:
        return f"Tesseract error: {str(e)}"


def extract_with_easyocr(image):
    try:
        reader = load_easyocr()
        np_image = np.array(image)
        result = reader.readtext(np_image, detail=0)
        return "\n".join(result)
    except Exception as e:
        return f"EasyOCR error: {str(e)}"


def create_text_download(text):
    """Return a downloadable .txt file"""
    buffer = BytesIO()
    buffer.write(text.encode('utf-8'))
    buffer.seek(0)
    return buffer


def create_pdf_download(text):
    """Return a downloadable .pdf file"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 60
    for line in text.split('\n'):
        p.drawString(60, y, line)
        y -= 18
        if y < 60:
            p.showPage()
            y = height - 60
    p.save()
    buffer.seek(0)
    return buffer


# ------------------------------------------------------------
# 🖼️ IMAGE UPLOAD
# ------------------------------------------------------------
uploaded_image = st.file_uploader("Upload handwritten Hindi/English image", type=["jpg", "jpeg", "png"])

if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    image.thumbnail((1200, 1200))
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Text"):
        with st.spinner("Extracting text... please wait"):
            text_tesseract = extract_with_tesseract(image)

            # if too short or empty, use EasyOCR fallback
            if len(text_tesseract.strip()) < 10:
                st.warning("Tesseract output too short, switching to EasyOCR fallback...")
                text = extract_with_easyocr(image)
            else:
                text = text_tesseract

        st.success("✅ Text extracted successfully!")
        st.text_area("🧾 Extracted Text:", text, height=300)

        # Download buttons
        txt_buffer = create_text_download(text)
        pdf_buffer = create_pdf_download(text)

        st.download_button("⬇️ Download as TXT", data=txt_buffer,
                           file_name="extracted_text.txt", mime="text/plain")

        st.download_button("⬇️ Download as PDF", data=pdf_buffer,
                           file_name="extracted_text.pdf", mime="application/pdf")
