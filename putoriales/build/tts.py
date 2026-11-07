import json,base64,urllib.request,sys
LINES=[
"Cómo sentarse. Sí, hijo de la chingada... sentarse. Alguien en este puto planeta lo necesita.",
"Primero, localice una silla. Esa cosa de cuatro patas que estorba en su cocina, pedazo de imbécil.",
"Doble las rodillas. Despacio. Las rodillas, cabrón... no el cuello. ¿Qué carajos le pasa a su cuello?",
"Ahora baje el culo. La gravedad hará el resto. Es lo único en este tutorial que sí trabaja.",
"Ah, la silla se fue. Qué sorpresa. Hasta los muebles lo odian.",
"Felicidades. Está sentado. En la nada, pero sentado. Ahora levántese, que ya me quiero ir a la verga.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.85,"similarity_boost":0.75,"style":0.0,"speed":1.0}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/nPczCjzI2devNBz1zQrb/with-timestamps?output_format=mp3_44100_128",
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
