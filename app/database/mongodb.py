import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/calendar_agent")

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.get_database()
        self.history = self.db.get_collection("conversation_history")

    def get_history(self, user_id: str, limit: int = 10):
        """Recupera o histórico de mensagens de um usuário."""
        doc = self.history.find_one({"user_id": user_id})
        if doc:
            return doc.get("messages", [])[-limit:]
        return []

    def save_message(self, user_id: str, message: dict):
        """Adiciona uma mensagem ao histórico do usuário."""
        self.history.update_one(
            {"user_id": user_id},
            {"$push": {"messages": message}},
            upsert=True
        )

    def clear_history(self, user_id: str):
        """Limpa o histórico de um usuário."""
        self.history.delete_one({"user_id": user_id})

db_manager = DatabaseManager()
