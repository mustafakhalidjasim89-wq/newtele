import base64
import json
import re
import requests
import streamlit as st

def clean_json_output(raw_text: str) -> dict:
    """Extracts JSON object from model output string."""
    try:
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(raw_text)
    except Exception:
        return {
            "equipment": "Unknown",
            "vendor": "Unknown",
            "issue_type": "Unstructured Output",
            "observation": raw_text.strip(),
            "severity": "Medium",
            "risk": "Requires manual review",
            "corrective_action": "Verify finding manually",
            "status": "Open",
            "confidence": 50
        }

def analyze_image(image_path: str, prompt: str, ocr_text: str = "") -> dict:
    """Calls Hugging Face Inference API to analyze image without local GPU/RAM consumption."""
    api_url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-VL-7B-Instruct"
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    full_prompt = prompt
    if ocr_text.strip():
        full_prompt += f"\n\nContext extracted via OCR:\n{ocr_text}"

    payload = {
        "inputs": {
            "image": f"data:image/jpeg;base64,{encoded_image}",
            "prompt": full_prompt
        },
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.1
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response_data = response.json()
        
        if isinstance(response_data, list) and "generated_text" in response_data[0]:
            raw_text = response_data[0]["generated_text"]
        elif isinstance(response_data, dict) and "generated_text" in response_data:
            raw_text = response_data["generated_text"]
        else:
            raw_text = str(response_data)
            
        return clean_json_output(raw_text)

    except Exception as e:
        return {
            "equipment": "API Error",
            "vendor": "Unknown",
            "issue_type": "Inference Error",
            "observation": f"Failed to query inference endpoint: {str(e)}",
            "severity": "Low",
            "risk": "None",
            "corrective_action": "Check API Key and endpoint",
            "status": "Failed",
            "confidence": 0
        }
