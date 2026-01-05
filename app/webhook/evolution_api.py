import os
import requests
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")

def send_whatsapp_message(number: str, text: str):
    # Evolution v2 often prefers just the numbers without @s.whatsapp.net
    clean_number = number.split("@")[0]
    
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": clean_number,
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201 and response.status_code != 200:
            print(f"Error Evolution API: {response.status_code} - {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None
