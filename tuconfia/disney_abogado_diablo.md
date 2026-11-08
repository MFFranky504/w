# Disney: revisión del abogado del diablo (script_disney.json)

Revisión del 8-nov-2026. Las afirmaciones de riesgo se comprobaron por separado con WebSearch, sin fiarse de las notas del analista (las fuentes están en el anexo).
**Resultado:** los datos aguantan. Los problemas reales son de **lógica interna**: el guion se contradice en tres sitios y dos frases suenan a otra cosa al oírlas. Hay que corregir 4 críticos antes de generar la voz.

Medida de duración: Hawking tenía 3.176 caracteres de `tts` y 186,5 s de audio, unos **17,0 caracteres por segundo con las etiquetas incluidas**.
- Disney actual: 2.565 caracteres, unos **2:31**.
- Disney con todas las correcciones de abajo: **2.741 caracteres, unos 2:41**. Queda por debajo de 2:50 y del límite de 2.900.

---

## 1. Veredicto por severidad

### CRÍTICO (corregir sí o sí)

**C1 · L2 (y L25, L22, la descripción y la miniatura A): «Ese no le costó su personaje... y a su equipo» choca con L5 y L6.**
L5 dice que Oswald nunca fue de Walt y L6 que Mintz ya había contratado a los animadores *antes* de la reunión. Entonces el «no» no le *costó* ni el conejo ni el equipo, porque ya los había perdido. Lo que hizo el «no» fue que se fuera sin ellos. Además, «le quitaron» (L22, L25 y la miniatura) contradice L5: no te pueden quitar lo que no es tuyo. Es el primer comentario de «pues en realidad...» que va a aparecer.
- L2 `t`: `Por ese *no*, tuvo que dejar a su personaje... y a casi todo su equipo. Y lo que pasó después con ese personaje... casi nadie lo sabe.`
- L2 `tts`: `Por ese no, tuvo que dejar a su personaje... y a casi todo su equipo. Y lo que pasó después con ese personaje... casi nadie lo sabe.`
- L2 `gen`: `[serious] Por ese no, tuvo que dejar a su personaje... y a casi todo su equipo. [whispers] Y lo que pasó después con ese personaje... casi nadie lo sabe.`
- L22 `t`: `¿Y el conejo que tuvo que dejar? En 2006, *setenta y ocho* años después, la compañía Disney recuperó a Oswald.`
  - L22 `tts`: `¿Y el conejo que tuvo que dejar? En dos mil seis, setenta y ocho años después, la compañía Dísney recuperó a Ósuald.`
  - L22 `gen`: `[curious] ¿Y el conejo que tuvo que dejar? [pause] En dos mil seis, setenta y ocho años después, [excited] la compañía Dísney recuperó a Ósuald.`
- L25 `t`: `*Perdió* su personaje y casi todo su equipo... pero no las ganas de *empezar* otra vez.`
  - L25 `tts`: `Perdió su personaje y casi todo su equipo... pero no las ganas de empezar otra vez.`
  - L25 `gen`: `[determined] Perdió su personaje y casi todo su equipo... [pause] pero no las ganas de empezar otra vez.`
- Descripción: cambiar «Ese "no" le costó su personaje» por «Por ese "no", tuvo que dejar a su personaje».

**C2 · L23: «Cambiándolo por un narrador» dice lo contrario de lo que pasó.**
El «lo» de «cambiándolo» se refiere a Oswald, así que al oírlo se entiende que Disney *entregó* el conejo a cambio de un narrador. Fue al revés: Disney (ABC/ESPN) dejó ir a Al Michaels y NBC Universal le devolvió Oswald. Además falta la ironía que mejor paga la curiosidad: Michaels se iba precisamente a la empresa dueña del conejo.
- `t`: `¿Cómo? Dejando ir a un *narrador* deportivo, Al Michaels, que quería irse a la competencia... justo a la empresa dueña del conejo.`
- `tts`: `¿Cómo? Dejando ir a un narrador deportivo, Al Máikols, que quería irse a la competencia... justo a la empresa dueña del conejo.`
- `gen`: `[playful] ¿Cómo? [pause] Dejando ir a un narrador deportivo, Al Máikols, que quería irse a la competencia... [pause] justo a la empresa dueña del conejo.`
(Verificado: ESPN/AP, NPR, Spokesman, 9/10-feb-2006. Michaels se iba a la NBC de *Sunday Night Football*, que era de NBC Universal, la dueña de Oswald.)

