import json,base64,urllib.request,sys
LINES=[
"¿Quieres ahorrar dinero? Primero muérete de hambre, pendejo.",
"Cómo ahorrar dinero. Deje de gastar. En todo. Hasta en comida, cabrón.",
"Ahora venda sus cosas. El sillón, la tele, hasta su dignidad. Ofrecen cincuenta centavos, qué generosos hijos de puta.",
"Apague la luz. Y el refri. La comida congelada ya está muerta, no se va a quejar.",
"Mire, ya juntó cien pesos. Felicidades. Lástima que se murió de hambre, puto.",
"Tranquilo. Su familia se los gastará en una semana, esos buitres hijos de la chingada.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.3,"speed":1.2}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/bIHbv24MWmeRgasZH58o/with-timestamps?output_format=mp3_44100_128",
 data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
r=json.load(urllib.request.urlopen(req))
open("assets5/voice.mp3","wb").write(base64.b64decode(r["audio_base64"]))
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
json.dump({"lines":LINES,"words":words},open("assets5/words.json","w"),ensure_ascii=False)
print(len(words),words[-1])
