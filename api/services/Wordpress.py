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

            # INSERT_YOUR_CODE
    def create_post(self, domain, token, post):       
        url = f"https://{domain}/wp-json/buta-buku/v1/create-post?token={token}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Siapkan form-data
        # Gunakan 'files' argument untuk form-encoded multipart jika ada file
        data = {
            'title': post.get('title', ''),
            'content': post.get('content', ''),
            'post_type': 'post',
            'excerpt': post.get('meta_description', ''),
            'categories': post.get('kategori', ''),
            'tags': post.get('tags', ''),
            'post_date': post.get('post_date', ''),
            'status': post.get('status', 'publish')
        }
        
        files = {}
        # Jika featured_image adalah path file lokal
        if post.get('featured_image') and isinstance(post.get('featured_image'), str) and not post.get('featured_image').startswith(('http://', 'https://')):
            try:
                files['featured_image'] = open(post['featured_image'], 'rb')
            except Exception:
                pass
        else:
            # Dukung kirim uri/cloud path, atau lewat string/URL (langsung assign ke form-data)
            if post.get('featured_image'):
                data['featured_image'] = post['featured_image']

        try:
            # Kirim sebagai multipart/form-data
            response = requests.post(url, data=data, files=files if files else None, timeout=30)
            if files:
                files['featured_image'].close()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


            # INSERT_YOUR_CODE
    def post_artikel(self, domain, token, content):
        """
        Method to create a post based on the provided curl instruction.
        This demonstrates how to map the multipart/form-data curl request to Python requests.
        """
        url = f"https://{domain}/wp-json/buta-buku/v1/create-post?token={token}"
        # Multipart form-data fields, copy from curl (content is multiline HTML)
        data = {
            'title': content['title'],
            'content':content['content'],
            'post_type': 'post',
            'excerpt': content['meta_description'],
            'tags': content['tags'],
            'category':content['kategori'],
            'post_date': content['post_date'],
            'status': 'publish'
        }
        # We need to mock the featured_image as a file. In the curl, the path is "postman-cloud://..."
        # For demo purposes, we can just submit the field as a string unless you have file at /tmp/sample.png
        files = {}
        # If you have the file locally, replace the next line with file open logic
        files['featured_image'] = open(content['thumbnail'], 'rb')
        # data['featured_image'] = content['thumbnail']

        try:
            response = requests.post(url, data=data, files=files if files else None, timeout=30)
            if files:
                # Close open file if used
                files['featured_image'].close()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}




