import os
from supabase import create_client, Client

class Database:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Ошибка: SUPABASE_URL или SUPABASE_KEY не найдены в .env")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def get_balance(self, user_id: int):
        res = self.client.table("users").select("balance").eq("user_id", user_id).maybe_single().execute()
        return res.data['balance'] if res.data else 1000

    def add_warn(self, user_id: int, reason: str, moderator: str):
        self.client.table("warns").insert({
            "user_id": user_id, 
            "reason": reason, 
            "moderator": moderator
        }).execute()