import json
import os

URLS_FILE = "storage/urls.json"

def load_urls():
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"Principal": {"url": "http://localhost:8501", "max_cupos": 100}}

def save_urls(urls):
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)