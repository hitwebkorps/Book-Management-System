import requests

Google_API_KEY = "AIzaSyDPD165jbXiE-oKObdwIS8wjpnILzxgO-k"

def fetch_books_from_google(query: str):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={Google_API_KEY}"
    req = requests.get(url)

    if req.status_code != 200:
        return []

    data = req.json()
    items = data.get("items", [])
    return items
