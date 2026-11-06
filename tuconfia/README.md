# TU CONF.IA — Stephen King y *Carrie*

## Estado
- `out/TU_CONFIA_Stephen_King_Carrie_v2_PREVIEW_sin_voz.mp4` — 1080×1920, 40 s, sin narración (ElevenLabs bloqueado en este entorno).

## Cómo obtener el MP4 final con voz
1. Entra en https://elevenlabs.io/app/speech-synthesis (voz en español latino, p. ej. una masculina grave/cálida).
2. Modelo **Eleven v3**: pega `elevenlabs_narracion_v3.txt` (lleva etiquetas [..]). Con Multilingual v2: pega `elevenlabs_narracion_v2.txt` (pausas con `<break>`).
3. Descarga el audio y guárdalo como `audio/narracion.mp3`.
4. `cd src && python3 -I build.py` → genera `out/TU_CONFIA_Stephen_King_Carrie_v2.mp4`. Los cortes de escena, subtítulos y el *drop* de la canción se reajustan solos a la voz real (detección de silencios).

## Música
`audio/cancion.m4a`: el inicio de la canción suena en el gancho/contexto; en el giro (Tabitha encuentra las hojas) hay un silencio estratégico y entra el *drop* de la canción (≈31.9 s del original), alineado con el inicio de esa escena.

## Hechos usados (verificados por fuentes secundarias; sin citas inventadas)
King y Tabitha vivían en un remolque en Hermon, Maine; él daba clases (Hampden Academy) y ella trabajaba en Dunkin' Donuts; escribió Carrie en un cuarto-lavadero; tiró ~3 páginas y Tabitha las rescató y lo animó a seguir (*On Writing*); Doubleday: anticipo de 2.500 USD; derechos de bolsillo: 400.000 USD. No se usan: nº de rechazos, fecha exacta ni comprador/reparto exacto (fuentes discrepan). Las escenas son recreaciones ilustradas, no retratos reales.

## Pendiente / límites
- Narración real (arriba). Duración final dependerá de la voz (est. 55–62 s).
- Personajes dibujados proceduralmente en pixel-art (estilo BW/Pokémon); la mascota del canal es tu sprite original.

---
## Historia 2 — Messi y el contrato en una servilleta (vigente)
- Preview: `out/TU_CONFIA_Messi_Servilleta_PREVIEW_sin_voz.mp4` (1080×1920, ~47 s, sin narración).
- Guion: `guion_messi.md` · ElevenLabs: `elevenlabs_messi_v3.txt` (v3) / `elevenlabs_messi_v2.txt` (Multilingual v2).
- Voz final: guarda el audio como `audio/narracion_messi.mp3` y ejecuta `cd src && python3 -I build_messi.py`.
- Sistema de personajes (reutilizable): `src/cast.py` (reparto) + `sprites.py` (chibi RPG) + `sprites_b.py` (batalla) + `chars_anime.py` (portrait). Jerarquía: chibi = planos lejanos · batalla = medios · portrait = solo primeros planos.
- Hechos usados: diagnóstico de déficit de hormona de crecimiento en la infancia; prueba en Barcelona a los 13; el 14-dic-2000 Rexach escribió el compromiso en una servilleta en el club de tenis Pompeia porque la familia pidió algo por escrito y no tenía otro papel; el Barcelona asumió el tratamiento; campeón del mundo 2022. No se usan cifras discutidas ni citas literales.

---
## Historia 3 — Stallone y *Rocky*: lo que no se vende (vigente; Messi, Jordan y Kanye ya estaban hechos por el usuario)
- Preview: `out/TU_CONFIA_Stallone_Rocky_PREVIEW_sin_voz.mp4` (1080×1920, ~48 s, sin narración).
- Guion: `guion_stallone.md` · ElevenLabs: `elevenlabs_stallone_v3.txt` / `elevenlabs_stallone_v2.txt`.
- Voz final: guarda el audio como `audio/narracion_stallone.mp3` y ejecuta `cd src && python3 -I build_stallone.py`.
- Hechos usados (búsquedas web): escribió *Rocky* en muy pocos días; estaba sin dinero y vendió a su perro Butkus; los productores querían comprar el guion sin él de protagonista; se negó; al final aceptó cobrar poco por el papel; *Rocky* ganó el Oscar a Mejor Película y Butkus salió en la película. No se usan cifras discutidas (precio del perro, recompra, oferta) ni citas literales.
- Escenas: `src/scenes4.py` · reparto ampliado en `src/cast.py` (stallone, stallone_tux, prod1, prod2) + perro Butkus en `src/sprites.py`.

### Actualización Stallone (diseño + música + voz)
- Diseño de Stallone más fiel al actor: pelo oscuro y espeso peinado hacia un lado, cejas gruesas, párpados caídos, mandíbula cuadrada y barba de dos días (`cast.py`: `stallone`, `stallone_tux`).
- Música: piano de *Runaway* (`audio/runaway.m4a`, solo ~38 s) al inicio; *Touch The Sky* (`audio/cancion.m4a`) entra al aceptar ("Al final aceptan") y suena en el Oscar.
- Voz: generada con ElevenLabs (voz premade "Brian", vía vidIQ). El MP3 está en la URL de vidIQ; descárgalo como `audio/narracion_stallone.mp3` y ejecuta `cd src && python3 -I build_stallone.py` para el render final con tiempos ajustados a la voz.

### Versión final con voz (Stallone)
- `out/TU_CONFIA_Stallone_Rocky.mp4` — 1080×1920, 52,5 s, voz real (`audio/narracion_stallone.mp3`), en bucle.
- Música: el instrumental de *Runaway* (solo piano, una nota E cada 1,38 s) abre el vídeo; la nota que cae justo en "Al final aceptan" coincide con el primer sonido de *Touch The Sky*, que suena desde el inicio de la canción original. Ambas giran en E, así que no hay desafine. Al final la música baja a silencio para el bucle.
- Alineación voz↔escenas: asignación óptima de las 13 fronteras entre líneas a los silencios de la voz (`align_real` en `src/build_stallone.py`).

### Voz actual (ElevenLabs directo)
- `audio/narracion_stallone.mp3`: voz **George** (premade, gratuita) con `eleven_v3` y etiquetas de emoción por línea ([serious], [warmly], [excited]…), generada con la API de ElevenLabs desde el entorno (la clave se guarda con `request_credential`; nunca va en el repo). 58 s.
- Copia de la versión anterior (Brian, vía vidIQ): `audio/narracion_stallone_brian_vidiq.mp3`.
- Para regenerar: POST a `https://api.elevenlabs.io/v1/text-to-speech/<voice_id>` con `model_id=eleven_v3` (el proxy inyecta la clave). Cuota gratuita: 10.000 caracteres/mes; las voces "profesionales" de la biblioteca (Salva, Antonio…) requieren plan de pago por API.
