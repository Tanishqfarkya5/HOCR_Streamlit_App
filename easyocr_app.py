import streamlit as st
from PIL import Image
import numpy as np
import io
import os

@st.cache_resource
def load_easyocr_reader(lang_list=["en"]):
    import easyocr
    return easyocr.Reader(lang_list, gpu=False)

st.set_page_config(page_title="EasyOCR Demo", layout="centered")
st.title("📷 EasyOCR Capstone — Streamlit App")
st.write("Upload images to extract text and download results.")

uploaded = st.file_uploader("Upload an image (jpg/png)", type=["jpg","jpeg","png"])
langs = st.multiselect("Languages for OCR", ["en", "hi"], default=["en"])

if uploaded:
    image = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)
    st.markdown("---")

    if st.button("Extract text"):
        with st.spinner("Running OCR..."):
            reader = load_easyocr_reader(lang_list=langs)
            img_np = np.array(image)
            results = reader.readtext(img_np)

        if not results:
            st.info("No text detected.")
        else:
            detected_text = [text for (_, text, _) in results]
            final_text = "\n".join(detected_text)

            st.subheader("📝 Detected text")
            st.text_area("Extracted Text", final_text, height=250)

            # === DOWNLOAD AS TEXT FILE ===
            st.download_button(
                label="📄 Download as TXT",
                data=final_text,
                file_name="extracted_text.txt",
                mime="text/plain"
            )

            # === DOWNLOAD AS DOCX FILE ===
            from docx import Document
            doc = Document()
            doc.add_paragraph(final_text)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="🧾 Download as DOCX",
                data=buffer,
                file_name="extracted_text.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            # === DOWNLOAD AS PDF FILE ===
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            y = height - 50
            for line in final_text.split("\n"):
                c.drawString(50, y, line)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = height - 50
            c.save()
            pdf_buffer.seek(0)
            st.download_button(
                label="📘 Download as PDF",
                data=pdf_buffer,
                file_name="extracted_text.pdf",
                mime="application/pdf"
            )

            # === Optional bounding boxes ===
            try:
                import cv2
                img_bboxes = img_np.copy()
                for (bbox, text, prob) in results:
                    pts = np.array(bbox).astype(int)
                    cv2.polylines(img_bboxes, [pts], isClosed=True, thickness=2, color=(0,255,0))
                st.image(img_bboxes, caption="With bounding boxes", use_container_width=True)
            except Exception as e:
                st.error(f"Error drawing boxes: {e}")
