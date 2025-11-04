import requests
from pathlib import Path
import os 
from dotenv import load_dotenv 
import json 

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('TOKEN_ARTIKEL')

class artikelGenerator:
    def __init__(self):
        self._token = TOKEN
        self._password = ''

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
                    ),
                    "output_structure": {
                        "content": f'string (HTML dengan <div>) pada sebagian h2 berikan https://tse1.mm.bing.net/th?q={replaces} style="width: 50%; height: auto;"'
                    },
                    "variables": {
                        "topic": topik,
                        "tone": "informatif",
                        "length": "very short"
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

    def get_title(self, token_gemini, topik, prev_content):
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
                        "kategory":["kategori","kategori2"]
                    },
                    "variables": {
                        "topic": topik,
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