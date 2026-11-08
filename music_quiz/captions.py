"""Game-style captions + hashtags per platform.  usage: python3 captions.py [episode]   (writes captions/<episode>.md)
The artist name is NEVER in the caption: it is a quiz, and the answer goes in the next video ("La respuesta de ayer")."""
import os, sys
os.environ.setdefault("EPISODE", sys.argv[1] if len(sys.argv) > 1 else "p11")
from episodes import current
EP = current()
GENRE_TAG = {"hip hop": "#HipHop", "reggaetón": "#Reggaeton", "pop": "#Pop", "electrónica": "#Electronica"}
BASE = ["#MusicQuiz", "#AdivinaElArtista", GENRE_TAG.get(EP["genre"], "#HipHop"), "#Música"]
BODY = ((f"¿Quién es el artista? 🎤 MODO MEGA DIFÍCIL: {len(EP['clues'])} pistas y ninguna es fácil.\n" if EP.get("mega") else "¿Quién es el artista? 🎤\n") +
        "Responde en comentarios, mañana revelo la respuesta.\n"
        "Sígueme para ver la respuesta.")
def caption(platform):
    tags = BASE + (["#Shorts"] if platform == "youtube" else [])          # broad tag only on YouTube
    return BODY + "\n\n" + " ".join(tags)
YT_TITLE = f"¿Quién es el artista? {'MEGA DIFÍCIL · ' if EP.get('mega') else ''}Adivina con {len(EP['clues'])} pistas | Parte {EP['part']}"
out = [f"# Captions · Parte {EP['part']} ({EP['genre']})\n", "Instagram:\n```\n" + caption("instagram") + "\n```\n",
       "TikTok:\n```\n" + caption("tiktok") + "\n```\n", f"YouTube — título:\n```\n{YT_TITLE}\n```\nYouTube — descripción:\n```\n" + caption("youtube") + "\n```\n"]
os.makedirs("captions", exist_ok=True); path = f"captions/parte{EP['part']}_{EP['artist'].lower().replace(' ', '')}.md"
open(path, "w").write("\n".join(out)); print("\n".join(out)); print("->", path)
