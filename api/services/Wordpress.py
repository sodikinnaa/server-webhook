import requests

class wpConfig():
    def __init__(self):
        self._domain = ''
        self._token = ''

    def validasi_plugin(self, domain, token):
        url = f"https://{domain}/wp-json/buta-buku/v1/check-token?token={token}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}