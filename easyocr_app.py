import streamlit as st
from PIL import Image
import pytesseract
from docx import Document
import cv2, numpy as np, io, os, urllib.request

st.set_page_config(page_title="Hindi OCR (Clean Output)", layout="centered")
st.title("🪷 Hindi OCR – Clean & Accurate Text Extraction")

MODEL_DIR = os.path.join(os.getcwd(), "tessdata_best")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "hin.traineddata")

# Download best Hindi model if missing
if not os.path.exists(MODEL_PATH):
    st.info("📥 Downloading Hindi OCR model...")
    urllib.request.urlretrieve(
        "https://github.com/tesseract-ocr/tessdata_best/raw/main/hin.traineddata",
        MODEL_PATH,
    )
    st.success("✅ Model downloaded!")

os.environ["TESSDATA_PREFIX"] = MODEL_DIR

uploaded = st.file_uploader("📸 Upload Hindi text image", type=["png", "jpg", "jpeg"])

def preprocess_image(image):
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    gray = cv2.equalizeHist(gray)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY, 35, 11)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((1, 1), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    return gray

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Hindi Text"):
        with st.spinner("Extracting text..."):
            processed = preprocess_image(image)
            cv2.imwrite("processed.png", processed)
            
            text = pytesseract.image_to_string(
                Image.open("processed.png"), lang="hin", config="--psm 6"
            )

            # Clean common OCR artifacts
            clean_text = (
                text.replace("§", "")
                    .replace("™", "")
                    .replace("ﬂ", "")
                    .replace("|", "")
                    .replace("ﬁ", "")
                    .replace("ﬂ", "")
                    .strip()
            )

            if clean_text:
                st.subheader("🪔 Recognized Hindi Text:")
                st.text_area("", clean_text, height=300)

                doc = Document()
                doc.add_paragraph(clean_text)
                buf = io.BytesIO()
                doc.save(buf)
                buf.seek(0)
                st.download_button(
                    "📥 Download Word File",
                    buf,
                    "Hindi_OCR_Clean.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            else:
                st.warning("⚠️ No readable Hindi text detected.")

st.caption("---")
st.caption("💡 Tip: Upload clear, printed Hindi text (300 DPI+) for best results.")
