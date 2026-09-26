from paddleocr import PaddleOCR

# Lazy loading OCR instance to optimize resource usage
_ocr_instance = None

def get_ocr_engine():
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang="en")
    return _ocr_instance

def read_text(image_path: str) -> str:
    """Extracts text strings from an image using PaddleOCR."""
    ocr = get_ocr_engine()
    result = ocr.ocr(image_path, cls=True)
    
    extracted_text = []
    if result and result[0]:
        for line in result[0]:
            if line and len(line) > 1:
                extracted_text.append(line[1][0])
                
    return " ".join(extracted_text)
