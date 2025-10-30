import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Hindi OCR App", layout="centered")
st.title("🪶 Hindi OCR App using EasyOCR")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['hi'], gpu=False)  # only Hindi

reader = load_reader()

uploaded_file = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((800,800))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            image_np = np.array(image)
            result = reader.readtext(image_np, detail=0, paragraph=True)

        extracted_text = "\n".join(result)
        st.subheader("Extracted Text")
        st.text_area("", extracted_text, height=200)

        # TXT
        txt_bytes = extracted_text.encode("utf-8")
        st.download_button("Download TXT", data=txt_bytes, file_name="output.txt", mime="text/plain")

        # DOCX
        doc = Document()
        doc.add_paragraph(extracted_text)
        docx_buf = BytesIO()
        doc.save(docx_buf)
        docx_buf.seek(0)
        st.download_button("Download DOCX", data=docx_buf, file_name="output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # PDF
        pdf_buf = BytesIO()
        c = canvas.Canvas(pdf_buf, pagesize=A4)
        width, height = A4
        y = height - 50
        for line in extracted_text.split("\n"):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line)
            y -= 20
        c.save()
        pdf_buf.seek(0)
        st.download_button("Download PDF", data=pdf_buf, file_name="output.pdf", mime="application/pdf")

else:
    st.info("Upload an image to start")
