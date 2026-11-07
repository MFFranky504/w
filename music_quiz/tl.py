# Shared timeline for video + audio (seconds) -- Parte 9 (artista: Nas)
# segments: 0 hook | 1 recap (artista anterior: Snoop Dogg) | 2 winners (parte 8) | 3..6 clues | 7 outro
FPS = 30
WIPE = 0.6
TW0, TWS = 1.4, 0.032                   # typewriter start (segment time) and sec/char
REVEAL = 3.4                            # recap: reveal moment (segment time)
S_HOOK, S_RECAP, S_WIN, S_C1, S_OUT = 0, 1, 2, 3, 7
ROW_H, WIN_SPEED, WIN_WH, WIN_START = 88, 190, 686, 0.8   # winners list (full-res px, px/s)

CLUES = [
    dict(n=1, diff="MUY DIFÍCIL", pts=4, chip="1991",
         text="Su primera aparición en un disco fue en *1991*, como invitado en un tema del grupo *Main Source*."),
    dict(n=2, diff="DIFÍCIL", pts=3, chip="JAZZ",
         text="Su padre, *Olu Dara*, es músico de *jazz* y blues. Él creció en *Queensbridge*, Nueva York."),
    dict(n=3, diff="MEDIA", pts=2, chip="1994",
         text="Su álbum debut, de *1994*, tiene solo *10 canciones* y es considerado una obra maestra del hip hop."),
    dict(n=4, diff="FÁCIL", pts=1, chip="ETHER",
         text="Su guerra de rimas con *Jay-Z* dejó «*Ether*» en *2001*, una de las mejores canciones de ataque del rap."),
]
BANNERS = {3: "¿YA LO SABES? ¡COMÉNTALO!", 4: "¿TE SALIÓ? ¡ESCRÍBELO YA!", 5: "LA ÚLTIMA PISTA ES REGALADA"}
BANNER_T = 5.4

# (handle, plataforma, pista (0 = no la indica), likes, horas desde el comentario). Transcrito de las capturas de la Parte 8.
RAW = [
 ("mmmaaaxiii","IG",1,5,8),("m4ry.npc","IG",1,14,10),("d3adcvp1d_zzz","IG",2,1,7),("chicocool789","IG",2,1,10),
 ("i_was_born_to_love_brian_may","IG",1,1,5),("pollo_thecreator","IG",0,1,7),("compapada","IG",0,1,7),("poll.o7816","IG",0,1,8),
 ("yoyo.mendez02","IG",0,1,8),("chikillodelascamelias","IG",2,1,9),("beni_ssj_goku","IG",0,1,6),("amytooor","IG",2,1,9),
 ("eliaadamian2011","IG",1,1,9),("g4po0_xd03","IG",0,1,6),("dylangabrielcruzcastano","IG",2,1,5),("xsantiagox66","IG",1,1,7),
 ("devx_.sk","IG",1,1,5),("gipsyy1414","IG",1,2,7),("juanjor117","IG",1,1,7),("nprss_yk22","IG",1,1,4),
 ("julia.coejo_1","IG",0,1,5),("diego._glzz","IG",0,1,6),("el_ciolita","IG",0,2,4),("va.lencia06","IG",0,2,10),
 ("jaritajeje","IG",0,1,7),("thi_agooxz","IG",0,1,9),("ernswt2","IG",0,2,6),("xolots_official","IG",0,1,10),
 ("diegosez.010","IG",0,1,5),("dieg.o021022","IG",0,1,7),("carlos._.1004k","IG",0,1,4),("kiike.ac.09","IG",0,1,4),
 ("_.missael98","IG",0,1,4),("je_suis_sam1917","IG",0,1,4),("alegre_changuito","IG",0,1,4),("jeff_the_land_shark124","IG",0,1,6),
 ("elwillmaf08","IG",2,1,4),("songomaro","IG",2,1,9),("grxan_tvr","IG",0,1,7),("demianancapi","IG",1,1,5),
 ("davichoo.pinedo3017","IG",0,1,10),("shoujizz","IG",1,1,10),("21ssanti","IG",3,1,10),("nehemias201602","IG",2,1,10),
 ("Emilio","TT",0,1,8),("Osamu Dazai","TT",0,1,8),("Steve Santos","TT",0,1,8),
]
SPECIAL = {"va.lencia06": "1º EN ADIVINAR"}      # la cuenta del canal le respondió "eres el primero en adivinarlo"
# Orden pedido: pista (1,2,3, sin pista) -> más likes -> comentó antes (más horas) ; empates: orden de aparición
_sorted = sorted(enumerate(RAW), key=lambda e: ((e[1][2] if e[1][2] else 9), -e[1][3], -e[1][4], e[0]))
WINNERS = [r for _, r in _sorted]
ROWS, _last, _rank = [], None, 0
for h, pl, pk, lk, hr in WINNERS:
    if pk != _last:
        ROWS.append(dict(kind="hdr", pk=pk)); _last = pk
    _rank += 1
    ROWS.append(dict(kind="row", rank=_rank, h=h, pl=pl, pk=pk, lk=lk))
WIN_SCROLL = max(0, len(ROWS) * ROW_H - WIN_WH) / WIN_SPEED
WIN_LEN = WIN_START + WIN_SCROLL + 2.5

# segment starts
T = [0, 3.0, 12.0]
T.append(T[2] + WIN_LEN)                 # first clue
for _ in range(4): T.append(T[-1] + 7.5)  # T[3..6]=clues, T[7]=outro
END = T[7] + 7.0
def plain(s): return s.replace("*", "")
if __name__ == "__main__":
    print(len(WINNERS), len(ROWS), "WIN_LEN", round(WIN_LEN, 1), "T", [round(x, 1) for x in T], "END", round(END, 1))
    for r in ROWS: print(r)