**C3 · L12: «...y lo animó» se entiende como «le dio ánimos».**
Al oírlo en español, «Ub le dio su forma y lo animó» suena a que Ub *animó a Walt* (le dio ánimos). Justo es el crédito que el video quiere darle a Iwerks y se pierde.
- `t`: `Según contó Walt, en el tren de regreso imaginó un ratón. Pero fue Ub quien le dio su *forma*... y quien lo hizo moverse.`
- `tts`: `Según contó Uólt, en el tren de regreso imaginó un ratón. Pero fue Ab quien le dio su forma... y quien lo hizo moverse.`
- `gen`: `[curious] Según contó Uólt, en el tren de regreso imaginó un ratón. [pause] Pero fue Ab quien le dio su forma... [proud] y quien lo hizo moverse.`

**C4 · L28 (y `meta.pregunta`): «que sea *solo* tuyo» contradice L26.**
L26 acaba de decir «Y no lo hizo solo: un hermano... y un amigo...». Cerrar con «crear algo *solo* tuyo» deshace la moraleja del equipo, y además el «solo» se puede oír como «únicamente» o como «a solas». Por otro lado, la tesis «crear algo tuyo» no tiene prueba en el cuerpo del guion: ver I1.
- `t`: `Y tú... ¿a qué trato injusto le dirías que *no*... y qué empezarías a crear que sea *tuyo*?`
- `tts`: `Y tú... ¿a qué trato injusto le dirías que no... y qué empezarías a crear que sea tuyo?`
- `gen`: `[softly, reflective] Y tú... ¿a qué trato injusto le dirías que no... [pause] [warmly] y qué empezarías a crear que sea tuyo?`
- `meta.pregunta` igual. Hay que cambiarla también en la descripción y en el comentario fijado.

### IMPORTANTE

**I1 · L16: falta el pago de la tesis «algo tuyo».**
L27 dice «decir no te obliga a crear algo tuyo», pero el guion nunca dice que el ratón *sí* fuera suyo. Ese es justamente el aprendizaje documentado de lo de Oswald: desde entonces Walt se aseguró de ser dueño de sus personajes. Con 24 caracteres más queda cerrado.
- `t`: `Y el público *estalló* de risa. El ratón fue un éxito... y esta vez, era *suyo*.`
- `tts`: `Y el público estalló de risa. El ratón fue un éxito... y esta vez, era suyo.`
- `gen`: `[excited] Y el público estalló de risa. [proud] El ratón fue un éxito... [pause] y esta vez, era suyo.`
(Es una simplificación defendible: los derechos eran del estudio de Walt y Roy, no de Universal.)

**I2 · L5 y L7: «su conejo» inmediatamente después de «Oswald no es de Walt».**
En L7, «se fue sin su conejo» repite la contradicción de C1 seis segundos después de explicarla. Además, «trabajar por menos *para otro*» es vago: ¿quién es ese otro?
- L7 `t`: `Podía quedarse, cobrar menos y trabajar para Mintz. Pero dijo *no*... y se fue sin Oswald.`
- L7 `tts`: `Podía quedarse, cobrar menos y trabajar para Mínts. Pero dijo no... y se fue sin Ósuald.`
- L7 `gen`: `[determined] Podía quedarse, cobrar menos y trabajar para Mínts. [bold] Pero dijo no... [pause] y se fue sin Ósuald.`
- L3 puede conservar «su conejo», porque ahí todavía no se ha revelado nada y el giro de L5 funciona.

