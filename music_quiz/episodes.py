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

# ---- winners of Parte 9 (Nas): only comments that say "Nas" (screenshots of IG, TikTok and YouTube, 8-nov-2026) ----
WINNERS_P9 = [
 ("chicocool789","IG",2,1,22),("annczyy__","IG",1,1,22),("mmmaaaxiii","IG",4,1,21),("va.lencia06","IG",3,1,22),
 ("brvjo.7","IG",2,1,21),("xanderrni","IG",2,1,21),("_alimjacob_","IG",1,1,8),("bastiano.wlr","IG",1,1,21),
 ("ricardox_c7","IG",2,1,21),("shoujizz","IG",1,1,3),("arisakatype99a","IG",3,1,11),("im_andrezzzes","IG",0,1,5),
 ("el_sebas84","IG",1,1,5),("devx_.sk","IG",1,1,0.3),("songomaro","IG",2,1,7),("pollo_bskt","IG",1,1,3),
 ("nataa.cug","IG",0,1,18),("a.vivanco__21","IG",1,1,14),("mosh.king2","IG",2,1,21),("_.missael98","IG",2,1,21),
 ("dieg.o021022","IG",3,1,20),("alexxnder_ybv","IG",1,1,22),("_jav_mendivil_","IG",1,1,4),
 ("Sergio","TT",0,3,21),("ŤĂĬĶ","TT",0,1,7),("fan de yiyis-enamorada","TT",0,0,7),
 ("raperonose","YT",0,1,12),("derekmp67","YT",0,1,13),
]
SPECIAL_P9 = {"Sergio": "1ER COMENTARIO"}                 # TikTok marked it "Primer comentario"

# ---- winners of Parte 10 (Tyler): comments that say "Tyler" (IG + TikTok screenshots, 9-nov-2026; transcribed by Gemini, checked by hand) ----
WINNERS_P10 = [
 ("chicocool789","IG",1,6,21),("pollo_thecreator","IG",1,3,19),("mosh.king2","IG",1,1,20),("cxml.mp3","IG",1,1,19),
 ("jaydx.5","IG",1,1,18),("1544c_lol","IG",1,1,18),("eyoklem","IG",1,1,18),("samuapont","IG",1,1,17),
 ("ludomzz_","IG",1,1,17),("_dx.gozz","IG",1,1,17),("marc_bno306","IG",1,1,14),
 ("dieg.o021022","IG",2,1,21),("ricardox_c7","IG",2,1,21),("alegre_changuito","IG",2,1,21),("ahmedcarmenateperez","IG",2,1,19),
 ("_mtosn","IG",2,1,19),("ssh_15_2011","IG",2,1,19),("oaxaca_187","IG",2,1,18),("alexxnder_ybv","IG",2,1,1),
 ("dylangabrielcruzcastano","IG",3,1,20),("diego._glzz","IG",3,1,20),("megalody34_ts_","IG",4,1,20),
 ("chris","TT",0,2,4),("Osamu Dazai","TT",0,1,4),
]
SPECIAL_P10 = {"Osamu Dazai": "1ER COMENTARIO"}

