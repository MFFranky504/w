> Nota: este archivo es la versión anterior. La plantilla vigente (ganchos «Hasta X fue rechazado» / «X podía... pero se negó», pregunta «¿Cuál fue tu mayor rechazo...?», guardar + suscribirse) está en `PLAN_PUBLICACION.md`, `IDEAS_15.md`, `src/plantilla.py`, `src/captions.py` y `src/cta.py`.

# TU CONF.IA — estrategia de crecimiento

## 1. Kanye West vs Michael Jordan (qué cambia)
No tengo acceso a tus métricas ni a los posts publicados, así que **no puedo afirmar** qué los separa. Lo único medido: Kanye 86 likes, Jordan 6, mediana 5.5, comentarios 0. Rellena esta tabla (Instagram → Insights de cada reel) y compara:

| Variable | Kanye | Jordan | Dónde verlo |
|---|---|---|---|
| Gancho (primeros 2 s, texto exacto) | | | el video |
| Duración (s) | | | el video |
| Primera imagen / miniatura | | | portada |
| Caption (largo, pregunta, hashtags) | | | el post |
| Día y hora de publicación | | | Insights → Audiencia |
| Alcance, % fuera de seguidores ("Exploración") | | | Insights |
| Retención media / % que lo ve completo | | | Insights |
| Compartidos y guardados | | | Insights |

Hipótesis (a verificar, no hechos): Kanye es más conocido, el tema "accidente → rechazo → éxito" engancha más que un logro deportivo, y con 0 seguidores casi todo el alcance viene del algoritmo/Exploración, así que 86 vs 6 puede ser **azar de distribución**. Con n=4 no hay conclusión fiable; por eso el punto 5.

## 2. Plantilla fija (ya en `src/captions.py`)
- Gancho: «¿Sabías que [famoso] transformó [fracaso o rechazo] en [logro]?» (primera frase del video y del caption).
- Estructura: gancho → fracaso → giro → pregunta.
- Cierre del video y del caption: «¿Qué vas a empezar hoy para demostrarte que sí puedes?»
- Hashtags: `#Motivación #Superación #HistoriasQueInspiran` + 1 de la persona (`#KanyeWest`). Sin hashtags ultra específicos (#RockyBalboa).
- Generar: `python3 src/captions.py "Steve Jobs" "su despido de Apple" "el regreso que cambió la tecnología"`
- Nota: el video de Jobs en curso tiene gancho/cierre anteriores; si quieres, lo reescribo al nuevo formato antes de renderizar.

## 3. Experimento (14 días, 1 video/día)
Reglas para que el resultado valga: mismo formato/duración (≤30 s), misma franja horaria 7 días y otra los otros 7 (compara horas), cambiar **una** variable a la vez, medir a las 48 h: alcance, retención, compartidos, guardados, comentarios. Conclusión solo con ≥14 posts. Los 4 videos tipo Kanye (accidente/rechazo → motivación) van en los días 1, 4, 8 y 12; propuestos: Ronaldo (corazón), Lady Gaga (la despiden), Dwayne Johnson (lo cortan), Jim Carrey (pobreza → carta).
Límite real: yo genero los videos/captions, **no publico ni leo tus métricas**; los resultados me los pasas tú.

## 4. 15 ideas (gancho → fracaso → giro → pregunta)
Datos a verificar con fuente antes de grabar (algunos son anécdotas populares).
1. **Kanye West** — ¿Sabías que transformó un accidente de coche (2002, mandíbula rota) en su primer disco? → graba "Through the Wire" con la mandíbula cerrada con alambres → "The College Dropout" → ¿Cuál fue tu mayor rechazo?
2. **J.K. Rowling** — rechazada por ~12 editoriales → Bloomsbury acepta tras leerla la hija del editor → Harry Potter.
3. **Lady Gaga** — la sello la despide a los pocos meses (2006) → escribe para otros → "The Fame".
4. **Dwayne Johnson** — cortado del fútbol (CFL), casi sin dinero → lucha libre → estrella de cine.
5. **Jim Carrey** — pobre, vivía en una van → se escribe un cheque de 10 millones "por servicios actorales" → éxito.
6. **Tom Brady** — elegido en el puesto 199 del draft → suplente → 7 Super Bowls.
7. **Cristiano Ronaldo** — a los 15 le detectan un problema cardíaco → operación → Balón de Oro.
8. **Oprah Winfrey** — despedida como presentadora en Baltimore (1977) → su propio talk show.
9. **Steve Jobs** — despedido de Apple (1985) → NeXT/Pixar → regresa (1997).
10. **Eminem** — su primer álbum "Infinite" fracasa → "The Slim Shady LP" → 8 Mile.
11. **Shakira** — la profesora la saca del coro del colegio → se vuelve cantante global.
12. **Vera Wang** — no entra al equipo olímpico de patinaje → moda a los 40 → vestidos icónicos.
13. **Walt Disney** — (anécdota popular) despedido de un periódico por "falta de imaginación" → quiebra de su primer estudio → Mickey Mouse.
14. **Elvis Presley** — (anécdota popular) le dicen que vuelva a conducir camiones tras una audición → rey del rock.
15. **Colonel Sanders** — cientos de rechazos a su receta ya jubilado → KFC.
