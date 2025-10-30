import streamlit as st
import easyocr
from PIL import Image
import io
from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# Register Hindi-compatible font for PDF
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# Streamlit App Configuration
st.set_page_config(page_title="EasyOCR Hindi App", layout="centered")
st.title("📄 EasyOCR - Hindi Handwritten Text Extractor")

# Upload image
uploaded_file = st.file_uploader("Upload a Hindi handwritten image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🪄 Extract Text"):
        with st.spinner("Extracting text... कृपया प्रतीक्षा करें..."):
            reader = easyocr.Reader(['hi', 'en'], gpu=False)
            result = reader.readtext(np.array(image), detail=0)

        extracted_text = "\n".join(result).strip()

        # Display extracted text
        st.subheader("📝 Extracted Text:")
        st.text_area("Extracted Text", extracted_text, height=300)

        # ---- Save as DOCX ----
        doc = Document()
        para = doc.add_paragraph(extracted_text)
        para.style.font.name = 'Mangal'
        para.style.font.size = Pt(14)
        docx_stream = io.BytesIO()
        doc.save(docx_stream)
        docx_stream.seek(0)

        # ---- Save as PDF ----
        pdf_stream = io.BytesIO()
        c = canvas.Canvas(pdf_stream, pagesize=A4)
        text_obj = c.beginText(50, 800)
        text_obj.setFont("STSong-Light", 14)
        for line in extracted_text.split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)
        c.showPage()
        c.save()
        pdf_stream.seek(0)

        # ---- Download buttons ----
        st.download_button("⬇️ Download DOCX", docx_stream, "output_text.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.download_button("⬇️ Download PDF", pdf_stream, "output_text.pdf", "application/pdf")

        st.success("✅ Text extracted and files ready to download!")
