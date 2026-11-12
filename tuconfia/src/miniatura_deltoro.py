"""Miniatura del documental de Guillermo del Toro: primer plano preocupado, teléfono sonando y estatuilla al fondo; texto «72 DÍAS»."""
import os, sys
os.environ['TC_LAND'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import props as PR
import scenes15 as S
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = lambda s: ImageFont.truetype(f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff', s)
base = S.close('gdt', 'wow', (1, 0), 'cold')(2.0, 0).convert('RGBA')
img = base.crop((74, 10, 218, 91))                                      # encuadre cerrado sobre la cara: 160x90 -> 1280x720
gl = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
for r in range(26, 0, -2): gd.ellipse([126 - r, 46 - r, 126 + r, 46 + r], fill=(255, 200, 80, int(70 * (1 - r / 26))))
img.alpha_composite(gl); st = PR.statuette(52); img.alpha_composite(st, (112, 20))
ph = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
d.rectangle([4, 14, 36, 26], fill=(200, 30, 40)); d.rectangle([10, 6, 30, 14], fill=(220, 40, 50)); d.rectangle([16, 16, 24, 22], fill=(240, 230, 220))
for k in (1, 2, 3): d.arc([20 - 6 * k, 2 - 3 * k, 20 + 6 * k, 18 + 3 * k], 200, 340, fill=(255, 230, 140))

big = img.convert('RGB').resize((1280, 720), Image.NEAREST)
dr = ImageDraw.Draw(big); ft = FL(230)
for dx, dy, col in ((10, 10, (200, 20, 40)), (0, 0, (255, 236, 160))):
    dr.text((34 + dx, 10 + dy), '72', font=ft, fill=col, stroke_width=12, stroke_fill=(14, 10, 26) if col != (200, 20, 40) else col)
    dr.text((34 + dx, 250 + dy), 'DÍAS', font=FL(150), fill=col if col != (255, 236, 160) else (255, 255, 255), stroke_width=12, stroke_fill=(14, 10, 26) if col != (200, 20, 40) else col)
    dr.text((40 + dx, 450 + dy), 'SIN SU', font=FL(96), fill=col if col != (255, 236, 160) else (255, 220, 90), stroke_width=10, stroke_fill=(14, 10, 26) if col != (200, 20, 40) else col)
    dr.text((40 + dx, 560 + dy), 'PADRE', font=FL(96), fill=col if col != (255, 236, 160) else (255, 220, 90), stroke_width=10, stroke_fill=(14, 10, 26) if col != (200, 20, 40) else col)
big.save(f'{ROOT}/out/miniatura_deltoro.png'); print('ok')