# ---- winners of Parte 11 (Queen): comments naming Queen or ANY member (Freddie, Mercury, Brian May...) — IG, TikTok, YouTube, 17-nov-2026; transcribed by Gemini, checked by hand ----
WINNERS_P11 = [
 ('armxxndo064_', 'IG', 1, 1, 96),
 ('mati09084', 'IG', 1, 1, 96),
 ('alejokirchheimer', 'IG', 1, 1, 96),
 ('ikmat2813', 'IG', 1, 1, 96),
 ('bolillotactico87', 'IG', 0, 1, 96),
 ('ianmoya.4', 'IG', 2, 1, 96),
 ('d3adcvp1d_zzz', 'IG', 1, 1, 96),
 ('diego._glzz', 'IG', 2, 1, 96),
 ('songomaro', 'IG', 1, 1, 24),
 ('3milio.x', 'IG', 0, 1, 96),
 ('gipsyy1414', 'IG', 1, 1, 96),
 ('_jav_mendivil_', 'IG', 1, 1, 96),
 ('personadelomasnormal2026', 'IG', 1, 1, 96),
 ('jeff_the_land_shark124', 'IG', 2, 1, 96),
 ('mosh.king2', 'IG', 1, 1, 96),
 ('caleb01516', 'IG', 0, 1, 96),
 ('gabrieljt2808', 'IG', 2, 1, 96),
 ('astromartin__', 'IG', 0, 1, 96),
 ('garzongodd', 'IG', 1, 2, 96),
 ('whatsername_1829', 'IG', 1, 1, 96),
 ('ricardox_c7', 'IG', 1, 1, 96),
 ('nixx3_09', 'IG', 1, 1, 96),
 ('m1435960', 'IG', 0, 1, 96),
 ('alwex_cqm', 'IG', 0, 1, 96),
 ('nake12312', 'IG', 1, 1, 96),
 ('i_am_not_maureen', 'IG', 2, 1, 96),
 ('zcx.bruh', 'IG', 1, 2, 96),
 ('FranciscoAntonioCruzGarcia-o7s', 'YT', 0, 2, 72),
 ('Betito.Santini', 'YT', 0, 1, 72),
 ('eden.vazquezzz', 'YT', 2, 2, 72),
 ('Osamu Dazai', 'TT', 0, 1, 72),
 ('dyf_r3nt', 'IG', 1, 1, 96),
 ('ernswt2', 'IG', 1, 1, 72),
 ('4nim4lkan1val', 'IG', 1, 1, 72),
 ('adalxx_gh', 'IG', 2, 1, 96),
 ('angell.5x_', 'IG', 0, 1, 72),
 ('luketa_paketa', 'IG', 0, 1, 96),
 ('fan_cdeg', 'IG', 1, 3, 96),
 ('r1ngo_mclennon', 'IG', 1, 1, 72),
 ('gg.37553', 'IG', 1, 1, 72),
 ('claudioandres_1710', 'IG', 0, 1, 72),
 ('_.missael98', 'IG', 0, 1, 96),
 ('im_andrezzzes', 'IG', 1, 1, 96),
 ('nosequeponer3596', 'IG', 0, 1, 72),
 ('bastian.reinaga.stratosg', 'IG', 1, 1, 72),
 ('pollo_bskt', 'IG', 1, 1, 72),
 ('movistar.707', 'IG', 1, 1, 72),
 ('aloisgross193', 'IG', 1, 1, 72),
 ('rom4n_drummer', 'IG', 2, 2, 72),
 ('matytesmo', 'IG', 1, 1, 72),
 ('pedrovs4614', 'IG', 1, 1, 72),
 ('ivxn._dump', 'IG', 1, 1, 72),
 ('richard.1034w', 'IG', 1, 1, 72),
 ('nott_balam2806', 'IG', 1, 3, 72),
 ('_saidens_', 'IG', 3, 1, 72),
 ('platanito_trailero', 'IG', 1, 14, 96),
 ('dylangabrielcruzcastano', 'IG', 1, 3, 96),
 ('luluna.tica', 'IG', 1, 1, 72),
 ('6._benjak_.10', 'IG', 1, 6, 96),
 ('deadof.ros3s', 'IG', 1, 1, 96),
 ('alexzgmx_', 'IG', 0, 1, 72),
 ('_canonizad0.211', 'IG', 2, 1, 96),
 ('justinvizcayaa', 'IG', 1, 1, 96),
 ('fer.nando_adr', 'IG', 1, 1, 72),
 ('compapada', 'IG', 4, 4, 96),
 ('julerodeluz', 'IG', 4, 2, 96),
 ('elbrotherx', 'IG', 1, 1, 96),
 ('d3g_420', 'IG', 4, 1, 96),
 ('nosoy._clark', 'IG', 1, 1, 72),
 ('alejandroo_ykz', 'IG', 1, 1, 72),
]
SPECIAL_P11 = {"Osamu Dazai": "1ER COMENTARIO"}

# ---- winners of Parte 12 (Nirvana): comments naming Nirvana or Kurt Cobain (IG, TikTok, YouTube; each user once) ----
import json as _json
_P12 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", "ganadores_p12_nirvana.json")
WINNERS_P12 = [(r["user"], r["plat"], r["pista"], r["likes"], r["horas"]) for r in _json.load(open(_P12))] if os.path.exists(_P12) else []

