import requests
from pathlib import Path
import os 
from dotenv import load_dotenv 
import json 
from datetime import datetime

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('TOKEN_ARTIKEL')

class artikelGenerator:
    def __init__(self):
        self._token = TOKEN
        self._password = ''

    
    def validase_gemini(self,apikey):
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={apikey}"
            headers = {
                "Accept": "application/json",
            }
            resp = requests.get(url, headers=headers, timeout=60)
            print("---------------------------- response gemini ---------------")
            print(resp.text)
        except Exception as e:
            return False
        if resp.status_code == 200:
            return True
        else:
            return False

    
    def get_artikel(self, token_gemini, topik):
        url = f'https://server-artikel.vercel.app/api/v1/generate?api_token={TOKEN}'
        try:
            replaces = "h2_spasi_replace_to_underscore"
            # Mengirim permintaan POST ke API dengan parameter sesuai contoh curl
            prompt_dict = {
                    "task": "generate_article_content",
                    "language": "id",
                    "instruction": (
                        "Tulis konten utama artikel dalam bahasa Indonesia, gaya blog edukatif dan ringan. "
                        "Sertakan contoh agar pembaca mudah memahami. Bungkus seluruh konten dalam tag <div> yang rapi. "
                        "Jangan buat title atau meta_description. Kembalikan hanya JSON valid dengan field 'content'."
                        "Berikan referensi dansumber terpercaya pada artikel sebanyak banyaknya yang diambil dari wikipedia yang langsung di emble hyperlink didalam artikel"
                    ),
                    "output_structure": {
                        "content": f'string (HTML dengan <div>) dibagiann bawah h2 berikan gambar https://tse1.mm.bing.net/th?q={replaces} style="width: 50%; height: auto;"'
                    },
                    "variables": {
                        "topic": topik,
                        "tone": "informatif",
                        "length": "very long"
                    }
                }
            data = {
                'promt': json.dumps(prompt_dict, ensure_ascii=False, indent=4),
                'token_gemini': token_gemini
            }
            # return data
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e: 
            return {"error ": str(e)}
    def download_gambar(self, url):
        """
        Download gambar dari url dan simpan di /tmp dengan nama file tahunbulanharijammenitdetik.png. Return path file lokal.
        """       
        

        print("-------------------------------img --------------------------------")

        # Buat nama file sesuai format tahunbulanharijammenitdetik.png
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        local_filename = f"{timestamp}.png"

        tmp_dir = "/tmp"
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        local_path = os.path.join(tmp_dir, local_filename)
        try:
            resp = requests.get(url, stream=True, timeout=30)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return local_path
        except Exception as e:
            print(f"Gagal download gambar: {e}")
            return None

    def get_meta(self, token_gemini, topik, prev_content):
        url = f'https://server-artikel.vercel.app/api/v1/generate?api_token={TOKEN}'
        try:
            replaces = "h2_spasi_replace_to_underscore"
            # Mengirim permintaan POST ke API dengan parameter sesuai contoh curl
            prompt_dict = {
                    "task": "generate_article_content",
                    "language": "id",
                    "instruction": (
                        "Buat title dan meta_description untuk artikel berdasarkan content yang sudah dibuat. Title harus SEO friendly dan menarik, meta_description ringkas dan jelas. Kembalikan hanya JSON valid dengan field 'title' dan 'meta_description' serta 'category'."
                    ),
                    "output_structure": {
                        "title": "string",
                        "meta_description": "string",
                        "kategory":"kategori1, kategori2, kategori3",
                        "tags":"tag1, tag2, tag3"
                    },
                    "variables": {
                        "topic": topik,
                        "length": "super very short 6 words",
                        "previous_content": prev_content
                    }
                }
            data = {
                'promt': json.dumps(prompt_dict, ensure_ascii=False, indent=4),
                'token_gemini': token_gemini
            }
            # return data
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e: 
            return {"error ": str(e)}