**I3 · L17: «un distribuidor con el que Walt se *había* peleado» es impreciso.**
En enero de 1930, Pat Powers era *el distribuidor de Walt* (Cinephone). La pelea por dinero y la salida de Iwerks ocurrieron al mismo tiempo: Powers fichó a Iwerks justo en esa disputa, y el acuerdo se firmó en abril de 1930. El pluscuamperfecto da a entender que Ub se fue con un enemigo antiguo.
- `t`: `Pero en 1930, Ub se fue. Firmó con Pat Powers, el distribuidor de Walt... con quien Walt peleaba por *dinero*.`
- `tts`: `Pero en mil novecientos treinta, Ab se fue. Firmó con Pat Páuers, el distribuidor de Uólt... con quien Uólt peleaba por dinero.`
- `gen`: `[serious] Pero en mil novecientos treinta, Ab se fue. [pause] Firmó con Pat Páuers, el distribuidor de Uólt... con quien Uólt peleaba por dinero.`

**I4 · L18: «cuando *todos* se fueron» es falso.**
También se quedó Les Clark (aprendiz que después fue uno de los «Nueve Ancianos»), y posiblemente Johnny Cannon. Las fuentes dicen «Iwerks y Les Clark». L11 tampoco debe dar a entender que Ub fue el único.
- L18 `t`: `El amigo que se quedó cuando *casi* todos se fueron... ahora era su *competencia*.`
  - L18 `tts`: `El amigo que se quedó cuando casi todos se fueron... ahora era su competencia.`
  - L18 `gen`: `[sad] El amigo que se quedó cuando casi todos se fueron... [softly] ahora era su competencia.`
- L11 `t`: `Y tenía a uno de los pocos que se negaron a irse con Mintz: su amigo, el animador *Ub Iwerks*.`
  - L11 `tts`: `Y tenía a uno de los pocos que se negaron a irse con Mínts: su amigo, el animador Ab Áiuerks.`
  - L11 `gen`: `[warmly] Y tenía a uno de los pocos que se negaron a irse con Mínts: [proud] su amigo, el animador Ab Áiuerks.`
- La nota de verificación de L11 («único animador clave») se debe corregir a «uno de los pocos (con Les Clark)».

**I5 · L19: la causa que se da a entender es la que no está probada.**
Puesto justo después de L18, se entiende que Walt se hundió *porque* Ub se fue. Las fuentes (Barrier; el viaje de oct-nov de 1931 recomendado por el médico, según D23/Kurtti) hablan sobre todo de exceso de trabajo y ansiedad. Además, quitar un año hablado ayuda: el guion dice 9 años distintos en 2:30.
- `t`: `Al año siguiente, agotado, Walt se vino *abajo*: así lo contó él mismo. Su médico le ordenó parar y descansar.`
- `tts`: `Al año siguiente, agotado, Uólt se vino abajo: así lo contó él mismo. Su médico le ordenó parar y descansar.`
- `gen`: `[softly] Al año siguiente, agotado, Uólt se vino abajo: así lo contó él mismo. [sad] Su médico le ordenó parar y descansar.`
- En pantalla, rótulo «1931».

**I6 · L21: la línea de sombra está pegada sin más («no fue perfecto», huelga) y no dice por qué.**
Así suena a un trámite antihagiográfico y deja al espectador sin saber de qué iba la huelga. El espejo con el tema de la historia lo vuelve honesto y fuerte: el hombre que se negó a cobrar menos vio a su gente pedir mejores sueldos. Los datos están comprobados: huelga desde el 29-may-1941, unos 200-400 huelguistas según la fuente, por desigualdad salarial y reconocimiento sindical.
- `t`: `Y no, Walt no fue un hombre perfecto. El hombre que se negó a cobrar menos... en 1941 vio a cientos de sus animadores en *huelga*, pidiendo mejores sueldos.`
- `tts`: `Y no, Uólt no fue un hombre perfecto. El hombre que se negó a cobrar menos... en mil novecientos cuarenta y uno vio a cientos de sus animadores en huelga, pidiendo mejores sueldos.`
- `gen`: `[serious] Y no, Uólt no fue un hombre perfecto. [pause] El hombre que se negó a cobrar menos... en mil novecientos cuarenta y uno vio a cientos de sus animadores en huelga, pidiendo mejores sueldos.`

