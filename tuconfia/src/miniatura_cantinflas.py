"""Miniatura del video largo de Cantinflas: primer plano preocupado bajo el foco de la carpa, ojos del público; texto «SE QUEDÓ MUDO»."""
import os, sys
os.environ['TC_LAND'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import scenes18 as S
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = lambda s: ImageFont.truetype(f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff', s)
c = S.cv(); S.carpa_inside(c, 2.0); c.light(236, 70, 70, 70, (255, 230, 180), .5)
S.face(c, 'cant_y', 'worry', 1.0, x=236, sc=1.75, bob=False)
for i in range(3): c.R(270 + i * 4, 76 + i * 12, 2, 4, (190, 230, 255))        # sudor
S.crowd_front(c, 2.0, y=190, eyes=True, seed=5)
img = S.fin(c, 'day', (1.0, .96, 1.0), .5).convert('RGB').resize((1280, 720), Image.NEAREST)
dr = ImageDraw.Draw(img)
for dx, dy, col in ((9, 9, (200, 20, 60)), (0, 0, None)):
    dr.text((40 + dx, 60 + dy), 'SE QUEDÓ', font=FL(120), fill=col or (255, 255, 255), stroke_width=11, stroke_fill=col or (14, 10, 26))
    dr.text((40 + dx, 210 + dy), 'MUDO...', font=FL(150), fill=col or (255, 216, 74), stroke_width=12, stroke_fill=col or (14, 10, 26))
    dr.text((44 + dx, 420 + dy), 'Y SE VOLVIÓ', font=FL(70), fill=col or (255, 255, 255), stroke_width=8, stroke_fill=col or (14, 10, 26))
    dr.text((44 + dx, 510 + dy), 'UNA PALABRA', font=FL(70), fill=col or (255, 216, 74), stroke_width=8, stroke_fill=col or (14, 10, 26))
img.save(f'{ROOT}/out/miniatura_cantinflas_largo.png'); print('ok')
