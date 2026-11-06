from frnky.captions import normalize_hashtags, build_captions, cta_for
from frnky.config import CTAS, HASHTAGS


def test_hashtags_unified():
    assert normalize_hashtags("#pixelart #PIXEL_ART #comedia #humor #mibro") == "#PixelArt #PixelArt #Comedia #Humor #MiBro"


def test_cta_rotates():
    assert [cta_for(i) for i in range(4)] == CTAS + [CTAS[0]]


def test_captions_have_cta_and_tags():
    for c in build_captions("hook", CTAS[1]).values():
        assert CTAS[1] in c and all(h in c for h in HASHTAGS)