**I7 · L14: «apostó por algo nuevo» da a entender que fue el primero.**
No lo fue: antes hubo los *Song Car-Tunes* de Fleischer (1924-26) y *Dinner Time* de Paul Terry (1928). Las notas lo saben, pero «algo nuevo» lo vuelve a sugerir.
- `t`: `Entonces apostó por la gran novedad del momento: dibujos con *sonido* sincronizado. Y él mismo le puso la voz al ratón.`
- `tts`: `Entonces apostó por la gran novedad del momento: dibujos con sonido sincronizado. Y él mismo le puso la voz al ratón.`
- `gen`: `[determined] Entonces apostó por la gran novedad del momento: dibujos con sonido sincronizado. [playful] Y él mismo le puso la voz al ratón.`

**I8 · L13: falta la palabra que une L13 con L14.**
Si no se dice que el primer corto era mudo, el salto «nadie lo quiso, entonces apostó por el sonido» no se entiende.
- `t`: `El primer corto del ratón, todavía *mudo*, no le interesó a *ningún* distribuidor. Otro rechazo.`
- `tts`: `El primer corto del ratón, todavía mudo, no le interesó a ningún distribuidor. Otro rechazo.`
- `gen`: `[sad] El primer corto del ratón, todavía mudo, no le interesó a ningún distribuidor. [heavy sigh] Otro rechazo.`

**I9 · Capítulos (estrategia, §3): 11 capítulos para unos 2:40 no se van a mostrar.**
YouTube exige que cada capítulo dure al menos 10 s. «El ratón de Ub Iwerks» (solo L12, unos 7 s) y «No fue perfecto» (solo L21) quedan cortos. Si un solo capítulo falla, YouTube no muestra ninguno. Propuesta de 7 capítulos:
`00:00 Dijo que no` (L1-L8) · `Lo que le quedó` (L9-L12) · `Otro rechazo... y el sonido` (L13-L16) · `El amigo que se fue` (L17-L20) · `No fue perfecto` (L21) · `El conejo vuelve` (L22-L24) · `Lo que te queda` (L25-L28).
Con la L21 nueva (unos 10,5 s) apenas pasa el mínimo. Si al montar queda por debajo de 10 s, fusionarla con «El amigo que se fue».

### MENOR

- **M1 · L5 `tts` «Iuniversal».** En español latino, Universal se dice en español («Uni-ver-sál»). «Iuniversal» suena a espanglish forzado. Usar `Universal`. En el `gen` hay que cambiar lo mismo.
- **M2 · L20 «pasó algo que pocos cuentan»** repite la promesa de L2 («casi nadie lo sabe»). Dos «secretos» abaratan el segundo, que es el bueno. Propuesta:
  - `t`: `Descansó... y volvió. Y en 1940, Ub *regresó* al estudio.`
  - `tts`: `Descansó... y volvió. Y en mil novecientos cuarenta, Ab regresó al estudio.`
  - `gen`: `[warmly] Descansó... y volvió. [pause] Y en mil novecientos cuarenta, [emotional] Ab regresó al estudio.`
  - Si sobra tiempo, se puede añadir «y se quedó hasta el final de su vida» (Iwerks murió en 1971 trabajando en Disney).
- **M3 · Demasiados arranques con «Pero» y «Y»** (L4, L7, L10, L17, L24 y diez con «Y»). Si al escucharlo cansa, cambiar L24 por «Walt había muerto en 1966...» (sin «Pero»).
- **M4 · L6 «a sus espaldas»:** se puede mantener. Mintz y Winkler negociaron sin decírselo, aunque Iwerks había avisado a Walt en enero de 1928 y Walt no le hizo caso. No hace falta contarlo, pero no hay que exagerar con un «traición total» en pantalla.
- **M5 · Avalancha de años:** 1928, 1923, 1928, 1930, (1931), 1940, 1941, 2006, 1966. Cada año que se diga en voz debe tener su rótulo grande en pantalla. L24 vuelve a 1966 después de 2006: ayuda poner en pantalla «1966» con la silla vacía.
- **M6 · L2 `[whispers]`:** en v3 puede bajar tanto el volumen que la frase-promesa se pierda en el móvil. Probar `[softly]` si el susurro queda por debajo de unos -20 LUFS respecto al resto.
- **M7 · Estreno en el Colony:** varias fuentes lo llaman «Universal's Colony Theatre», lo que sería una ironía muy buena. **No está verificado**, así que NO usarlo.

