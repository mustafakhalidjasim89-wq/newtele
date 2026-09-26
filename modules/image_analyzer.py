import re
import json
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from config import MODEL_NAME

processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

def clean_json_output(raw_text: str) -> dict:
    """Extracts a valid JSON dict from model text, stripping markdown codeblocks if present."""
    try:
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(raw_text)
    except Exception:
        return {
            "equipment": "Unknown",
            "vendor": "Unknown",
            "issue_type": "Unstructured Response",
            "observation": raw_text.strip(),
            "severity": "Medium",
            "risk": "Requires manual inspection",
            "corrective_action": "Verify finding manually",
            "status": "Open",
            "confidence": 50
        }

def analyze_image(image_path: str, prompt: str, ocr_text: str = "") -> dict:
    """Analyzes an image using Qwen2.5-VL with optional OCR context enrichment."""
    image = Image.open(image_path).convert("RGB")
    
    full_prompt = prompt
    if ocr_text.strip():
        full_prompt += f"\n\nContext extracted via OCR from image:\n{ocr_text}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": full_prompt}
            ]
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = processor(
        text=[text],
        images=[image],
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.1
        )

    # Trim prompt tokens from generation output
    generated_ids = [
        output_ids[len(input_ids):] 
        for input_ids, output_ids in zip(inputs.input_ids, output_ids)
    ]
    
    raw_response = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    return clean_json_output(raw_response)
