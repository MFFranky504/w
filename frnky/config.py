"""Una sola fuente de verdad para bio, hashtags, CTAs y reglas de publicación."""

# Usuario común propuesto (hay que verificar que esté libre en las 3 redes). Hoy: @frnky66.ia (IG), @franky66ia (TikTok), @FRNKY66IA (YouTube).
HANDLE = "frnky66ia"
CURRENT_HANDLES = {"instagram": "frnky66.ia", "tiktok": "franky66ia", "youtube": "FRNKY66IA"}
BIO = "Un video nuevo cada día para mandarle a tu bro"
PLATFORMS = {"instagram": "Instagram", "tiktok": "TikTok", "youtube": "YouTube"}
# Bio igual en las 3 redes + enlaces cruzados (sustituye las URLs por las reales al publicar).
BIOS = {
    k: f"{BIO}\n📲 También en " + " · ".join(f"{v} @{HANDLE}" for kk, v in PLATFORMS.items() if kk != k)
    for k in PLATFORMS
}

# Fijos, en minúsculas y siempre en este orden; después va 1 hashtag variable por tema.
HASHTAGS = ["#mibro", "#humor", "#comedia", "#pixelart"]
TOPIC_TAG = {"ultimo-hombre": "#apocalipsis", "fiel": "#fidelidad", "traicion": "#traicion", "crush": "#crush",
             "proyectarse": "#amorpropio", "dinero": "#dinero", "trabajo": "#trabajo", "familia": "#familia",
             "amistad": "#amistad", "redes": "#redessociales", "videojuegos": "#gamer"}

# Se rotan en orden (video y caption usan el mismo). Se mide cuál genera más comentarios y compartidos.
CTAS = [
    "Etiqueta a tu bro que haría esto",
    "Mándaselo a tu bro",
    "¿Quién es tu bro?",
    "Comenta qué haría tu bro",
]
CTA_SECONDS = 2.5      # el CTA ocupa siempre los últimos segundos del video
HOOK_SECONDS = 2.0     # el conflicto debe estar en pantalla dentro de este tiempo

CATEGORIES = ["ultimo-hombre", "fiel", "traicion", "crush", "proyectarse", "dinero", "trabajo", "familia", "amistad", "redes", "videojuegos"]
NEW_CATEGORIES = ["dinero", "trabajo", "familia"]     # cada semana: 1 situación NUEVA de cada una (3 en total)
VARIANTS_PER_WEEK = 3
# Situaciones ganadoras (más vistas): se repiten con variaciones (ver "kind": "ganadora" en data/ideas.json).
WINNERS = ["los últimos hombres en la tierra", "el bro más fiel del mundo", "traición"]
POSTS_PER_DAY = (1, 2)

# Pesos para decidir qué categoría rinde mejor. Comentarios y compartidos pesan
# mucho más que likes porque ese es el problema actual de la cuenta.
WEIGHTS = {"likes": 1, "comments": 8, "shares": 10, "saves": 5, "followers": 25}

# --- Metas y reglas de decisión (línea base: 1-7 nov 2026, 14-15 videos por red) ---
BASELINE = {
    "youtube": {"seguidores": 20, "vistas_media": 816, "vistas_mediana": 890, "likes": 11},
    "tiktok": {"seguidores": 3, "vistas_media": 259, "likes": 12, "comentarios": 0, "compartidos": 0.3, "duracion_s": 54},
    "instagram": {"seguidores": 9, "likes": 34, "comentarios": 0.7},
}
GOALS_30D = {"mediana_vistas_x": 3, "top_vistas_x": 10, "comentarios_tiktok_por_video": 5, "seguidores_por_red": 100}
WIN_X, RETIRE_X, RETIRE_STREAK, WIN_VARIATIONS = 2.0, 0.5, 3, 3
SCHEDULE = {"main": "16:00", "secondary": "07:30", "instagram_test": "19:00"}   # hora México
DUR_RANGE_S = (20, 35)
