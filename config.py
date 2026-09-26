import os

MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"

UPLOAD_DIR = "uploads"
REPORT_DIR = "reports"
IMAGE_DIR = "extracted_images"

# Automatically create runtime directories to prevent FileNotFoundError
for directory in [UPLOAD_DIR, REPORT_DIR, IMAGE_DIR]:
    os.makedirs(directory, exist_ok=True)
