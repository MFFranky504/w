import json,base64,urllib.request,sys
LINES=["¿Sigues pudriéndote en tu cuarto como un mueble con conciencia? Aprende a abrir una puerta, pendejo.", "TUTORIAL: Cómo abrir esa maldita puerta.", "Localice el pomo culero; si su cerebro logra coordinar el brazo, intente no arrancárselo en el proceso.", "Gire esa chingada pieza con la fuerza de alguien que intenta escapar de su propia mediocridad.", "Empuje con ganas; si ve un vacío existencial lloviendo teclados, es una mamada normal, no se queje.", "Felicidades, ya puede salir a cagarla; el mundo exterior lo acaba de bloquear por verga.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.3,"speed":1.2}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/bIHbv24MWmeRgasZH58o/with-timestamps?output_format=mp3_44100_128",
 data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
r=json.load(urllib.request.urlopen(req))
open("assets8/voice.mp3","wb").write(base64.b64decode(r["audio_base64"]))
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
json.dump({"lines":LINES,"words":words},open("assets8/words.json","w"),ensure_ascii=False)
print(len(words),words[-1])
