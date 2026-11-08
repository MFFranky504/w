import json,base64,urllib.request,sys
LINES=[
"Eres una mierda jugando, pendejo. Hasta el tutorial te mató.",
"Cómo jugar un videojuego. Primero, agarre el control. Con las manos, hijo de la chingada, no con las patas.",
"Ahora presione un botón. Uno. No los veinte al mismo tiempo, mono baboso.",
"Apunte. Dispare. ¿Por qué le disparó a su propio equipo, pedazo de imbécil?",
"Murió otra vez. Qué sorpresa, puto manco de mierda. Hasta los bots se burlan de usted.",
"Felicidades. Perdió contra un niño de nueve años. Ahora apague eso y váyase a la verga, culero.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.3,"speed":1.2}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/bIHbv24MWmeRgasZH58o/with-timestamps?output_format=mp3_44100_128",
 data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
r=json.load(urllib.request.urlopen(req))
open("assets7/voice.mp3","wb").write(base64.b64decode(r["audio_base64"]))
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
json.dump({"lines":LINES,"words":words},open("assets7/words.json","w"),ensure_ascii=False)
print(len(words),words[-1])
