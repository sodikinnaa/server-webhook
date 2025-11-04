import requests
import os 
from pathlib import Path
from dotenv import load_dotenv 
from services.SupabaseDb import SupabaseService
from services.Wordpress import wpConfig
from services.ArtikelGenerator import artikelGenerator
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
        self.wp_config = wpConfig()
        self.artikel_config = artikelGenerator()
        
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
        if "/post" in text:
            # Ekstrak kata-kata setelah /post (misal: "/post kuliah, tekno, omset, darknes")
            parts = original.split('/post', 1)
            if len(parts) > 1:
                # Ambil string setelah /post dan pecah menjadi list dengan separator koma
                tags_str = parts[1].strip()
                tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                
                # Perulangkan keyword, generate artikel dan kirim satu persatu
                for tag in tags_list:

                    konten = self.artikel_config.get_artikel(os.getenv('TOKEN_GEMINI'), tag)
                    # # Contoh penggunaan get_artikel, sesuaikan parameter jika diperlukan
                    # artikel_result = self.artikel_config.get_artikel(tag, None, tag)
                    # # Anggap artikel_result berisi dict dengan konten artikel
                    # if artikel_result and isinstance(artikel_result, dict):
                    #     konten = artikel_result.get('content') or str(artikel_result)
                    # else:
                    #     konten = "Gagal generate artikel."

                    # Kirim artikel per keyword
                    self.send_message(phone, f"Artikel untuk keyword '{tag}':\n{konten}")

                message = f"Posting artikel telah dikirim untuk keyword:\n{tags_list}"
            else:
                message = "Perintah /post tidak ditemukan atau tidak ada tags."
            
        elif "/sc" in text:
            user = self.db_config.get_user_by_wa(phone)
            id_user = user.get('id')
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

                if not domain:
                    message = f"*Domain Gagal disimapan* G template :\n/sc\n \nDomain : .......\nToken: ...."
                else :
                    response = self.wp_config.validasi_plugin(domain,token)
                    if response and isinstance(response, dict) and "error" in response:
                        message = f"*Gagal validasi plugin*\nPesan: *Token tidak sesuai*\n dan pastiken menggunakan template:\n/sc\n \nDomain : .......\nToken: ...."
                    else:
                        cs = self.db_config.get_wp_credentials(id_user)
                        print(f"crendesial info {cs} dari id {id_user}")
                        if not cs:
                            data = {
                                "user_id": id_user,
                                "wp_url": domain,
                                "wp_token": token
                            }
                            self.db_config.insert_wp_credential(data)
                            message = f"*Domain Berhasil disimpan* \nDomain : {domain}\nToken : {token}"
                        else:
                            message = f"Update cs"
                            update = self.db_config.update_wp_credential_by_user(user.get('id'), domain, token)
                            print(f"update info : {update}")
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
    