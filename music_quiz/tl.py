# Shared timeline for video + audio (seconds). Everything is derived from the episode config (episodes.py).
# segments: 0 hook | 1 recap ("la respuesta de ayer") | 2 winners (optional) | 3..3+N-1 clues | outro
from episodes import current
EP = current()
FPS = 30
WIPE = 0.6
TW0, TWS = 1.4, 0.032                    # typewriter start (segment time) and sec/char
CLUES = EP["clues"]; NCL = len(CLUES)
PREV = EP["prev"]; WINNERS = PREV["winners"]; SPECIAL = PREV["special"]
HOOK_LEN = EP["hook_len"]; REVEAL = EP["reveal"]
S_HOOK, S_RECAP, S_WIN, S_C1 = 0, 1, 2, 3
S_OUT = S_C1 + NCL
ROW_H, WIN_SPEED, WIN_WH, WIN_START = 88, 270, 686, 0.8   # winners list (full-res px, px/s)
CLUE_LEN, LAST_CLUE_LEN = 7.5, 9.0                        # the easiest clue is last and gets a 3-2-1 countdown
RECAP_LEN = 9.0 if WINNERS else REVEAL + 3.6
PCOL_KEYS = (1, 2, 3, 0)

ROWS, _last, _rank = [], None, 0
for h, pl, pk, lk, hr in WINNERS:
    if pk != _last:
        ROWS.append(dict(kind="hdr", pk=pk)); _last = pk
    _rank += 1
    ROWS.append(dict(kind="row", rank=_rank, h=h, pl=pl, pk=pk, lk=lk))
WIN_SCROLL = max(0, len(ROWS) * ROW_H - WIN_WH) / WIN_SPEED
WIN_LEN = (WIN_START + WIN_SCROLL + 2.5) if WINNERS else 0.0

T = [0, HOOK_LEN, HOOK_LEN + RECAP_LEN]
T.append(T[2] + WIN_LEN)                                   # first clue
for i in range(NCL): T.append(T[-1] + (LAST_CLUE_LEN if i == NCL - 1 else CLUE_LEN))   # T[S_OUT] = outro start
END = T[S_OUT] + 7.0
BANNERS = {S_C1: "¿YA LO SABES? ¡COMÉNTALO!", S_C1 + 1: "¿TE SALIÓ? ¡ESCRÍBELO YA!"}
if NCL >= 3: BANNERS[S_C1 + NCL - 2] = "LA ÚLTIMA PISTA ES REGALADA"
BANNER_T = 5.4
def plain(s): return s.replace("*", "")
if __name__ == "__main__":
    print(EP["artist"], "clues", NCL, "winners", len(WINNERS), "T", [round(x, 1) for x in T], "END", round(END, 1))
