from frnky.captions import normalize_hashtags, build_captions, cta_for
from frnky.config import CTAS, HASHTAGS, BIOS, HANDLE, BIO
from frnky import tracker


def test_hashtags_lowercase_same_order():
    assert HASHTAGS == ["#mibro", "#humor", "#comedia", "#pixelart"]
    assert normalize_hashtags("#MiBro #HUMOR #Comedia #PixelArt #Pixel_Art") == "#mibro #humor #comedia #pixelart #pixelart"


def test_four_ctas_rotate():
    assert len(CTAS) == 4 and "Comenta qué haría tu bro" in CTAS
    assert [cta_for(i) for i in range(5)] == CTAS + [CTAS[0]]


def test_captions_per_network():
    c = build_captions("¿Qué pasaría si mi bro…?", CTAS[0], "fiel")
    assert "#Shorts" in c["youtube"] and "#Shorts" not in c["tiktok"]
    for v in c.values():
        assert all(h in v for h in HASHTAGS) and "#fidelidad" in v


def test_bios_same_line_and_crosslinks():
    for k, b in BIOS.items():
        assert b.startswith(BIO) and "También en" in b and f"@{HANDLE}" in b


def test_idea_bank_60_with_mix():
    ideas = tracker.ideas()
    assert len(ideas) == 60
    kinds = [i["kind"] for i in ideas]
    assert (kinds.count("ganadora"), kinds.count("nueva"), kinds.count("videojuegos")) == (36, 18, 6)
    assert all(i[k] for i in ideas for k in ("hook", "situation", "twist", "cta"))


def test_calendar_max_two_per_day():
    rows = tracker.calendario()
    from collections import Counter
    assert len(rows) == 20 and max(Counter(r["fecha"] for r in rows).values()) <= 2
