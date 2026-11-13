# EP-001 — Vuelo 914 — Legal y QC

## Checklist pre-publicación (Biblia §12)

- [ ] Fuentes verificadas por un humano (tabla de `01_INVESTIGACION.md` §4). **Bloquea la publicación.**
- [x] Animación de Claude integrada en la línea de tiempo (`export/final_v02.mp4`, 9:42).
- [x] Audio nivelado (-16 LUFS), gradación fría y grano aplicados en cada clip.
- [ ] Miniatura generada y revisada (prompt en `02_GUION_PRODUCCION.md`).
- [ ] Shorts subidos con "Video relacionado" apuntando al largo.
- [ ] Handle `@ArchivoCero` verificado en YouTube, TikTok e Instagram (§0.3).
- [ ] Revisión visual humana de las 44 escenas: artefactos, texto ilegible, rostros.
- [ ] Descripción con enlaces a las fuentes confirmadas.

## QC técnico del build

| Regla | Estado |
| :--- | :--- |
| Plano ≥ 3.0 s (§2.4) | Cumple: cada plano dura lo que su narración |
| Movimiento lento (§2.4) | Zoom 10% por plano, con paneo lateral alterno |
| Saturación ≤ 25% promedio | Saturación reducida a 30% del original en el build; medir en el editor |
| Badge de certeza por bloque (§11.A.5) | Esquina superior izquierda |
| Sin rostros reconocibles (§5.3) | Prompts sin rostros; requiere revisión humana |
| Música con licencia (§4.3) | Drone sintetizado en el build, producción propia |
| Formato A, 8-12 min | Cumple: 9:42. Shorts: 43, 41 y 44 s |

## Desviaciones conocidas de la Biblia

- **Gradación y grano van horneados en los clips.** No aplicar otra capa de LUT en DaVinci sobre `assets/vid/`.
- **Shorts sin guion propio.** Reutilizan audio e imagen de escenas del largo más una frase de cierre. El gancho de 0-3 s es el inicio de la escena, no una pregunta escrita para el Short.
- **Voz Edge TTS sin marcas de modulación** (`[cuchillo]`, `[pausa-clave]`). Solo hay silencios: 0.6 s entre escenas y 2 s entre bloques.
- **Imágenes:** Cloudflare Workers AI (Flux schnell), no Ideogram. Salida 1024×1024, escalada a 1080p.

## Pendiente antes de publicar

- **Escenas 31 a 44 (bloques 7.2 a 9.5) usan imágenes repetidas de marcador.** La cuota diaria gratis de Cloudflare se agotó tras 30 imágenes. Repetir el build al día siguiente: genera las 14 imágenes que faltan y sus clips finales. El Short 3 incluye una de esas escenas (7.3).
- **Texto ilegible generado por la IA** en calendarios y periódicos (escenas 11, 12, 14, 21, 26 y otras). Regenerar borrando el `.jpg` de `assets/img/` o tapar en edición.
- Los exports `v01` son la primera pasada, demasiado oscura. Usar `v02`.

## Fe de erratas

Sin entradas.

---

## Versión pixel art (motor `tools/pixel`) — 2026-11-13

| Comprobación | Resultado |
| :--- | :--- |
| Archivo | `export/vuelo914_v01.mp4`, 1920×1080, 24 fps, 8:01, 11.551 fotogramas |
| Short | `export/vuelo914_short_short_v01.mp4`, 1080×1920, 30,7 s, más `.srt` |
| Loudness | −16,3 LUFS (episodio), −16,7 LUFS (Short) |
| Negros y silencios accidentales | 0 y 0 |
| Gancho | Primer fotograma: el avión. Frase en los segundos 0 a 3: "Este avión despegó de Nueva York en 1955." |
| Planos | 104, todos de 8 s o menos; los de menos de 2 s son golpes de ritmo intencionales |
| Texto en pantalla | Todo compuesto por el motor. Cero texto generado por IA. Autoprueba de glifos y paleta superada |
| Fuentes | Verificadas en Snopes, Lead Stories y Wikipedia (`01_INVESTIGACION.md` v2). Datos de una sola fuente, atribuidos en pantalla |
| Música y efectos | Síntesis original del motor, sin audio de terceros. Gemini escuchó 20 s del Short: voz clara, música audible sin tapar la voz, sin distorsión |
| Revisión | Un fotograma cada 6 s del episodio y un fotograma por plano en las stills. **No se vio ni escuchó el episodio completo de corrido** |
