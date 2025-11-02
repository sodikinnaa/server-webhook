import requests
import os 
from pathlib import Path
from dotenv import load_dotenv 
from services.SupabaseDb import SupabaseService
import time 
import json 

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv("WUZAPI_BASE_URL")
class WhatsappSender:
    def __init__(self,):
        self._base_url = BASE_URL
        self._token = os.getenv("WUZAPI_TOKEN")
        self.db_config = SupabaseService()
        
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

    def send_message(self, phone_number, message):
        url = f"{self._base_url}/chat/send/text"

        headers = {
            "accept": "applicatin/json",
            "Content-Type": "application/json",
            "token": self._token
        }

        data = {
            "Phone": phone_number, 
            "Body": message
        }

        response = requests.post(url, headers=headers, json=data)

        return response.json() if response.status_code == 200 else None

    def message_to_reply(self, text, original, phone):
        if text.startswith("/sc"):
            user = self.db_config.get_user_by_wa(phone)
            if user:
                lines = original.split('\n')
                domain = ""
                token = ""
                for line in lines:
                    if line.lower().startswith("domain"):
                        # Ambil setelah tanda ':' dan hapus spasi
                        domain = line.split(':', 1)[-1].strip()
                        # Hapus prefix http:// atau https:// jika ada
                        if domain.startswith("http://"):
                            domain = domain[len("http://"):]
                        elif domain.startswith("https://"):
                            domain = domain[len("https://"):]
                        # Hapus tanda '/' di akhir jika ada
                        if domain.endswith("/"):
                            domain = domain[:-1]
                    elif line.lower().startswith("token"):
                        token = line.split(':', 1)[-1].strip()

                        
                message = f"Domain disimpan: {domain}\nToken disimpan: {token}"

            else :
                message = "Anda balum terdaftar silahkan mendaftar dengan mengirimkan pesan daftar."
        elif "login" in text:
            user = self.db_config.get_user_by_wa(phone)
            if user:
                message = f"""Terdaftar dengan data {user.get('token')}"""
            else:
                message = "Anda balum terdaftar silahkan mendaftar dengan mengirimkan pesan daftar."
        elif "register" in text or "daftar" in text:
            data = self.db_config.get_user_by_wa(phone)
            if data:
                token = data.get('token')
                message = f"Anda sudah terdaftar silahkan gunakan token anda"
                self.send_message(phone, token)
            else:
                token = self.db_config.token_generator()
                token = f"{token}"
                self.db_config.insert_user(phone, token)
                self.send_message(phone, token)
                message = f"Terimakasih sudah mendaftar silahkan gunakan token di atas untuk proses penyimpanan data dan crendensial untuk akun anda."
        else:
            message ="defaul message"

        return message
    