import os
import fitz  # PyMuPDF
from PIL import Image
import io

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    img_count = 1

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for img in image_list:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            path = os.path.join(output_dir, f"image_{img_count}.{image_ext}")
            image.save(path)
            image_paths.append(path)
            img_count += 1

    return image_paths
