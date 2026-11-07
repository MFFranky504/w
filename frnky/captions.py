import re
from .config import CTAS, HASHTAGS, HANDLE, TOPIC_TAG

_CANON = {h.lower(): h for h in HASHTAGS}
_TAG = re.compile(r"#\w+")


def cta_for(index: int) -> str:
    return CTAS[index % len(CTAS)]


def normalize_hashtags(text: str) -> str:
    """Hashtags fijos siempre en minúsculas (#MiBro, #PIXELART, #Pixel_Art -> #mibro, #pixelart)."""
    text = re.sub(r"#pixel[_ ]?art\b", "#pixelart", text, flags=re.I)
    return _TAG.sub(lambda m: m.group(0).lower() if m.group(0).lower() in _CANON else m.group(0), text)


def build_captions(hook: str, cta: str, topic: str = "") -> dict:
    """Mismo gancho en las 3 redes, adaptado. Fijos + 1 variable por tema, siempre en el mismo orden."""
    extra = TOPIC_TAG.get(topic, "")
    tags = " ".join(HASHTAGS + ([extra] if extra else []))
    q = hook if hook.endswith("?") else hook
    raw = {
        "instagram": f"{q}\n\n{cta} 👇\n\nMás en @{HANDLE}\n{tags}",
        "tiktok": f"{q} {cta}. {tags}",
        "youtube": f"{q} | {cta}\n\n{tags} #Shorts",
    }
    return {k: normalize_hashtags(v) for k, v in raw.items()}
