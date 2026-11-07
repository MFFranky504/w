import json,base64,urllib.request,sys
LINES=[
"Cómo sentarse. Sí, pinche chingada... sentarse. Alguien en este puto planeta lo necesita, y seguro es un pendejo.",
"Primero, localice una silla. Esa mamada de cuatro patas que estorba en su pinche cocina, pedazo de imbécil.",
"Doble las rodillas. Despacio, wey. Las rodillas, cabrón... no el cuello. ¿Qué carajos le pasa a su puto cuello?",
"Ahora baje el culo. La gravedad hará el resto, hijo de puta. Es lo único en este pinche tutorial que sí trabaja.",
"Ah, la silla se fue. Qué sorpresa. Hasta los muebles lo odian, culero.",
"Felicidades, pendejo. Está sentado. En la nada, pero sentado. Ahora levántese, que ya me quiero ir a la verga.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.35,"similarity_boost":0.75,"style":0.55,"speed":1.15}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ/with-timestamps?output_format=mp3_44100_128",
 data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
r=json.load(urllib.request.urlopen(req))
open("assets/voice.mp3","wb").write(base64.b64decode(r["audio_base64"]))
a=r["alignment"]
# words
words=[];cur="";st=None
for c,s,e in zip(a["characters"],a["character_start_times_seconds"],a["character_end_times_seconds"]):
    if c.isspace():
        if cur: words.append([cur,st,pe]);cur="";st=None
    else:
        if st is None: st=s
        cur+=c
    pe=e
if cur: words.append([cur,st,pe])
json.dump({"lines":LINES,"words":words},open("assets/words.json","w"),ensure_ascii=False)
print(len(words),words[-1])

import re
norm=lambda x:re.sub(r"[^a-záéíóúñü]","",x.lower())
A=[(0,'cómo'),(2.37,'chingada'),(7.5,'primero'),(8.65,'silla'),(12.97,'imbécil'),(14.07,'doble'),(18.88,'cuello'),(22.73,'culo'),(27.31,'trabaja'),(28.38,'ah'),(29.19,'fue'),(30.11,'sorpresa'),(31.15,'hasta'),(33.06,'felicidades'),(35.99,'nada'),(37.94,'levántese'),(39.85,'verga')]
warp=[]
for old,w in A:
    for x in words:
        if norm(x[0])==norm(w): warp.append([old,x[1]]);break
    else: raise SystemExit('anchor missing '+w)
end=words[-1][2]
warp.append([40.5,end])
json.dump({"warp":warp,"end":end},open("assets/warp.json","w"))
print(warp)
