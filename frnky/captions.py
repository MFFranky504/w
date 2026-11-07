import re
from .config import CTAS, HASHTAGS, HANDLE

_CANON = {h.lower(): h for h in HASHTAGS}
_TAG = re.compile(r"#\w+")


def cta_for(index: int) -> str:
    return CTAS[index % len(CTAS)]


def normalize_hashtags(text: str) -> str:
    """#pixelart / #Pixelart / #PIXELART -> #PixelArt (solo las 4 oficiales)."""
    text = re.sub(r"#pixel[_ ]?art\b", "#PixelArt", text, flags=re.I)
    return _TAG.sub(lambda m: _CANON.get(m.group(0).lower(), m.group(0)), text)


def build_captions(hook: str, cta: str) -> dict:
    tags = " ".join(HASHTAGS)
    raw = {
        "instagram": f"{hook}\n\n{cta} 👇\n\nMás en @{HANDLE}\n{tags}",
        "tiktok": f"{hook} {cta}. @{HANDLE} {tags}",
        "youtube": f"{hook} | {cta}\n\n@{HANDLE}\n{tags}",
    }
    return {k: normalize_hashtags(v) for k, v in raw.items()}
