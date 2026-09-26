import os
from docling.document_converter import DocumentConverter

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> list[str]:
    """Extracts embedded images from a PDF using Docling and saves them to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    
    image_paths = []
    if hasattr(result.document, "pictures"):
        for idx, picture in enumerate(result.document.pictures):
            if picture.image and picture.image.pil_image:
                image = picture.image.pil_image
                image_path = os.path.join(output_dir, f"image_{idx+1}.jpg")
                image.save(image_path)
                image_paths.append(image_path)
                
    return image_paths
