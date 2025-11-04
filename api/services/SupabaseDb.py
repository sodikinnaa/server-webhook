from supabase import create_client, Client
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.url, self.key)

    # -------------------------
    # USERS TABLE
    # -------------------------
    def insert_user(self, wa_number: str, token: str):
        """Menambahkan user baru"""
        data = {"wa_number": wa_number, "token": token}
        res = self.client.table("users").insert(data).execute()
        return res.data

    def get_user_by_wa(self, wa_number: str):
        """Mengambil data user berdasarkan nomor WA"""
        res = self.client.table("users").select("*").eq("wa_number", wa_number).execute()
        return res.data[0] if res.data else None

    def get_user_by_token(self, token: str):
        """Autentikasi berdasarkan token"""
        res = self.client.table("users").select("*").eq("token", token).execute()
        return res.data[0] if res.data else None

    # -------------------------
    # WP CREDENTIALS TABLE
    # -------------------------
    def insert_wp_credential(self, data):
        """Menyimpan kredensial WP baru"""
        # Ensure 'created_at' is formatted as ISO 8601 for PostgreSQL compatibility
        from datetime import datetime

        created_at = data.get('created_at')
        if isinstance(created_at, str):
            # Try parsing the string if not already in ISO format
            try:
                # Try some common formats, fallback to original
                created_at_dt = datetime.strptime(created_at, "%d-%m-%y-%H-%M-%S")
                created_at_iso = created_at_dt.isoformat()
            except ValueError:
                try:
                    # Maybe it's in another format that's parseable by fromisoformat
                    created_at_iso = datetime.fromisoformat(created_at).isoformat()
                except Exception:
                    # If can't parse, set to current UTC time as fallback
                    created_at_iso = datetime.utcnow().isoformat()
        elif isinstance(created_at, datetime):
            created_at_iso = created_at.isoformat()
        else:
            created_at_iso = datetime.utcnow().isoformat()

        insert_data = {
            "user_id": data['user_id'],
            "wp_url": data['wp_url'],
            "wp_token": data['wp_token'],
            "created_at": created_at_iso
        }
        res = self.client.table("wp_credentials").insert(insert_data).execute()
        return res.data

    def get_wp_credentials(self, user_id: str):
        """Ambil semua kredensial milik user"""
        res = self.client.table("wp_credentials").select("*").eq("user_id", user_id).execute()
        return res.data

    def update_wp_credential_by_user(self, user_id: str, wp_url: str = None, wp_token: str = None):
        """Update credential WP berdasarkan user id"""
        update_fields = {}
        if wp_url is not None:
            update_fields["wp_url"] = wp_url
        if wp_token is not None:
            update_fields["wp_token"] = wp_token
        if not update_fields:
            return None  # Nothing to update

        # Optionally, update 'updated_at' field if your schema has it
        # from datetime import datetime
        # update_fields["updated_at"] = datetime.utcnow().isoformat()

        try:
            res = self.client.table("wp_credentials").update(update_fields).eq("user_id", user_id).execute()
            return res
        except Exception as e:
            print(f"Update failed: {e}")
            return None


    # -------------------------
    # ARTICLES TABLE
    # -------------------------
    def insert_article(self, user_id: str, title: str, content: str, status="generated"):
        """Menyimpan artikel yang digenerate"""
        data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        }
        res = self.client.table("articles").insert(data).execute()
        return res.data

    def get_articles(self, user_id: str, status=None):
        """Ambil semua artikel milik user (bisa filter status)"""
        query = self.client.table("articles").select("*").eq("user_id", user_id)
        if status:
            query = query.eq("status", status)
        res = query.order("created_at", desc=True).execute()
        return res.data
    def token_generator(self, length=16):
        """
        Generate a token in the format: itretceh-day-mm-yy-hh-mm-ss
        """
        from datetime import datetime

        base = 'ITR-'
        now = datetime.now()
        date_part = now.strftime("%d%m%y%H%M%S")
        # Optionally add some random chars for entropy
        token = f"{base}{date_part}"
        return token