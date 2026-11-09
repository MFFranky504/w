import json,subprocess,sys
L=[("n1","adam","Diez naciones. Una cabaña sepultada en la nieve. Nadie sabe por qué están aquí."),
("n2","adam","Yo sí."),
("d1","cal","Tenemos que hablar. Ahora."),
("d2","harry","¡Aquí se viene a pelear!"),
("d3","bill","Ya no queda nada por hacer..."),
("n3","adam","Bienvenidos a Escape: World Survival. Mis reglas son simples."),
("n4","adam","Cada país tiene una sola decisión. La audiencia decide por ustedes."),
("n5","adam","Cada uno empieza con cien de resistencia. Cada error les costará recursos. Llegar a cero... es la eliminación."),
("n6","adam","Y la habitación empeora con cada hora."),
("n7","adam","El termómetro marca seis grados. Cae tres, cada hora."),
("n8","adam","Un hacha. Un encendedor con una sola chispa. Un cuchillo. Un mapa. Cinco velas. Troncos húmedos. Tres leños secos."),
("n9","adam","Y una nota. Léanla con cuidado."),
("n9b","adam","El frío no se vence con fuerza. Lo que pesa, no te salvará. Lo que brilla poco, gástalo una sola vez, y donde más dure. El humo conoce la salida."),
("n10","adam","Tienen tres caminos. A: encender la chimenea con los leños secos. B: romper el muro con el hacha. C: encender las cinco velas."),
("n11","adam","Cada país tiene una decisión. Escriban el país y la letra en los comentarios. Tienen veinticuatro horas. Después... no habrá marcha atrás.")]
V={"adam":"pNInz6obpgDQGcFmaJgB","cal":"N2lVS1w4EtoT3dr4eOWO","harry":"SOYHLrjzK2X1ezoPC6cr","bill":"pqHfZKP75CvOlQylNhV4"}
for k,v,t in L:
    b={"text":t,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.6,"similarity_boost":0.8,"style":0.35,"speed":0.9 if v=="adam" else 1.0}}
    subprocess.run(["curl","-s","-m","90","-o",f"audio/{k}.mp3",f"https://api.elevenlabs.io/v1/text-to-speech/{V[v]}?output_format=mp3_44100_128","-H","xi-api-key: proxy-injected","-H","content-type: application/json","-d",json.dumps(b)])
def sfx(n,t,d):
    subprocess.run(["curl","-s","-m","90","-o",f"audio/{n}.mp3","https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128","-H","xi-api-key: proxy-injected","-H","content-type: application/json","-d",json.dumps({"text":t,"duration_seconds":d})])
sfx("wind","howling icy wind outside a wooden cabin, low rumble, creaking timbers, dark horror ambience",15)
sfx("boom","deep cinematic sub bass impact hit with dark reverb tail",4)
sfx("creak","slow eerie wooden door creak and metal groan, horror",4)
