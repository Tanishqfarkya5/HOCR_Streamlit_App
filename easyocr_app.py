import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# ------------------------------
# APP TITLE & DESCRIPTION
# ------------------------------
st.set_page_config(page_title="Image Text Extractor", page_icon="🪄")
st.title("🪄 OCR Text Extractor using EasyOCR")
st.markdown(
    """
    Upload an image below and extract text automatically using **EasyOCR**.
    This app supports **English, Hindi**, and other languages as needed.
    """
)

# ------------------------------
# FILE UPLOAD SECTION
# ------------------------------
uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

# If image uploaded
if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Uploaded Image", use_column_width=True)

    # Add a button for OCR
    if st.button("🔍 Extract Text"):
        with st.spinner("Extracting text... Please wait ⏳"):
            # Initialize EasyOCR reader (verbose=False to suppress logs)
            reader = easyocr.Reader(['en', 'hi'], verbose=False)

            # Convert image → NumPy array
            img_array = np.array(image)

            # Extract text (detail=0 gives only text, not coordinates)
            result = reader.readtext(img_array, detail=0)

        # Display results
        st.success("✅ Text extracted successfully!")
        if result:
            st.subheader("📄 Extracted Text:")
            extracted_text = "\n".join(result)
            st.text_area("Text Output", extracted_text, height=200)
        else:
            st.warning("No text detected in the image.")

# ------------------------------
# FOOTER
# ------------------------------
st.markdown(
    """
    ---
    🔧 **Built with:** Streamlit + EasyOCR  
    📦 **Author:** Your Name  
    💡 *Supports multilingual OCR recognition.*
    """
)
