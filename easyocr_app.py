import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from docx import Document
import numpy as np
import io, os, urllib.request, cv2

st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪷 Hindi OCR (Tesseract-based)")
st.markdown("Upload a Hindi text image to extract and download the recognized text as a Word file.")

# --- Model setup ---
MODEL_DIR = os.path.join(os.getcwd(), "tessdata_best")
os.makedirs(MODEL_DIR, exist_ok=True)
HIN_PATH = os.path.join(MODEL_DIR, "hin.traineddata")
ENG_PATH = os.path.join(MODEL_DIR, "eng.traineddata")

def download_model(lang, path):
    if not os.path.exists(path):
        url = f"https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata"
        st.info(f"📦 Downloading {lang} model...")
        urllib.request.urlretrieve(url, path)
        st.success(f"✅ {lang} model ready!")

download_model("hin", HIN_PATH)
download_model("eng", ENG_PATH)
os.environ["TESSDATA_PREFIX"] = MODEL_DIR

# --- File uploader ---
uploaded_file = st.file_uploader("📤 Upload image (Hindi or mixed text)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="📸 Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Hindi Text"):
        with st.spinner("Processing image and extracting Hindi text..."):
            try:
                # Convert to grayscale
                img = np.array(image.convert("RGB"))
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

                # Denoise & enhance
                gray = cv2.bilateralFilter(gray, 11, 17, 17)
                gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 31, 2)

                # Sharpen & enlarge
                gray = cv2.resize(gray, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
                gray = cv2.GaussianBlur(gray, (1, 1), 0)

                # Save temporary processed file
                cv2.imwrite("temp.png", gray)

                # Perform OCR
                text = pytesseract.image_to_string(Image.open("temp.png"), lang="hin+eng")

                if text.strip():
                    st.subheader("🪔 Recognized Text:")
                    st.text_area("", text, height=300)

                    # Create Word file
                    doc = Document()
                    doc.add_paragraph(text)
                    buf = io.BytesIO()
                    doc.save(buf)
                    buf.seek(0)

                    st.download_button(
                        label="📥 Download Word File",
                        data=buf,
                        file_name="Hindi_OCR_Output.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.warning("⚠️ No readable Hindi text found in the image.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.caption("---")
st.caption("💡 Tip: Use clear, well-lit images with 300+ DPI for best OCR accuracy.")
