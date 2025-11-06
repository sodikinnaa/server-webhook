import requests
import os 
from pathlib import Path
from dotenv import load_dotenv 
from services.SupabaseDb import SupabaseService
from services.Wordpress import wpConfig
from services.ArtikelGenerator import artikelGenerator
from services.Debug import debugConfig
import time 
import json 
from datetime import datetime

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
        self.debug_config = debugConfig()
        
    def token_generator(self, length=16):
        """
        Generate a token in the format: itretceh-day-mm-yy-hh-mm-ss
        """
        
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
        if "/test" in text:
            url = 'https://tse1.mm.bing.net/th?q=abah_gandu'
            path  = self.artikel_config.download_gambar(url)
            message = f"gambar {path} "
        elif "/post" in text:
            # Ekstrak kata-kata setelah /post (misal: "/post kuliah, tekno, omset, darknes")
            parts = original.split('/post', 1)
            user = self.db_config.get_user_by_wa(phone)
            id_user = user.get('id')
            credential = self.db_config.get_wp_credentials(user.get('id'))
            credential = credential[0]
            self.debug_config.lineMessage("Crendential")
            if not credential:
                message = 'anda belum menambahkan crendensial '
            elif user:
                if len(parts) > 1:
                 
                    lines = original.split('\n')
                    tags_str = ""
                    # Cari baris setelah /post (bisa berupa baris kosong baru data)
                    for idx, line in enumerate(lines):
                        if "/post" in line:
                            # search forward for the next non-empty line (could have empty lines for clarity)
                            for nextline in lines[idx+1:]:
                                if nextline.strip():
                                    tags_str = nextline.strip()
                                    break
                            if tags_str == "" and len(parts) > 1:
                                tags_str = parts[1].strip()  # fallback to /post xxx
                            break
                    if not tags_str and len(parts) > 1:
                        tags_str = parts[1].strip()
                    tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    self.debug_config.lineMessage(f"tags {tags_list}")
                    # Perulangkan keyword, generate artikel dan kirim satu persatu
                    max_loop = 5
                    for idx, tag in enumerate(tags_list):
                        if idx >= max_loop:
                            self.send_message(phone, f"Hanya diproses maksimal {max_loop} keyword.")
                            break
                        self.send_message(phone, f"Sedang membuat artikel dengan topik : *{tag}*")
                        
                        self.debug_config.lineMessage(f"Create artikel : {tag}")
                        konten = self.artikel_config.get_artikel(credential.get('gemini_token'), tag)
                        self.debug_config.lineMessage("Kontent Selesai dibuat")

                        content = konten.get('payload', {}).get('data', {}).get('content', [])
                        trim_content = ''
                        self.debug_config.lineMessage("Create title")
                        meta = self.artikel_config.get_meta(credential.get('gemini_token'), tag, trim_content)
                        self.debug_config.lineMessage("Title Selesai Dibuat")
                        title = meta.get('payload', {}).get('data', {}).get('title', '')
                        
                        if not content or not title:
                            self.send_message(phone, f"Proses gagal untuk keyword '{tag}': Server tidak dapat memproses!")
                            break

                        self.send_message(phone, f"Artikel dengan judul *{title}* telah dibuat")
                        url = f"https://tse1.mm.bing.net/th?q={title.replace(' ','_')}"
                        path_img = self.artikel_config.download_gambar(url)
                        self.debug_config.lineMessage(f"img path {path_img} ")
                        artikel = {
                            'kategori': meta.get('payload', {}).get('data', {}).get('kategory', []),
                            'title': title,
                            'meta_description': meta.get('payload', {}).get('data', {}).get('meta_description', ''),
                            'tags': meta.get('payload', {}).get('data', {}).get('tags', ''),
                            'content': content,
                            'thumbnail': path_img,
                            'post_date': datetime.now().strftime("%Y-%m-%d"),
                        }
                        response = self.debug_config.lineMessage(f"Posting Artikel {title}")
                        posting = self.wp_config.post_artikel(credential.get('wp_url'), credential.get('wp_token'), artikel)
                        print(posting)
                        self.debug_config.lineMessage("Selesai Posting")
                        # Kirim artikel per keyword
                        # Kirim hanya link artikel yang sudah berhasil diposting
                        self.debug_config.lineMessage(f"Debuging psting {posting}")
                        print(posting)

                        post_url = ""
                        if isinstance(posting, dict):
                            post_url = posting.get("post_url", "")
                        if post_url:
                            self.send_message(phone, f"Artikel untuk keyword '{tag}':\n{post_url}")
                        else:
                            self.send_message(phone, f"Artikel untuk keyword '{tag}':\n(Post url tidak ditemukan)")

                    message = f"Posting artikel telah dikirim untuk keyword:\n{tags_list}"
                else:
                    message = "Perintah /post tidak ditemukan atau tidak ada tags."
            else:
                message="silahkan lakukan registrasi "
        elif "/sc" in text:
            user = self.db_config.get_user_by_wa(phone)
            id_user = user.get('id')
            if user:
                lines = original.split('\n')
                domain = ""
                token = ""
                gemini = ""
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
                    elif line.lower().startswith("gemini"):
                        gemini = line.split(':', 1)[-1].strip()

                if not domain:
                    message = f"*Domain Gagal disimapan* G template :\n/sc\n \nDomain : .......\nToken: ...."
                else :
                    gemini_test = self.artikel_config.validase_gemini(gemini)

                    response = self.wp_config.validasi_plugin(domain,token)
                    if not gemini_test:
                        message = f"Token gemini yang anda inputkan tidak valid {gemini} response {gemini_test}"
                    elif response and isinstance(response, dict) and "error" in response:
                        message = f"*Gagal validasi plugin*\nPesan: *Token tidak sesuai*\n dan pastiken menggunakan template:\n/sc\n \nDomain : .......\nToken: ...."
                    else:
                        cs = self.db_config.get_wp_credentials(id_user)
                        print(f"crendesial info {cs} dari id {id_user}")
                        if not cs:
                            data = {
                                "user_id": id_user,
                                "wp_url": domain,
                                "wp_token": token,
                                "gemini_token":gemini
                            }
                            self.db_config.insert_wp_credential(data)
                            message = f"*Domain Berhasil disimpan* \nDomain : {domain}\nToken : {token}"
                        else:
                            message = f"Update Crendensial website"
                            update = self.db_config.update_wp_credential_by_user(user.get('id'), domain, token, gemini)
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
            message = "defaul message"

        return message
    