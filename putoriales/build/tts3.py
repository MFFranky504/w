import json,base64,urllib.request,sys
LINES=[
"Pareces un zombi con ojeras hasta el culo. Así se duerme, pendejo.",
"Cómo dormir ocho horas. Primero, acuéstese en la cama. Ese mueble blandito que ignora desde hace años, cabrón.",
"Ahora cierre los ojos. Su cerebro empezará a recordar todas las pendejadas que hizo desde el dos mil nueve. Disfrútelo.",
"Mejor cuente borregos. Uno... dos... tres... ¿Por qué chingados el cuarto lo está mirando así?",
"Ah, valió madre. Ya se pusieron violentos, esos hijos de puta.",
"Felicidades. Durmió ocho segundos. Ahora levántese y váyase a trabajar, culero.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.3,"speed":1.2}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/bIHbv24MWmeRgasZH58o/with-timestamps?output_format=mp3_44100_128",
 data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
r=json.load(urllib.request.urlopen(req))
open("assets3/voice.mp3","wb").write(base64.b64decode(r["audio_base64"]))
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
json.dump({"lines":LINES,"words":words},open("assets3/words.json","w"),ensure_ascii=False)
print(len(words),words[-1])
