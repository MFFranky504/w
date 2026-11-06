# Shared timeline for video + audio (seconds)
# segments: 0 hook | 1 recap (artista anterior + ganadores) | 2..5 clues | 6 outro
T = [0, 3.0, 17.5, 25.0, 32.5, 40.0, 47.5]
END = 54.5
WIPE = 0.6
FPS = 30
TW0, TWS = 1.4, 0.032                   # typewriter start (segment time) and sec/char
REVEAL = 3.2                            # recap: reveal moment (segment time)
WIN0, WIN_SPEED, ROW_H = 5.2, 135, 96   # winners list start, scroll px/s, row height (full-res px)
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
BANNERS = {2: "¿YA LO SABES? ¡COMÉNTALO!", 3: "¿TE SALIÓ? ¡ESCRÍBELO YA!", 4: "LA ÚLTIMA PISTA ES REGALADA"}
BANNER_T = 5.4
# Handles taken from the user's screenshots (public comments, correct answers "Notorious B.I.G / Biggie")
WINNERS = [("jariestherperez", "♥ 12"), ("_jav_mendivil_", "♥ 3"), ("maxmotojr", "♥ 3"), ("andre_leon1216", "♥ 2"),
           ("diegosacas", "♥ 2"), ("1544c_lol", "PISTA 1"), ("fer.nando_adr", "PISTA 2"), ("xolots_official", ""),
           ("g4po0_xd03", ""), ("el_sebas84", ""), ("swt_sxmuel", ""), ("adalxx_gh", "")]
def plain(s): return s.replace("*", "")
