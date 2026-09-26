import base64
import json
import os
import re
import time
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
            "issue_type": "Audit Finding",
            "observation": raw_text.strip() if raw_text else "No observation returned",
            "severity": "Medium",
            "risk": "Requires inspection",
            "corrective_action": "Verify manually",
            "status": "Open",
            "confidence": 50
        }

def analyze_image(image_path: str, prompt: str, ocr_text: str = "") -> dict:
    """Calls Hugging Face Inference API with retry logic for model cold starts."""
    api_url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-VL-7B-Instruct"
    
    # Ensure HF_TOKEN exists in Streamlit Secrets
    hf_token = st.secrets.get("HF_TOKEN", "")
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

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

    # Try up to 3 times to handle model loading / cold starts
    for attempt in range(3):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response_data = response.json()

            # If model is loading, wait and retry
            if isinstance(response_data, dict) and "error" in response_data:
                if "loading" in response_data["error"].lower():
                    time.sleep(15)
                    continue
                else:
                    st.warning(f"API Warning ({os.path.basename(image_path)}): {response_data['error']}")
                    return clean_json_output(response_data["error"])

            if isinstance(response_data, list) and len(response_data) > 0:
                raw_text = response_data[0].get("generated_text", str(response_data[0]))
            elif isinstance(response_data, dict):
                raw_text = response_data.get("generated_text", str(response_data))
            else:
                raw_text = str(response_data)

            return clean_json_output(raw_text)

        except Exception as e:
            if attempt == 2:
                st.error(f"Inference error on {os.path.basename(image_path)}: {e}")
                return {
                    "equipment": "N/A",
                    "vendor": "N/A",
                    "issue_type": "Error",
                    "observation": f"Inference failed: {str(e)}",
                    "severity": "Low",
                    "risk": "None",
                    "corrective_action": "Retry inspection",
                    "status": "Failed",
                    "confidence": 0
                }
            time.sleep(3)
