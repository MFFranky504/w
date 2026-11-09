import json,subprocess,sys
L=[("n1","adam","Diez naciones. Una cabaña sepultada en la nieve. Nadie sabe por qué están aquí."),
("n2","adam","Yo sí."),
("n3","adam","Bienvenidos a Escape: World Survival. Mis reglas son simples."),
("n4","adam","Cada país, una decisión. La audiencia decide por ustedes."),
("n5","adam","Cien de resistencia. Cada error cuesta recursos. Cero... es la eliminación."),
("n7","adam","Y la cabaña empeora. Seis grados. Cae tres, cada hora."),
("n8","adam","Un hacha. Un encendedor de una sola chispa. Un cuchillo. Un mapa. Cinco velas. Troncos húmedos. Tres leños secos."),
("n9","adam","Y una nota. Léanla con cuidado."),
("n9b","adam","El frío no se vence con fuerza. Lo que pesa, no te salvará. Lo que brilla poco, gástalo una sola vez, y donde más dure. El humo conoce la salida."),
("n10","adam","Tres caminos. A: la chimenea, con los leños secos. B: el muro, con el hacha. C: las cinco velas."),
("n11","adam","Cada país, una decisión. Escriban país y letra en los comentarios. Veinticuatro horas. Después... no habrá marcha atrás.")]
V={"adam":"pNInz6obpgDQGcFmaJgB"}
for k,v,t in L:
    b={"text":t,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.6,"similarity_boost":0.8,"style":0.35,"speed":1.0}}
    subprocess.run(["curl","-s","-m","90","-o",f"audio/{k}.mp3",f"https://api.elevenlabs.io/v1/text-to-speech/{V[v]}?output_format=mp3_44100_128","-H","xi-api-key: proxy-injected","-H","content-type: application/json","-d",json.dumps(b)])
