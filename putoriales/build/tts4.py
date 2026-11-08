import json,base64,urllib.request,sys
LINES=[
"Llevas dos días en la cama, pendejo. Hasta tu barba se levantó antes que tú.",
"Cómo levantarse. Primero, abra los ojos. Sí, los dos, cabrón.",
"Ahora saque una pierna de la cama. Una. Despacio. No se quede viendo el techo, hijo de puta.",
"Siéntese. Sí, en la cama. Ya aprendió a sentarse, qué milagro.",
"Ahora póngase de pie. Ah, la cama no lo suelta. Qué pinche cariñosa.",
"Felicidades. Se levantó. Ahora regrese a dormir, culero, que son las tres de la mañana.",
]
text=" ".join(LINES)
body={"text":text,"model_id":"eleven_multilingual_v2","language_code":"es",
 "voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.3,"speed":1.2}}
req=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/bIHbv24MWmeRgasZH58o/with-timestamps?output_format=mp3_44100_128",
 data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
r=json.load(urllib.request.urlopen(req))
open("assets4/voice.mp3","wb").write(base64.b64decode(r["audio_base64"]))
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
json.dump({"lines":LINES,"words":words},open("assets4/words.json","w"),ensure_ascii=False)
print(len(words),words[-1])
