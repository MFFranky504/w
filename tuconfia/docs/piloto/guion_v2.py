"""Guion final del piloto (síntesis del director a partir de los borradores de Gemini, llama y gpt-oss y de los hechos contrastados).
Cada beat: (emoción, narración). Genera script_deltoro.json."""
import json, re
from num2words import num2words
G = [
 ("Cold open", [
  ("bold", "Los monstruos de verdad no estaban en sus películas."),
  ("softly", "Guillermo del Toro llevaba años dibujándolos. Vampiros, insectos, fantasmas. Con esos sabía qué hacer."),
  ("tense", "Pero a finales de los noventa sonó el teléfono. Era una llamada desde Guadalajara."),
  ("tense", "Para entonces ya había pasado por lo que él mismo llama su peor experiencia haciendo cine."),
  ("tense", "Y todavía le faltaba quedarse sin dos de los proyectos más grandes de su carrera."),
  ("hopeful", "Aun así, años después, subió al escenario de los Óscar."),
  ("bold", "Esta es la historia de cómo se llega de esa llamada... a ese escenario."),
 ]),
 ("El niño de las pesadillas", [
  ("warmly", "Guadalajara, México, 1964. Ahí nace Guillermo del Toro."),
  ("softly", "Crece en un hogar católico estricto. Y pasa mucho tiempo con su abuela, una mujer muy devota."),
  ("softly", "Él mismo se ha descrito como un niño solitario... con pesadillas muy vívidas."),
  ("hopeful", "Con los años, esos monstruos se vuelven su oficio."),
  ("warmly", "De joven aprende maquillaje de efectos especiales. Látex, pintura, prótesis."),
  ("bold", "Y en su propia ciudad funda una empresa de efectos: Necropia."),
  ("softly", "Hasta ahí, los monstruos eran para las películas de otros."),
  ("tense", "La pregunta era simple: ¿podía un maquillador de Guadalajara dirigir su propia película?"),
 ]),
 ("Cronos", [
  ("bold", "La respuesta se llama Cronos."),
  ("softly", "Una historia de vampiros tan extraña que casi nadie quería financiarla."),
  ("tense", "Costaba unos 2 millones de dólares. Y él era un director sin experiencia."),
  ("sad", "El dinero no alcanzaba. Según ha contado, hipotecó su casa... y vendió su coche."),
  ("tense", "Lo apostó todo a una sola película."),
  ("excited", "En 1993, Cronos se estrena. Y la crítica la celebra."),
  ("hopeful", "De pronto, el maquillador de Guadalajara es un director al que hay que seguir."),
  ("tense", "Y entonces llama Hollywood. Ahí empieza el problema."),
 ]),
 ("Mimic", [
  ("bold", "1997. Su primera película en Hollywood se llama Mimic."),
  ("softly", "Más dinero, más equipo, más gente opinando. La producen los hermanos Weinstein."),
  ("tense", "Y muy pronto empieza la pelea: quién decide cómo es la película."),
  ("sad", "Del Toro ha dicho que fue su peor experiencia haciendo cine."),
  ("tense", "Tan mala, que tomó una decisión. Sus historias más oscuras y personales... no volvería a intentarlas dentro de Hollywood."),
  ("sad", "Había llegado a donde quería. Y ahí no podía hacer lo que quería."),
  ("softly", "Él mismo ha dicho que Mimic fue peor que lo que vino después."),
  ("tense", "Y lo que vino después... fue el teléfono."),
 ]),
 ("La llamada", [
  ("tense", "La llamada llega desde Guadalajara. Han secuestrado a su padre, Federico del Toro."),
  ("sad", "Aquí no hay guion. No hay maquillaje. No hay un monstruo que se apague al terminar el día."),
  ("tense", "Pasa un día. Pasa una semana. Pasa un mes."),
  ("hopeful", "En medio de eso aparece un amigo: el director James Cameron."),
  ("warmly", "Cameron le da dinero para contratar a un negociador profesional."),
  ("softly", "El rescate lo paga la familia. Y tiempo después, le devuelven a Cameron cada dólar."),
  ("tense", "El secuestro dura 72 días."),
  ("warmly", "Y termina. Federico del Toro vuelve a casa. Con vida."),
  ("softly", "Varios de los responsables fueron detenidos. Otros, no."),
  ("sad", "Después de eso, Del Toro toma otra decisión. Se va de México con su familia."),
  ("tense", "Sin país. Y sin querer volver al Hollywood de Mimic. ¿Dónde iba a hacer sus películas?"),
 ]),
 ("El laberinto", [
  ("hopeful", "La respuesta estaba al otro lado del océano. En España."),
  ("warmly", "En 2001 filma ahí El espinazo del diablo. En español. A su manera."),
  ("bold", "Y en 2006 vuelve con otra historia: El laberinto del fauno."),
  ("softly", "Todo lo que es esa película vive en una libreta. Cuatro años de notas y de dibujos de personajes."),
  ("tense", "Y un día, esa libreta se queda en el asiento de un taxi británico."),
  ("sad", "Cuatro años de trabajo, alejándose por la calle."),
  ("warmly", "Según ha contado, la recuperó."),
  ("softly", "El rodaje tampoco fue fácil. Él lo llama su segunda peor experiencia. Solo detrás de Mimic."),
  ("tense", "27 de mayo de 2006. Festival de Cannes. Se apagan las luces."),
  ("excited", "Cuando termina la película, el público se pone de pie. Y aplaude."),
  ("excited", "Aplaude durante unos 22 minutos. Una de las ovaciones más largas que se recuerdan en el festival."),
  ("tense", "Después de eso, Hollywood vuelve a llamar. Esta vez, con proyectos gigantes."),
 ]),
 ("Las puertas cerradas", [
  ("bold", "El primero: El Hobbit."),
  ("hopeful", "Del Toro acepta. Y pasa casi dos años diseñando ese mundo. Criaturas, escenarios, cada detalle."),
  ("tense", "Pero el rodaje no empieza. El estudio, MGM, tiene problemas financieros. La fecha se mueve. Y se vuelve a mover."),
  ("sad", "En mayo de 2010, Del Toro deja El Hobbit."),
  ("hopeful", "Entonces apuesta por otro sueño: En las montañas de la locura."),
  ("tense", "Unos 150 millones de dólares. Clasificación para adultos. Un final duro. Sin historia de amor."),
  ("softly", "El estudio dudó. Por el presupuesto. Y por la clasificación."),
  ("sad", "Él no la suaviza. Y en 2011, el proyecto se archiva."),
  ("sad", "Dos mundos enteros que no llegó a filmar. ¿Qué le quedaba?"),
 ]),
 ("El Óscar", [
  ("softly", "Le quedaba lo de siempre. Una historia pequeña. Y un monstruo."),
  ("warmly", "La forma del agua: una mujer... y una criatura."),
  ("hopeful", "Sin mundos gigantes. Solo eso."),
  ("tense", "2018. La noche de los Óscar."),
  ("excited", "Mejor director: Guillermo del Toro. Mejor película: La forma del agua."),
  ("warmly", "En el escenario, recordó que es un inmigrante."),
  ("softly", "Mira el camino. En Mimic peleó por el control. Dejó El Hobbit. Le archivaron las montañas de la locura."),
  ("bold", "Y lo que le dio el Óscar fue una película hecha a su manera."),
  ("warmly", "No llegó ahí a pesar de sus monstruos. Llegó porque nunca los soltó."),
  ("softly", "Los monstruos de verdad no estaban en sus películas. Y él nunca dejó de filmar a los suyos."),
  ("warmly", "Si esta historia te sirvió, suscríbete. Hay más como esta."),
 ]),
]
EN = {'Hollywood': 'Jólivud', 'Weinstein': 'Uáinstin', 'James Cameron': 'Yeims Cámeron', 'Cameron': 'Cámeron', 'Mimic': 'Mímic', 'Cannes': 'Can',
      'El Hobbit': 'El Jóbit', 'MGM': 'eme ge eme', 'Necropia': 'Necropia'}
def tts(t):
    for k, v in sorted(EN.items(), key=lambda x: -len(x[0])): t = t.replace(k, v)
    return re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='es'), t)
lines, caps, i = [], [], 0
for ci, (tit, beats) in enumerate(G):
    caps.append(dict(titulo=tit, desde=i + 1))
    for emo, t in beats:
        i += 1; s = tts(t); lines.append(dict(id=f"L{i}", cap=ci, rol='', t=t, tts=s, gen=f"[{emo}] {s}", p=.4, tag=''))
json.dump(dict(titulo='deltoro', meta=dict(famoso='Guillermo del Toro'), capitulos=caps, lines=lines), open('/home/user/w/tuconfia/script_deltoro.json', 'w'), ensure_ascii=False, indent=1)
print('beats', len(lines), 'narración', sum(len(l['t']) for l in lines), 'tts', sum(len(l['tts']) for l in lines), 'gen', sum(len(l['gen']) + 1 for l in lines))
for ci, c in enumerate(caps): print(ci, c['titulo'], sum(len(l['tts']) for l in lines if l['cap'] == ci))
