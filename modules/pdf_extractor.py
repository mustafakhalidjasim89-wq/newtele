import os
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> list[str]:
    """Extracts embedded images from a PDF using Docling without triggering RapidOCR model downloads."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure pipeline to skip internal OCR
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    
    converter = DocumentConverter(
        format_options={
            "pdf": PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
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
