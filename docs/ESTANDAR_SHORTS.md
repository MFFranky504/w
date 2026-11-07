# Estándar para los siguientes Shorts
- 22 s (20-35). Gancho en 0,0-1,0 s sin intro; CTA a mitad (7-9 s) y CTA final arriba; un solo remate; loop al segundo 0.
- Zona segura: texto crítico en 12-70 % de la altura, margen lateral 8 %, nada en el 25 % inferior ni a la derecha. Cajas de máx. 8 palabras en 1 línea (≥ 50 px nominal). HUD 1,5x. Banderas: apagadas (`make_cast(flags=False)`).
- Jerga: UN registro por video (`make_cast(register="MX"|"AR")`). Sin «chamo»/«causa».
- Audio: `mix="pro"` → música 22 dB bajo SFX con ducking al hablar; loudnorm a -14 LUFS, true peak ≤ -1 dBTP; se mide y guarda `videos/<id>-<variante>.lufs.json`.
- Experimentos (una variable por video): `render --variant A|B` (gancho) y `--cta ab|etiqueta` (CTA). `python3 -m frnky analisis` aplica los umbrales: gancho ≥ 10 pts de retención 3 s con ≥ 300 vistas cada uno; CTA ≥ 3 vs 0 comentarios/1.000 vistas; sin conclusión con < 5 videos por variante. Siempre mediana.
- Meta realista: media 259 → 400-600 vistas (1,5x-2x) en 5 videos; retención 3 s ≥ 65 %; ≥ 1 comentario por video. Sin métricas inventadas.
