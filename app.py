import os
import streamlit as st

from config import UPLOAD_DIR, REPORT_DIR, IMAGE_DIR
from modules.pdf_extractor import extract_images_from_pdf
from modules.ocr_reader import read_text
from modules.image_analyzer import analyze_image
from modules.report_generator import generate_excel
from modules.summary_generator import generate_text_summary

st.set_page_config(page_title="Telecom Audit AI", layout="wide")

st.title("📡 Telecom Audit AI Inspector")
st.write("Automated visual defect identification and site audit report generator.")

use_ocr = st.sidebar.checkbox("Enable OCR Context Integration", value=True)

uploaded = st.file_uploader("Upload Inspection PDF", type=["pdf"])

if uploaded:
    pdf_path = os.path.join(UPLOAD_DIR, uploaded.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded.read())

    st.success(f"Uploaded: `{uploaded.name}`")

    with st.spinner("Extracting images from PDF via Docling..."):
        images = extract_images_from_pdf(pdf_path, IMAGE_DIR)

    st.info(f"Extracted **{len(images)}** images for inspection.")

    prompt_path = os.path.join("prompts", "telecom_prompt.txt")
    with open(prompt_path, "r") as f:
        prompt = f.read()

    findings = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, image_path in enumerate(images):
        status_text.text(f"Analyzing image {idx + 1} of {len(images)}: {os.path.basename(image_path)}")

        ocr_text = ""
        if use_ocr:
            try:
                ocr_text = read_text(image_path)
            except Exception:
                pass

        data = analyze_image(image_path, prompt, ocr_text=ocr_text)

        findings.append({
            "Photo No": idx + 1,
            "Photo Name": os.path.basename(image_path),
            "Equipment": data.get("equipment", ""),
            "Vendor": data.get("vendor", ""),
            "Issue Type": data.get("issue_type", ""),
            "Observation": data.get("observation", ""),
            "Severity": data.get("severity", ""),
            "Risk": data.get("risk", ""),
            "Corrective Action": data.get("corrective_action", ""),
            "Status": data.get("status", "Open"),
            "AI Confidence (%)": data.get("confidence", 0)
        })

        progress_bar.progress((idx + 1) / len(images))

    status_text.text("Building Excel report...")
    report_path = os.path.join(REPORT_DIR, "Telecom_Audit_Report.xlsx")
    generate_excel(findings, report_path)

    st.success("Analysis Complete!")

    # Display Text Summary
    st.subheader("Executive Summary")
    st.write(generate_text_summary(findings))

    # Display Table Preview
    st.subheader("Inspection Findings Preview")
    st.dataframe(findings)

    # Download Button
    with open(report_path, "rb") as file:
        st.download_button(
            label="📥 Download Audit Report (.xlsx)",
            data=file,
            file_name="Telecom_Audit_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
