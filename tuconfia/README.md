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