---

## 2. Si pasa de 2:50: qué recortar o fusionar (en este orden)

Previsión con las correcciones: unos 2:41, así que **no debería hacer falta**. Si la toma real de v3 sale lenta:
1. **L20:** dejar solo `Y en mil novecientos cuarenta, Ab regresó al estudio.` (quita «Descansó... y volvió.», unos 1,5 s).
2. **Fusionar L17 y L18:** `Pero en mil novecientos treinta, Ab se fue con Pat Páuers, el distribuidor con quien Uólt peleaba por dinero. Su amigo... ahora era su competencia.` (unos 3 s).
3. **L16:** quitar «Y el público estalló de risa.» y dejar `El ratón fue un éxito... y esta vez, era suyo.` (unos 1,5 s; la escena de público riendo lo cuenta en imagen).
4. **L23:** quitar «...justo a la empresa dueña del conejo» (unos 2 s). Último recurso, porque es la mejor ironía.
5. **NO recortar:** L2 (el bucle), L5-L7 (el giro), L21 (la sombra), L24 (el golpe final), L26 (el crédito a Roy y a Ub) ni L28.

---

## 3. Pronunciación (ElevenLabs v3, español)

| Palabra en `tts` | Riesgo | Recomendación |
|---|---|---|
| Uólt Dísney | bajo | Mantener. Comprobar que no diga «Dis-néi» con acento final. |
| Ósuald | medio (que lea «Ó-su-ald» en 3 sílabas) | Mantener «Ósuald». Si sale en 3 sílabas, probar «Óswald». |
| Chárls Mínts | bajo | Mantener. |
| **Iuniversal** | **alto: suena raro** | **`Universal`**, en español normal. |
| Kánsas Síti | bajo | Mantener. |
| Rói | bajo | Mantener. |
| **Ab** (Ub) | medio: puede deletrear «a, be» o quedar tragado | Mantener «Ab». Si falla, probar «Áb» o «Ab Áiuerks» completo en la primera mención de cada bloque. |
| Áiuerks | bajo | Mantener (inglés /ˈaɪwərks/). |
| Estímbout Uíli | medio | Mantener. Alternativa: «Estímbout Güíli» si lee «U-í-li». |
| Pat Páuers | bajo | Mantener. |
| Al Máikols | bajo | Mantener. **No** escribir «NBC» en el `tts`: v3 diría «en-bi-si» o «ene-be-ce» según el momento. Por eso C2 dice «la competencia». |
| Años | bajo | Todos van en palabras. Correcto. |
| «setenta y ocho» | bajo | Correcto. Comprobar que no lo pegue con «años» de la frase anterior. |
| «dieciocho de noviembre» | bajo | Correcto. |

Regla para la toma: generar L3, L11, L15 y L23 sueltas primero (son las de más nombres). Si salen bien, generar el resto.

---

## 4. Título y miniatura

**Título 1 «Walt Disney podía aceptar el trato... pero se negó» (50 c): se mantiene.** El nombre va primero, sigue la fórmula del canal y es veraz.
- Crítica: «el trato» es abstracto y no tiene ninguna palabra que alguien busque.
- Lo compensa la miniatura y la descripción (el «Oswald» de la descripción).

**Título 2 «Le quitaron su conejo a Walt Disney... volvió 78 años después»: corregir.** «Le quitaron» tiene el mismo problema que C1. Usar:
**«Walt Disney perdió a su conejo... y volvió 78 años después»** (57 c).

**Título 3:** sirve tal cual como reserva.

