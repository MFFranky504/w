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
