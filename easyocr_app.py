import streamlit as st
import cv2
import json
import numpy as np
import re
import os
from PIL import Image
import easyocr
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from indicnlp.tokenize import indic_tokenize
from docx import Document

# =========================
# 🔧 HELPER FUNCTIONS
# =========================

def run_easyocr(img_path):
    reader = easyocr.Reader(['hi', 'en'])
    results = reader.readtext(img_path, detail=1, paragraph=False)
    h, w, _ = cv2.imread(img_path).shape
    layout_data = []
    for (bbox, text, conf) in results:
        x_coords = [pt[0] for pt in bbox]
        y_coords = [pt[1] for pt in bbox]
        x0, y0, x1, y1 = min(x_coords), min(y_coords), max(x_coords), max(y_coords)
        x0 /= w; x1 /= w; y0 /= h; y1 /= h
        layout_data.append({
            "text": text.strip(),
            "bbox": [round(x0,4), round(y0,4), round(x1,4), round(y1,4)],
            "confidence": round(float(conf), 4)
        })
    return layout_data


def reconstruct_text(ocr_data):
    if not ocr_data:
        return "⚠️ No OCR data found."

    ocr_data = sorted(ocr_data, key=lambda x: (x["bbox"][1], x["bbox"][0]))
    LINE_Y_THRESHOLD = 0.03
    INDENT_MULTIPLIER = 55
    PARAGRAPH_GAP_RATIO = 1.8

    lines, current_line = [], [ocr_data[0]]
    for i in range(1, len(ocr_data)):
        prev_y = np.mean([current_line[-1]["bbox"][1], current_line[-1]["bbox"][3]])
        curr_y = np.mean([ocr_data[i]["bbox"][1], ocr_data[i]["bbox"][3]])
        if abs(curr_y - prev_y) < LINE_Y_THRESHOLD:
            current_line.append(ocr_data[i])
        else:
            lines.append(current_line)
            current_line = [ocr_data[i]]
    lines.append(current_line)

    clean_lines = []
    for line in lines:
        line = sorted(line, key=lambda x: x["bbox"][0])
        raw_text = " ".join([x["text"] for x in line])
        clean_text = re.sub(r"[^ऀ-ॿA-Za-z0-9\s।,!?\"'\-]", "", raw_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        clean_lines.append({
            "text": clean_text,
            "bbox": np.mean([w["bbox"] for w in line], axis=0).tolist()
        })

    final_text = ""
    last_y_bottom = 0
    avg_line_gap = np.median([
        clean_lines[i+1]["bbox"][1] - clean_lines[i]["bbox"][3]
        for i in range(len(clean_lines)-1)
    ]) if len(clean_lines) > 1 else 0.03

    for idx, line in enumerate(clean_lines):
        x0, y0, x1, y1 = line["bbox"]
        indent_spaces = int(x0 * INDENT_MULTIPLIER)
        indent = " " * max(indent_spaces, 0)
        if idx > 0:
            gap = y0 - last_y_bottom
            if gap > avg_line_gap * PARAGRAPH_GAP_RATIO:
                final_text += "\n"
        line_text = line["text"]
        if idx < len(clean_lines) - 1 and not re.search(r"[।!?\"']$", line_text):
            line_text += " "
        final_text += indent + line_text + "\n"
        last_y_bottom = y1

    final_text = re.sub(r"\n{3,}", "\n\n", final_text).strip()
    return final_text


def clean_hindi_text(text):
    text = re.sub(r"[A-Za-z0-9]+", "", text)
    text = re.sub(r"[^ऀ-ॿ।,!? \n\-]", "", text)
    text = re.sub(r"(?<![अ-ह])([ा-ौ])", "", text)
    text = re.sub(r"\s+([।,!?])", r"\1", text)
    text = re.sub(r"([।!?])([^ \n])", r"\1 \2", text)
    text = re.sub(r" +", " ", text)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    merged_lines = []
    for i, line in enumerate(lines):
        if i > 0 and len(line) < 20:
            merged_lines[-1] += " " + line
        else:
            merged_lines.append(line)
    return "\n".join(merged_lines).strip()


def normalize_hindi_text(text):
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer("hi")
    lines = text.split("\n")
    normalized_lines = []
    for line in lines:
        norm = normalizer.normalize(line)
        tokens = indic_tokenize.trivial_tokenize(norm)
        norm_line = " ".join(tokens)
        normalized_lines.append(norm_line.strip())
    return "\n".join(normalized_lines)


def save_docx(text, output_path):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(output_path)


# =========================
# 🎨 STREAMLIT APP
# =========================
st.set_page_config(page_title="Hindi OCR App", layout="centered")

st.title("🪷 Hindi Handwritten OCR with Layout Reconstruction")
st.write("Upload a Hindi handwritten image, extract text, and export as TXT or DOCX.")

uploaded_file = st.file_uploader("📤 Upload an image (JPG/PNG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    img_path = "temp_input.png"
    img.save(img_path)
    st.image(img, caption="📄 Uploaded Image", use_column_width=True)

    if st.button("🚀 Run OCR"):
        with st.spinner("Running Hindi OCR... Please wait ⏳"):
            ocr_data = run_easyocr(img_path)
            raw_text = reconstruct_text(ocr_data)
            cleaned = clean_hindi_text(raw_text)
            final_text = normalize_hindi_text(cleaned)

        st.success("✅ OCR Completed Successfully!")
        st.subheader("🧠 Extracted Text:")
        st.text_area("OCR Output", final_text, height=300)

        # ===== Save Outputs =====
        txt_path = "output_hindi_text.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        docx_path = "output_hindi_text.docx"
        save_docx(final_text, docx_path)

        st.download_button("⬇️ Download TXT", open(txt_path, "rb"), file_name="hindi_text.txt")
        st.download_button("⬇️ Download DOCX", open(docx_path, "rb"), file_name="hindi_text.docx")

        st.info("You can now download the extracted Hindi text in your preferred format.")
