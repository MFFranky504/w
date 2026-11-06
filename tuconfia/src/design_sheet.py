import sys; sys.path.insert(0,'.')
from PIL import Image, ImageDraw, ImageFont
import sprites as S
from sprites_b import battle2
from chars_anime import portrait
F=lambda s: ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', s)
BG=(52,110,112)
chars=[('STEPHEN KING','king',['plaid','teacher']),('TABITHA','tab',['cardigan','uniform']),('TÚ (espectador)','you',['hoodie'])]
RH=520
sheet=Image.new('RGB',(1700,60+RH*3),BG); d=ImageDraw.Draw(sheet)
for x,t in ((40,'1 · RPG  (planos MUY lejanos)'),(640,'2 · BATALLA  (planos medios / lejanos)'),(1330,'3 · PORTRAIT  (primer plano)')):
    d.text((x,14),t,font=F(26),fill=(255,236,150))
for r,(name,who,outs) in enumerate(chars):
    y0=60+r*RH
    d.text((40,y0+10),name,font=F(28),fill=(255,255,255))
    x=40
    for o in outs:
        for st in (0,1):
            im=S.rpg(who,o,step=st); big=im.resize((im.width*3,im.height*3),Image.NEAREST); sheet.paste(big,(x,y0+RH-60-big.height),big); x+=big.width-6
        x+=14
    x=640
    for o in outs[:2]:
        for pose in ('hold','stand'):
            if o in('teacher','uniform') and pose=='hold': continue
            b=battle2(who,pose,o); big=b.resize((b.width*3,b.height*3),Image.NEAREST); sheet.paste(big,(x,y0+RH-40-big.height),big); x+=big.width-30
        x+=30
    p=portrait(who,'n',outfit=outs[0]); p=p.crop((0,0,96,150)); big=p.resize((p.width*3,p.height*3),Image.NEAREST); sheet.paste(big,(1380,y0+RH-40-big.height),big)
sheet.save('../out/hoja_diseno.png')
