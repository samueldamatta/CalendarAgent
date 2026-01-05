from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class WebhookKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str

class WebhookMessage(BaseModel):
    conversation: Optional[str] = None
    extendedTextMessage: Optional[Dict[str, Any]] = None

class WebhookData(BaseModel):
    key: WebhookKey
    message: Optional[Dict[str, Any]] = None
    pushName: Optional[str] = None
    messageTimestamp: Optional[int] = None

class EvolutionWebhook(BaseModel):
    event: str
    instance: str
    data: Dict[str, Any]
