import os
import requests
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import process_message

load_dotenv()

app = FastAPI()

# Evolution API Config
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

@app.get("/")
async def root():
    return {"status": "online", "message": "Calendar Agent API is running"}

@app.post("/webhook")
async def evolution_webhook(request: Request):
    data = await request.json()
    print(f"Received webhook: {data}")

    # Evolution API sends 'messages.upsert' event for new messages
    event = data.get("event")
    if event == "messages.upsert":
        message_data = data.get("data", {})
        key = message_data.get("key", {})
        from_me = key.get("fromMe", False)
        
        # Avoid responding to our own messages
        if from_me:
            return {"status": "ignored", "reason": "own_message"}

        remote_jid = key.get("remoteJid")
        # Text message is usually in message.conversation or message.extendedTextMessage.text
        message = message_data.get("message", {})
        text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text")

        if text and remote_jid:
            print(f"Message from {remote_jid}: {text}")
            
            # Process with AI Agent
            response_text = process_message(text)
            print(f"Agent response: {response_text}")
            
            # Send back to WhatsApp using the full remote_jid
            send_whatsapp_message(remote_jid, response_text)
            
            return {"status": "success"}

    return {"status": "ignored", "event": event}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
