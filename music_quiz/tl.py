# Shared timeline for video + audio (seconds)
T = [0, 3.8, 12.4, 21.0, 29.6, 38.2]   # hook | clue1..4 | outro starts
END = 44.5
WIPE = 0.6
FPS = 30
TW0, TWS = 1.8, 0.04                    # typewriter start (segment time) and sec/char
CLUES = [
    dict(n=1, diff="MUY DIFÍCIL", pts=4, chip="¿APODO?",
         text="Su mamá le puso el *apodo* por un *personaje* de las *tiras cómicas*."),
    dict(n=2, diff="DIFÍCIL", pts=3, chip="1993",
         text="Su álbum debut, de *1993*, lo produjo *Dr. Dre* y debutó en el *número 1* de Billboard."),
    dict(n=3, diff="MEDIA", pts=2, chip="2004",
         text="En *2004* grabó «*Drop It Like It's Hot*» junto a *Pharrell Williams*."),
    dict(n=4, diff="FÁCIL", pts=1, chip="SUPER BOWL",
         text="Nació en *Long Beach*, California, y en *2022* tocó en el *Super Bowl* con *Dr. Dre* y *Eminem*."),
]
def plain(s): return s.replace("*", "")
