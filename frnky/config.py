"""Una sola fuente de verdad para bio, hashtags, CTAs y reglas de publicación."""

# Un solo nombre en todas las redes (antes: frnky66.ia, franky66ia y FRNKY66IA).
HANDLE = "frnky66.ia"
BIO = "Un video nuevo cada día para mandarle a tu bro"

# Bio por red: misma línea + dónde encontrar las otras redes.
PLATFORMS = {
    "instagram": "Instagram", "tiktok": "TikTok", "youtube": "YouTube",
}
BIOS = {
    k: f"{BIO}\n📲 También en " + " · ".join(v for kk, v in PLATFORMS.items() if kk != k) + f": @{HANDLE}"
    for k in PLATFORMS
}

# Siempre se escriben así y en este orden, para que cuenten como una sola etiqueta.
HASHTAGS = ["#MiBro", "#Humor", "#Comedia", "#PixelArt"]

# Se rotan en orden (video y caption usan el mismo).
CTAS = [
    "Etiqueta a tu bro que haría esto",
    "Mándaselo a tu bro",
    "¿Quién es tu bro?",
]
CTA_SECONDS = 2.5      # el CTA ocupa siempre los últimos segundos del video
HOOK_SECONDS = 2.0     # el conflicto debe estar en pantalla dentro de este tiempo

CATEGORIES = ["amor", "trabajo", "dinero", "amistad"]
NEW_CATEGORIES = ["dinero", "trabajo", "amor"]     # cada semana: 1 situación NUEVA de cada una (3 en total)
VARIANTS_PER_WEEK = 3
# Situaciones ganadoras (más vistas): se repiten con variaciones (ver "kind": "ganadora" en data/ideas.json).
WINNERS = ["los últimos hombres en la tierra", "el bro más fiel del mundo", "traición"]
POSTS_PER_DAY = (1, 2)

# Pesos para decidir qué categoría rinde mejor. Comentarios y compartidos pesan
# mucho más que likes porque ese es el problema actual de la cuenta.
WEIGHTS = {"likes": 1, "comments": 8, "shares": 10, "saves": 5, "followers": 25}
