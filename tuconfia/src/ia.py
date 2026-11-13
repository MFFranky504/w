"""Equipo de IAs externas (claves inyectadas por el proxy del entorno). Uso: python3 ia.py <alias> "<prompt>" [imagen.png ...]
Cada alias tiene un papel; ver ROLES. Reintenta ante 429/502. Solo 'gemini' acepta imágenes.
En Cloudflare (plan gratis) solo responden gpt-oss y llama; DeepSeek, GLM-5.3 y Kimi dan 403."""
import sys, json, time, base64, io, urllib.request, urllib.error
CF = "https://api.cloudflare.com/client/v4/accounts/0c44d0b72948bf2a54d96ce7046aad8d/ai/v1/chat/completions"
P = {  # alias: (url, modelo, max_tokens)
    'gemini':   ("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "gemini-3.1-flash-lite", 6000),
    'gptoss':   (CF, "@cf/openai/gpt-oss-120b", 4000),
    'llama':    (CF, "@cf/meta/llama-3.3-70b-instruct-fp8-fast", 3000),
    'zai':      ("https://api.z.ai/api/paas/v4/chat/completions", "glm-4.5-flash", 3000),
    'minimax':  ("https://integrate.api.nvidia.com/v1/chat/completions", "minimaxai/minimax-m3.1-flash", 400),  # más tokens: 502
    'liquid':   ("https://openrouter.ai/api/v1/chat/completions", "liquid/lfm-2.5-2.6b:free", 1500),
    'groq':     ("https://api.groq.com/openai/v1/chat/completions", "openai/gpt-oss-20b", 3000),
    'qwen':     ("https://api.groq.com/openai/v1/chat/completions", "qwen/qwen3.8-27b", 3000),
    'kilo':     ("https://api.kilo.ai/api/gateway/chat/completions", "kilo-auto/free", 3000),
    'nemotron': ("https://router.requesty.ai/v1/chat/completions", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", 4000),
    'polli':    ("https://gen.pollinations.ai/v1/chat/completions", "deepseek", 3000),
}
ROLES = {'gemini': 'crítica visual y de guion (ve imágenes)', 'gptoss': 'abogado del diablo',
         'llama': 'historias, temas, ganchos y experto en YouTube', 'zai': 'segunda opinión corta',
         'minimax': 'respuestas muy cortas', 'liquid': 'respaldo', 'groq': 'texto rápido', 'qwen': 'texto, razonamiento', 'kilo': 'auto-router gratis', 'nemotron': 'razonamiento', 'polli': 'DeepSeek'}


def ask(alias, prompt, images=(), tries=5):
    url, model, mt = P[alias]
    content = prompt
    if images:
        from PIL import Image
        content = [{"type": "text", "text": prompt}]
        for p in images:
            b = io.BytesIO(); im = Image.open(p).convert('RGB'); im.thumbnail((960, 960)); im.save(b, 'JPEG', quality=85)
            content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()}})
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": content}], "max_tokens": mt}).encode()
    err = None
    for k in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, body, {"Authorization": "Bearer proxy-injected", "content-type": "application/json", "User-Agent": "curl/8.5.0"}), timeout=240)
            m = json.load(r)["choices"][0]["message"]
            return m.get("content") or m.get("reasoning_content") or ""
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:200]!r}"
            if e.code not in (429, 500, 502, 503): break
        except Exception as e:
            err = repr(e)[:200]
        time.sleep(20)
    raise RuntimeError(f"{alias} ({model}) falló: {err}")


if __name__ == '__main__':
    print(ask(sys.argv[1], sys.argv[2], sys.argv[3:]))
