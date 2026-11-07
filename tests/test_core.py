from frnky.captions import normalize_hashtags, build_captions, cta_for
from frnky.config import CTAS, HASHTAGS, BIOS, HANDLE, BIO


def test_hashtags_unified():
    assert normalize_hashtags("#mibro #HUMOR #comedia #pixelart #Pixel_Art") == "#MiBro #Humor #Comedia #PixelArt #PixelArt"
    assert HASHTAGS == ["#MiBro", "#Humor", "#Comedia", "#PixelArt"]


def test_cta_rotates():
    assert [cta_for(i) for i in range(4)] == CTAS + [CTAS[0]]


def test_captions_have_cta_tags_and_handle():
    for c in build_captions("hook", CTAS[1]).values():
        assert CTAS[1] in c and all(h in c for h in HASHTAGS) and f"@{HANDLE}" in c


def test_bios_same_line_and_other_networks():
    assert set(BIOS) == {"instagram", "tiktok", "youtube"}
    for k, b in BIOS.items():
        assert b.startswith(BIO) and f"@{HANDLE}" in b and "También en" in b


def test_one_handle():
    assert HANDLE == "frnky66.ia"
