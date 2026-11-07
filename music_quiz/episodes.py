"""One config per episode. Pick with EPISODE=p11 (default). Everything else (timeline, audio, video) is derived from this."""
import os

# ---- winners of Parte 8 (from the user's screenshots), kept for the p9 episode ----
# (handle, plataforma, pista (0 = no la indica), likes, horas desde el comentario). Transcrito de las capturas de la Parte 8.
WINNERS_P8 = [
 ("mmmaaaxiii","IG",1,5,8),("m4ry.npc","IG",1,14,10),("d3adcvp1d_zzz","IG",2,1,7),("chicocool789","IG",2,1,10),
 ("i_was_born_to_love_brian_may","IG",1,1,5),("pollo_thecreator","IG",0,1,7),("compapada","IG",0,1,7),("poll.o7816","IG",0,1,8),
 ("yoyo.mendez02","IG",0,1,8),("chikillodelascamelias","IG",2,1,9),("beni_ssj_goku","IG",0,1,6),("amytooor","IG",2,1,9),
 ("eliaadamian2011","IG",1,1,9),("g4po0_xd03","IG",0,1,6),("dylangabrielcruzcastano","IG",2,1,5),("xsantiagox66","IG",1,1,7),
 ("devx_.sk","IG",1,1,5),("gipsyy1414","IG",1,2,7),("juanjor117","IG",1,1,7),("nprss_yk22","IG",1,1,4),
 ("julia.coejo_1","IG",0,1,5),("diego._glzz","IG",0,1,6),("el_ciolita","IG",0,2,4),("va.lencia06","IG",1,2,10),
 ("jaritajeje","IG",0,1,7),("thi_agooxz","IG",0,1,9),("ernswt2","IG",0,2,6),("xolots_official","IG",1,1,10),
 ("diegosez.010","IG",0,1,5),("dieg.o021022","IG",0,1,7),("carlos._.1004k","IG",0,1,4),("kiike.ac.09","IG",0,1,4),
 ("_.missael98","IG",0,1,4),("je_suis_sam1917","IG",0,1,4),("alegre_changuito","IG",0,1,4),("jeff_the_land_shark124","IG",0,1,6),
 ("elwillmaf08","IG",2,1,4),("songomaro","IG",2,1,9),("grxan_tvr","IG",0,1,7),("demianancapi","IG",1,1,5),
 ("davichoo.pinedo3017","IG",0,1,10),("shoujizz","IG",1,1,10),("21ssanti","IG",3,1,10),("nehemias201602","IG",2,1,10),
 ("jesus_rch27","",0,0,0),
 ("Emilio","TT",0,1,8),("Osamu Dazai","TT",0,1,8),("Steve Santos","TT",0,1,8),
]

SPECIAL_P8 = {"va.lencia06": "1º EN ADIVINAR"}      # the channel replied "eres el primero en adivinarlo"

def _sort_rows(raw):
    """Order requested by the channel owner: pista (1,2,3, sin pista) -> más likes -> comentó antes (más horas)."""
    s = sorted(enumerate(raw), key=lambda e: ((e[1][2] if e[1][2] else 9), -e[1][3], -e[1][4], e[0]))
    return [r for _, r in s]

EPISODES = {
    # ------------------------------------------------------------------ Parte 11: Daft Punk
    "p11": dict(
        part=11, artist="Daft Punk", genre="electrónica", music="house", hook="b", next_part=12,
        hook_len=2.0, reveal=2.6, hook_scene="hook_sunset", outro_scene="paris", outro_sign=None,
        prev=dict(sprite="tyler", scene="travel", part=9, lines=("TYLER,", "THE CREATOR"), sub="LOS ÁNGELES, CALIFORNIA",
                  winners=[], winners_part=None, special={}),
        clues=[
            dict(n=1, diff="ULTRA DIFÍCIL", pts=5, chip="1978", scene="disco",
                 text="Su padre fue un compositor y productor de música disco: escribió «*Cuba*» en *1978* y «*D.I.S.C.O.*» en 1979."),
            dict(n=2, diff="MUY DIFÍCIL", pts=4, chip="1992", scene="press",
                 text="En *1992* tuvieron una banda de rock con un tercer amigo, que después se unió a la banda *Phoenix*."),
            dict(n=3, diff="DIFÍCIL", pts=3, chip="1994", scene="rave",
                 text="Su primer sencillo salió en *1994* en *Soma*, un sello escocés de techno, tras entregar una maqueta en un rave."),
            dict(n=4, diff="MEDIA", pts=2, chip="2006", scene="pyramid",
                 text="En *2006* tocaron en *Coachella* dentro de una pirámide de pantallas y luces LED."),
            dict(n=5, diff="FÁCIL", pts=1, chip="GRAMMY", scene="grammy",
                 text="En *2014* ganaron el Grammy a *Álbum del Año*, con un disco que incluía «*Get Lucky*» junto a *Pharrell*."),
        ]),
    # ------------------------------------------------------------------ Parte 9: Nas (ya publicado)
    "p9": dict(
        part=9, artist="Nas", genre="hip hop", music="boombap", hook="a", next_part=10,
        hook_len=3.0, reveal=3.4, outro_scene="brook", outro_sign="NUEVA YORK",
        prev=dict(sprite="snoop", scene="sunset", part=8, lines=("SNOOP", "DOGG"), sub="LONG BEACH, CALIFORNIA",
                  winners=_sort_rows(WINNERS_P8) + [], winners_part=8, special=SPECIAL_P8),
        clues=[
            dict(n=1, diff="MUY DIFÍCIL", pts=4, chip="1991", scene="block",
                 text="Su primera aparición en un disco fue en *1991*, como invitado en un tema del grupo *Main Source*."),
            dict(n=2, diff="DIFÍCIL", pts=3, chip="JAZZ", scene="jazz",
                 text="Su padre, *Olu Dara*, es músico de *jazz* y blues. Él creció en *Queensbridge*, Nueva York."),
            dict(n=3, diff="MEDIA", pts=2, chip="1994", scene="qb",
                 text="Su álbum debut, de *1994*, tiene solo *10 canciones* y es considerado una obra maestra del hip hop."),
            dict(n=4, diff="FÁCIL", pts=1, chip="ETHER", scene="battle",
                 text="Su guerra de rimas con *Jay-Z* dejó «*Ether*» en *2001*, una de las mejores canciones de ataque del rap."),
        ]),
}
# the Parte 8 winners list needs the extra rows added after Parte 8 (jesus_rch27)
EPISODES["p9"]["prev"]["winners"] = _sort_rows(WINNERS_P8)

def current():
    ep = dict(EPISODES[os.environ.get("EPISODE", "p11")])
    h = os.environ.get("HOOK")                       # A/B test of the first-2-seconds hook:  HOOK=a (old) | HOOK=b ("Solo el 1%...")
    if h in ("a", "b"): ep["hook"] = h; ep["hook_len"] = 3.0 if h == "a" else 2.0
    return ep