**Miniatura A «LE QUITARON SU CONEJO»: rechazada.** Es falsa en lo técnico (C1) y va a invitar al «nunca fue suyo» en los comentarios, justo donde el video presume de rigor.
- **Propuesta final A: «PERDIÓ SU CONEJO»** (3 palabras).
  - Es veraz.
  - Crea un vacío de curiosidad («¿Disney tenía un conejo?»), que es el gancho real para un público latino que no conoce a Oswald.
  - No repite el título: el título dice lo que hizo y la miniatura lo que perdió.
  - Se lee en 1 s en el móvil.
  - «PERDIÓ» en blanco, «SU CONEJO» en amarillo #FFD23F.
- **B, para la prueba A/B: «78 AÑOS DESPUÉS»** (3 palabras). Es mejor que «VOLVIÓ 78 AÑOS DESPUÉS» porque es más corta, más grande y deja que la imagen (el conejo entrando por la puerta) cuente el regreso.
- **Composición:** se mantiene la del analista (Walt chibi y silueta de conejo de espaldas), con un cambio: **quitar el «contrato roto»**. Walt no rompió ningún contrato, y en pantalla parece que lo hubiera hecho. Mejor que sostenga una hoja con un **dibujo de conejo genérico**, mientras la silueta se aleja.
- **Nada de «MICKEY» en la miniatura**, aunque «ANTES DE MICKEY» sería tentador: es una marca registrada y además destripa la historia.

---

## 5. Riesgos legales y éticos, y cómo mitigarlos en pantalla

**Marcas y personajes**
- *Steamboat Willie* (1928) es de dominio público en EE. UU. desde el 1-ene-2024. Los cortos de Oswald de 1927 lo son desde 2023.
- Pero **Disney conserva las marcas** de Mickey y Oswald, y las versiones posteriores siguen protegidas.
- Que la obra sea de dominio público **no** permite usar diseños que confundan con la marca. Política del canal: **ningún diseño reconocible**.

**NO dibujar:**
1. Mickey en ninguna forma: tres círculos, orejas redondas negras, pantalón corto rojo con botones, guantes blancos, zapatos amarillos.
2. **Un ratón al timón de un barco de vapor silbando.** Es la imagen más reconocible de *Steamboat Willie*, aunque sea de dominio público. Riesgo de marca y de Content ID.
3. Oswald: orejas largas negras con punta, pantalón corto, cara de 1927. El conejo debe ser **gris y genérico, preferiblemente en silueta**.
4. El castillo, el logotipo «Walt Disney» con la **firma cursiva** (es una marca), la tipografía de Disney y los logos de Universal, NBC, ABC o ESPN. Los nombres en texto plano están bien. Los logos, no.
5. En la escena 7 (tren), **el «círculo» que garabatea Walt no debe convertirse en una cabeza con dos orejas**. Que sea una hoja llena de garabatos ilegibles.

**Audio**
- Solo el piano original o con licencia.
- **No** usar «Steamboat Bill», el silbido de Willie, «When You Wish Upon a Star» ni ninguna melodía de Disney, aunque sea en piano: activa Content ID.
- No generar con ElevenLabs una «voz de Mickey» ni una «voz de Walt» en L14.

**Personas reales**
- **Walt:** el derecho de imagen póstumo de California dura 70 años (hasta 2036), pero excluye expresamente las obras audiovisuales biográficas. El chibi en el video y en la miniatura del propio video está bien. **No** usarlo en merch, anuncios pagados ni patrocinios.
- **Al Michaels** está vivo: solo silueta genérica con micrófono, sin parecido, sin foto y sin burla del tipo «lo vendieron como un objeto». El texto en pantalla no debe decir «vendido». Debe decir «lo dejaron ir».
- **Mintz:** silueta y nada de rasgos caricaturescos de villano. Retratar a un hombre real como malo de dibujos animados es un riesgo ético, sobre todo si se exageran rasgos étnicos. Traje y contraluz bastan.
- **Huelga:** carteles sin texto legible, como ya propone el analista. Bien.

**Plataforma**
- Marcar el video como **«No, no es contenido para niños»**. Pixel art, chibis y Disney hacen que el clasificador de YouTube lo pueda tomar como contenido infantil, lo que quita comentarios y la pantalla final.
- Divulgación de contenido sintético: no es obligatoria para una narración no realista. Aun así, conviene dejar la línea de la descripción («Los personajes del video son dibujos originales del canal...») y añadir: **«No afiliado a The Walt Disney Company.»**
- No usar fotos ni metraje de archivo de Disney, de *Steamboat Willie* ni de Oswald.