def _sort_rows(raw):
    """Order requested by the channel owner: pista (1,2,3, sin pista) -> más likes -> comentó antes (más horas)."""
    s = sorted(enumerate(raw), key=lambda e: ((e[1][2] if e[1][2] else 9), -e[1][3], -e[1][4], e[0]))
    return [r for _, r in s]

EPISODES = {
    # ------------------------------------------------------------------ Parte 11: Daft Punk
    "p11_dp": dict(
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
    # ------------------------------------------------------------------ Parte 13: AC/DC (rock, estilo GBA) — respuesta de ayer: Nirvana
    "p13": dict(
        part=13, artist="The Beatles", genre="rock", music="rock", bpm=140, win_speed=360, prog=[0, 0, 5, 7, 0, 0, 5, 7], hook="b", next_part=14, gba=True, gba_dir="parte13",
        hook_len=2.0, reveal=2.8, hook_scene="g13_hook", outro_scene="g13_outro", outro_sign=None,
        prev=dict(sprite="kurt_gba", scene="g_outro", part=12, lines=("NIRVANA",), sub="ABERDEEN · WASHINGTON", winners=[], winners_part=12, special={}),
        clues=[
            dict(n=1, diff="ULTRA DIFÍCIL", pts=4, chip="48 NOCHES", scene="g13_hamburg",
                 text="En *1960* tocaron *48 noches seguidas* en un club diminuto de *Hamburgo*, Alemania."),
            dict(n=2, diff="MUY DIFÍCIL", pts=3, chip="SKIFFLE", scene="g13_fete",
                 text="Empezaron como un grupo de *skiffle* con el nombre de una *escuela*. Dos miembros se conocieron en una *fiesta de iglesia*."),
            dict(n=3, diff="DIFÍCIL", pts=2, chip="RECHAZO", scene="g13_audition",
                 text="Una disquera los *rechazó* en *1962*; según la historia, dijeron que *los grupos de guitarras pasaban de moda*."),
            dict(n=4, diff="MEDIA", pts=1, chip="AZOTEA", scene="g13_rooftop",
                 text="Su último concierto público fue en la *azotea* de su oficina en *Londres*, en *1969*, hasta que llegó la policía."),
        ]),
    # ------------------------------------------------------------------ Parte 12: Nirvana (rock/grunge, estilo GBA) — respuesta de ayer: Queen
    "p12": dict(
        part=12, artist="Nirvana", genre="rock", music="rock", bpm=116, prog=[0, 3, 5, 3, 0, 3, 7, 5], hook="b", next_part=13, gba=True,
        hook_len=2.0, reveal=2.8, hook_scene="g_hook", outro_scene="g_outro", outro_sign=None,
        prev=dict(sprite="freddie_gba", scene="g_wembley", part=11, lines=("QUEEN",), sub="LONDRES · REINO UNIDO", winners=[], winners_part=11, special=SPECIAL_P11),
        clues=[
            dict(n=1, diff="ULTRA DIFÍCIL", pts=4, chip="NOMBRES", scene="g_garage",
                 text="Antes de su nombre definitivo se llamaron *Skid Row*, *Pen Cap Chew*, *Bliss* y *Ted Ed Fred*."),
            dict(n=2, diff="MUY DIFÍCIL", pts=3, chip="$606.17", scene="g_studio",
                 text="Su álbum debut, de *1989*, costó solo *606,17 dólares* y salió en el sello *Sub Pop*."),
            dict(n=3, diff="DIFÍCIL", pts=2, chip="1987", scene="g_aberdeen",
                 text="Se formaron en *1987* en *Aberdeen*, *Washington*."),
            dict(n=4, diff="MEDIA", pts=1, chip="1992", scene="g_pool",
                 text="En enero de *1992* su álbum con un *bebé nadando* en la portada sacó del #1 a *Dangerous* de Michael Jackson."),
        ]),
    # ------------------------------------------------------------------ Parte 11: Queen (rock) — respuesta de ayer: Tyler, The Creator
    "p11": dict(
        part=11, artist="Queen", genre="rock", music="rock", hook="b", next_part=12,
        hook_len=2.0, reveal=2.6, hook_scene="hook_sunset", outro_scene="grammy", outro_sign=None, diff_nb=5,
        prev=dict(sprite="tyler", scene="travel", part=10, lines=("TYLER,", "THE CREATOR"), sub="LOS ÁNGELES, CALIFORNIA", winners=[], winners_part=10, special=SPECIAL_P10),
        clues=[
            dict(n=1, diff="ULTRA DIFÍCIL", pts=4, chip="1963", scene="workshop",
                 text="Su guitarrista construyó su guitarra con su papá, a partir de *1963*, usando madera de una *repisa de chimenea* vieja."),
            dict(n=2, diff="MUY DIFÍCIL", pts=3, chip="ZANZÍBAR", scene="garden",
                 text="Su cantante nació en *Zanzíbar* y se llamaba *Farrokh Bulsara*. Entró en la banda *Smile* en *1970*."),
            dict(n=3, diff="DIFÍCIL", pts=2, chip="1985", scene="wembley",
                 text="En *1985* tocaron unos *20 minutos* en el estadio de *Wembley* en el *Live Aid*, y muchos dicen que robaron el show."),
            dict(n=4, diff="MEDIA", pts=1, chip="1975", scene="grammy",
                 text="Su álbum de *1975*, «*A Night at the Opera*», incluye «*Bohemian Rhapsody*»."),
        ]),
    # ------------------------------------------------------------------ Parte 10: MEGA DIFÍCIL (Tyler, The Creator)
    "p10": dict(
        part=10, artist="Tyler, The Creator", genre="hip hop", music="tyler", hook="c", next_part=11, mega=True,
        hook_len=2.0, reveal=2.6, hook_scene="danger", outro_scene="sunset", outro_sign=None, diff_nb=12,
        clue_len=5.5, last_clue_len=7.0, tw0=1.0, tws=0.024,                  # less time to answer
        banners={0: "¡NIVEL: MEGA DIFÍCIL!", 1: "SOLO PARA FANS DE VERDAD", 2: "NI LA ÚLTIMA ES FÁCIL"},
        prev=dict(sprite="nas2", scene="brook", part=9, lines=("NAS",), sub="QUEENSBRIDGE · NUEVA YORK", winners=[], winners_part=9, special=SPECIAL_P9),
        clues=[
            dict(n=1, diff="IMPOSIBLE", pts=4, chip="CAFÉ", scene="cafe",
                 text="Antes de la fama trabajó más de *dos años* en *Starbucks*... y en *FedEx* duró menos de dos semanas."),
            dict(n=2, diff="IMPOSIBLE", pts=3, chip="12", scene="school",
                 text="De niño pasó por *12 escuelas distintas* en 12 años, entre Los Ángeles y Sacramento."),
            dict(n=3, diff="ULTRA DIFÍCIL", pts=2, chip="2015", scene="airport",
                 text="En *2015* le prohibieron entrar al *Reino Unido* por letras de sus primeros discos. Volvió en *2019*."),
            dict(n=4, diff="ULTRA DIFÍCIL", pts=1, chip="SEUDÓNIMO", scene="set",
                 text="Dirige todos sus propios videos musicales, pero firma como director con un seudónimo: *Wolf Haley*."),
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
EPISODES["p10"]["prev"]["winners"] = _sort_rows(WINNERS_P9)
EPISODES["p11"]["prev"]["winners"] = _sort_rows(WINNERS_P10)
EPISODES["p12"]["prev"]["winners"] = _sort_rows(WINNERS_P11)
EPISODES["p13"]["prev"]["winners"] = _sort_rows(WINNERS_P12)

def current():
    ep = dict(EPISODES[os.environ.get("EPISODE", "p11")])
    h = os.environ.get("HOOK")                       # A/B test of the first-2-seconds hook:  HOOK=a (old) | HOOK=b ("Solo el 1%...")
    if h in ("a", "b"): ep["hook"] = h; ep["hook_len"] = 3.0 if h == "a" else 2.0
    return ep
