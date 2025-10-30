import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from docx import Document
import io
import os
import urllib.request
import cv2
import numpy as np

# =============================
# ✅ Setup Hindi model (best version)
# =============================
LOCAL_TESSDATA_DIR = os.path.join(os.getcwd(), "tessdata_best")
os.makedirs(LOCAL_TESSDATA_DIR, exist_ok=True)
HIN_MODEL = os.path.join(LOCAL_TESSDATA_DIR, "hin.traineddata")
ENG_MODEL = os.path.join(LOCAL_TESSDATA_DIR, "eng.traineddata")

# Download Hindi & English models if missing
def download_model(lang, path):
    if not os.path.exists(path):
        url = f"https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata"
        st.info(f"🔽 Downloading {lang} model...")
        urllib.request.urlretrieve(url, path)
        st.success(f"✅ {lang} model downloaded successfully!")

download_model("hin", HIN_MODEL)
download_model("eng", ENG_MODEL)

os.environ["TESSDATA_PREFIX"] = LOCAL_TESSDATA_DIR

# =============================
# ✅ Streamlit UI
# =============================
st.set_page_config(page_title="Improved Hindi OCR", layout="centered")
st.title("🪷 Improved Hindi OCR App")
st.markdown("Upload a Hindi or mixed Hindi-English text image for cleaner OCR output.")

uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="📸 Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Text"):
        with st.spinner("Processing and extracting text..."):
            try:
                # Convert image to OpenCV format
                img = np.array(image.convert('RGB'))
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

                # ✅ Preprocessing: denoise + threshold + enlarge
                img = cv2.GaussianBlur(img, (3, 3), 0)
                img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

                # Save temp image
                temp_path = "temp.png"
                cv2.imwrite(temp_path, img)

                # ✅ Use both Hindi + English for better handling
                extracted_text = pytesseract.image_to_string(Image.open(temp_path), lang="hin+eng")

                if extracted_text.strip():
                    st.subheader("🪔 Recognized Hindi Text:")
                    st.text_area("Recognized text:", extracted_text, height=350)

                    # Save to Word
                    doc = Document()
                    doc.add_paragraph(extracted_text)
                    buffer = io.BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Download Word File",
                        data=buffer,
                        file_name="Hindi_Extracted_Text.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.warning("⚠️ No clear text found. Try a sharper image or better lighting.")

            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")
st.caption("💡 Uses Tesseract tessdata_best for Hindi-English OCR | Streamlit + OpenCV + Python-docx")