**Tono:** con C1, I1 e I6, el guion deja de ser hagiográfico y no manipula. Lo único que roza el clickbait es «casi nadie lo sabe» (L2). Es aceptable para el público objetivo, siempre que no se repita (M2).

---

## 6. Lo que SÍ está bien (no romperlo al editar)

- **Arranque in medias res en Nueva York 1928:** el «no» llega en unos 25 s. La estructura L3-L7 (petición → oferta peor → dos revelaciones → «dijo no») es de manual.
- **Bucle L2 → pago L22-L24:** la promesa se cumple, y «nunca vio volver a su conejo» es el mejor golpe emocional del guion.
- **Segundo golpe después del éxito (L17-L19):** evita el valle de logros. Crédito explícito a Roy y a Ub (L10, L11, L26).
- **«Según contó Walt» para el ratón del tren y «Walt mismo contó» para la crisis:** se mantienen esas marcas, como pide voice.md.
- **Datos comprobados por separado, todos correctos:**
  - Nueva York 1928 y la oferta a la baja de Mintz.
  - Los derechos eran de Universal.
  - Mintz contrató a los animadores sin decírselo a Walt.
  - Edad: 26 (nació el 5-dic-1901).
  - Kansas City: Laugh-O-Gram quebró en 1923, cinco años antes.
  - El primer corto (*Plane Crazy*) no consiguió distribuidor.
  - Estreno el 18-nov-1928 en el Colony de Nueva York.
  - Walt puso la voz a Mickey.
  - Iwerks se fue con Powers en enero de 1930 y volvió en 1940.
  - Crisis y viaje de descanso por orden del médico en 1931.
  - Huelga desde el 29-may-1941.
  - Oswald volvió en febrero de 2006 a cambio de Al Michaels: 78 años.
  - Walt murió en 1966.
- Sin cifras dudosas («700 dibujos», cuánto dinero le recortaron) y sin «perdió todo». Se mantiene así.
- Fórmula del gancho y reglas de voice.md: años en palabras, una palabra con énfasis por frase, SUSCRÍBETE solo en pantalla.

---

### Anexo: fuentes consultadas en esta revisión
- Quiénes se quedaron y el aviso de Iwerks en enero de 1928: https://en.wikipedia.org/wiki/Les_Clark · https://www.waltdisney.org/blog/first-nine-les-clark · https://cartoonresearch.com/index.php/winkler-oswalds/
- Powers e Iwerks en 1930: https://en.wikipedia.org/wiki/Iwerks_Studio · https://en.wikipedia.org/wiki/Pat_Powers_(producer) · https://mouseplanet.com/harry-cohn-columbia-and-walt-disney/2543/
- Colony Theater, 18-nov-1928: https://www.moma.org/collection/works/302797 · https://d23.com/a-to-z/steamboat-willie/
- El sonido no fue el primero (Fleischer y Terry): https://en.wikipedia.org/wiki/Steamboat_Willie
- Crisis de 1931 y viaje recomendado por el médico: https://d23.com/?p=88248
- Huelga de 1941: https://en.wikipedia.org/wiki/Disney_animators%27_strike · https://avclub.com/the-great-disney-strike-of-1941-1850623261
- Oswald y Al Michaels en 2006: https://www.espn.com/espn/wire/_/section/nfl/id/2325512 · https://www.npr.org/2006/02/13/5204187/abc-trades-sportscaster-for-oswald-the-rabbit · https://www.spokesman.com/stories/2006/feb/10/hare-brained-deal/
- Iwerks vuelve en 1940 y Laugh-O-Gram quiebra en 1923: https://animationresources.org/biography-ub-iwerks/ · https://d23.com/disney-a-to-z/iwerks-ub/
- Lección de ser dueño de sus personajes: https://jimhillmedia.com/?p=1157 · https://www.joshuakennon.com/the-life-and-business-lessons-of-oswald-the-lucky-rabbit/
