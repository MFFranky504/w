"""Una sola fuente de verdad para bio, hashtags, CTAs y reglas de publicación."""

BIO = "Un video nuevo cada día para mandarle a tu bro"
HANDLE = "@frnky66.ia"

# Siempre se escriben así y en este orden, para que cuenten como una sola etiqueta.
HASHTAGS = ["#PixelArt", "#Comedia", "#Humor", "#MiBro"]

# Se rotan en orden (video y caption usan el mismo).
CTAS = [
    "Etiqueta a tu bro que haría esto",
    "Mándaselo a tu bro",
    "¿Quién es tu bro?",
]
CTA_SECONDS = 2.5      # el CTA ocupa siempre los últimos segundos del video
HOOK_SECONDS = 2.0     # el conflicto debe estar en pantalla dentro de este tiempo

CATEGORIES = ["amor", "trabajo", "dinero", "amistad"]
VARIANTS_PER_WEEK = 3
POSTS_PER_DAY = (1, 2)

# Pesos para decidir qué categoría rinde mejor. Comentarios y compartidos pesan
# mucho más que likes porque ese es el problema actual de la cuenta.
WEIGHTS = {"likes": 1, "comments": 8, "shares": 10, "saves": 5, "followers": 25}
