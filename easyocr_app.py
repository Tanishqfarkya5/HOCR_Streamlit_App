import streamlit as st
from PIL import Image
import pytesseract
from docx import Document
import io
import os
import urllib.request

# =============================
# ✅ Step 1: Use local folder for tessdata
# =============================
LOCAL_TESSDATA_DIR = os.path.join(os.getcwd(), "tessdata")
os.makedirs(LOCAL_TESSDATA_DIR, exist_ok=True)

HIN_MODEL = os.path.join(LOCAL_TESSDATA_DIR, "hin.traineddata")

if not os.path.exists(HIN_MODEL):
    st.info("🔽 Downloading Hindi OCR model (hin.traineddata)...")
    try:
        urllib.request.urlretrieve(
            "https://github.com/tesseract-ocr/tessdata_best/raw/main/hin.traineddata",
            HIN_MODEL
        )
        st.success("✅ Hindi OCR model downloaded successfully!")
    except Exception as e:
        st.error(f"❌ Error downloading Hindi model: {e}")

# Tell pytesseract where our local model is
os.environ["TESSDATA_PREFIX"] = LOCAL_TESSDATA_DIR

# =============================
# ✅ Step 2: Streamlit UI setup
# =============================
st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪔 Hindi OCR Text Extractor")
st.markdown("Upload a Hindi text image and extract editable text easily!")

uploaded_file = st.file_uploader("📤 Upload Hindi image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Uploaded Image", use_container_width=True)

    if st.button("🔍 Extract Text"):
        with st.spinner("Extracting text using Tesseract... Please wait..."):
            try:
                # Perform OCR in Hindi only
                extracted_text = pytesseract.image_to_string(image, lang="hin")

                if extracted_text.strip():
                    st.subheader("🪷 Extracted Hindi Text:")
                    st.text_area("Recognized text:", extracted_text, height=300)

                    # Save to Word file
                    doc = Document()
                    doc.add_paragraph(extracted_text)
                    buffer = io.BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Download Word File",
                        data=buffer,
                        file_name="Hindi_Text.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.warning("⚠️ No text detected. Try another image or check image clarity.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# =============================
# ✅ Footer
# =============================
st.markdown("---")
st.caption("✨ Made with Streamlit & Tesseract OCR | Supports Hindi text extraction")
