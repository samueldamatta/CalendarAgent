from fastapi import APIRouter, Request, HTTPException
from app.agent.assistant import process_message
from app.webhook.evolution_api import send_whatsapp_message

router = APIRouter()

@router.post("/webhook")
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
            
            # Process with AI Agent (passando o remote_jid como user_id para a memória)
            response_text = process_message(remote_jid, text)
            print(f"Agent response: {response_text}")
            
            # Send back to WhatsApp using the full remote_jid
            send_whatsapp_message(remote_jid, response_text)
            
            return {"status": "success"}

    return {"status": "ignored", "event": event}
