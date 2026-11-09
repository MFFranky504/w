"""Revisión visual con Gemini: python3 gemini_qa.py 'prompt' img1.png img2.png ... (usa la clave inyectada por el proxy)."""
import sys, json, base64, io, urllib.request
from PIL import Image
parts = [{"type": "text", "text": sys.argv[1]}]
for p in sys.argv[2:]:
    b = io.BytesIO(); Image.open(p).convert('RGB').resize((405, 720)).save(b, 'JPEG', quality=85)
    parts.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()}})
req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    json.dumps({"model": "gemini-3.1-flash-lite", "messages": [{"role": "user", "content": parts}], "max_tokens": 3000}).encode(),
    {"Authorization": "Bearer proxy-injected", "content-type": "application/json"})
print(json.load(urllib.request.urlopen(req, timeout=150))["choices"][0]["message"]["content"])
