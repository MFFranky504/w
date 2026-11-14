# PLAN J — Especificación de la Temporada 1

**Versión:** 1.0 · **Base:** Documento Maestro v2.0 y respuestas de la Fase de Descubrimiento (14/11/2026)
**Estado:** Borrador para auditoría (Gemini/DeepSeek) y para implementación (Codex)

---

## 0. Decisiones cerradas en el descubrimiento

| Tema | Decisión | Consecuencia de diseño |
|---|---|---|
| Premio | Simbólico (título, insignia, cameo en T2) | Se permite el azar auditado. Hacen falta bases mínimas, pero no permiso de sorteo. |
| Secreto | Híbrido: G1–G2 por comentario público; G3–G6 por DM | Los juegos públicos se diseñan para que ver a los demás sea parte de la estrategia. Los DMs requieren App Review o una herramienta aprobada (§7.4). |
| Mezcla | Equilibrada (objetivo 40 lógica / 20 azar / 40 social) | Resultado aproximado: lógica 2 juegos, azar 1 juego + repechaje, social 3 juegos. |
| Repechaje | Uno, a mitad de temporada | Ventana "La Grieta" tras el G3. |
| Escala | Desconocida: el diseño vale de 200 a 20,000 | Cupos calculados con fórmula sobre los elegibles, nunca números fijos. |
| Duración | 6 semanas, 6 juegos, 1 ganador | 12 episodios de juego, más convocatoria y censo. |
| Producción | Una persona + IA | Render 100% programático desde plantillas. Revisión humana de unos 30 min por episodio. |
| Cuenta IG | Nueva, sin seguidores | Calentamiento de 7 semanas que sirve también como prueba real de ingesta. |
| Cadencia | 2 episodios/semana, ventanas de 48 h | Lunes REGLAS y jueves VEREDICTO. |
| Hora oficial | CDMX (UTC−6 todo el año, sin horario de verano) | 20:00 CDMX = 02:00 UTC del día siguiente. Siempre se publican ambas. |
| Portal web | No: todo en Instagram | Resultados en "El Muro" (carrusel de cuadrícula por ID) y hashes en los captions. |
| Inicio | Se trabaja desde ya; la convocatoria se abre al pasar el gate | Convocatoria recomendada: **lunes 4 de enero de 2027**. |

**Por qué no antes de enero:** una convocatoria a principios de diciembre pondría el G3–G5 en Nochebuena y Año Nuevo (24 y 31 de diciembre caen en jueves, día de veredicto). Además, el App Review de Meta necesita margen y una cuenta nueva necesita semanas de alcance.

---

## 1. Correcciones al Documento Maestro

1. **La identidad se ancla al `ig_user_id`, no al @handle.** La API entrega en cada comentario el ID interno del autor (`from.id`). El handle se guarda como historial porque puede cambiar a mitad de temporada.
2. **Nuevo estado de jugador `disqualified`** para acoso, doxxing o multicuenta probada. Es distinto de `eliminated`: no vota ni entra al repechaje.
3. **Las alianzas usan el ID `J-XXXX`, nunca @etiquetas.** Así no hay spam de notificaciones, no se puede arrastrar a alguien que no consintió y el input se valida mejor.
4. **No se usan encuestas de Historias como input.** Meta no expone por API quién votó qué, así que no son auditables. Todos los votos van por comentario con formato.
5. **El Episodio 0 lleva la marca `SIMULACIÓN` permanente** en cada fotograma. Es la única excepción a la Regla 1 y es explícita.
6. **Todo comentario de juego incluye el ID del jugador.** Miles de comentarios idénticos ("A", "QUIERO JUGAR") pueden activar el filtro antispam de Instagram, y el ID además deja el tablero público legible. Si el ID del comentario no coincide con la cuenta que lo escribe, el input es inválido, así que comentar el ID de otro no tiene efecto.

### Modelo de datos del jugador (v2)

```json
{
  "season_id": "S01",
  "player_id": "J-0412",
  "ig_user_id": "17841400000000000",
  "handle_history": [{"handle": "@usuario", "seen_at": "2027-01-05T03:12:44Z"}],
  "registration": {"status": "accepted", "comment_id": "180...", "timestamp": "2027-01-05T03:12:44Z"},
  "player_status": "active",
  "flags": {"returned": false, "shield_g4": false, "traitor_g3": false},
  "duo_id": null,
  "g1_door": null,
  "history": [
    {"game": "G1", "input": "B", "input_comment_id": "180...", "result": "survived", "audit_ref": "evt_000231"}
  ]
}
```

Estados de jugador: `active`, `eliminated`, `withdrawn`, `disqualified`, `winner`. Se elimina `qualified`, que no tenía uso.

---

## 2. Arquitectura de la temporada

### 2.1 Mapa de juegos

| Sem | Juego | Canal de input | Tipo | Regla de 3 segundos |
|---|---|---|---|---|
| 1 | **G1 · Las Tres Puertas** | Comentario público | Azar + lectura de multitudes | "Si tu puerta se cierra, caes. Cuanta más gente en tu puerta, más probable que se cierre." |
| 2 | **G2 · El Muelle (Pactos)** | Comentario público | Social | "Si tu pacto no es mutuo, caes." |
| 3 | **G3 · El Confesionario (Dilema)** | DM secreto | Social | "Si confías y tu pareja te traiciona, caes. Si ambos traicionan, caen los dos." |
| 3½ | **Repechaje · La Grieta** | Comentario público (solo eliminados) | Azar | "Los números más cercanos al número de la Grieta vuelven." |
| 4 | **G4 · El Objetivo** | DM secreto | Lógica | "Gana quien más se acerque a ⅔ (o ½) del promedio de todos." |
| 5 | **G5 · La Balsa** | DM secreto | Social | "Los más señalados por los demás caen." |
| 6 | **G6 · El Último Número** | DM secreto | Lógica | "Gana el número más bajo que nadie más eligió." |

### 2.2 Cupos que escalan

Los juegos G1–G3 eliminan por su propia regla, sin cupo. Del G4 en adelante el cupo sale de la cantidad de elegibles (E), para que la temporada termine en 1 sea cual sea la escala:

- **Cupo G4:** `S4 = max(⌈E^(2/3)⌉, escudados)`
- **Cupo G5:** `S5 = min(16, max(3, ⌈√E⌉))` (finalistas)
- **G6:** 1 ganador.
- **Repechaje:** `R = max(1, ⌈0.10 × supervivientes_G3⌉)` regresan.

En video se anuncia solo el número ("Quedan 1,991. Solo pasan 159."). La fórmula vive en el reglamento para quien quiera auditarla.

### 2.3 Regla del Último Aliento (red de seguridad, publicada en el reglamento)

Si una prueba dejaría menos de `M = max(2, ⌈0.10 × elegibles⌉)` supervivientes (G1–G3), o 0 supervivientes (G4–G6), se revive a los eliminados **por regla** (nunca a los AFK) en orden de mérito de esa prueba. Si no hay orden de mérito, se usa el orden por semilla (§5.3) hasta alcanzar M.
Si una prueba recibe menos de 2 inputs válidos, se repite una vez con 24 h de ventana extra. Si vuelve a fallar, la temporada se declara **anulada** y se publica el registro de auditoría.

### 2.4 Trayectoria esperada (supuestos de §6)

| Etapa | N = 200 | N = 2,000 | N = 20,000 |
|---|---|---|---|
| Inscritos | 200 | 2,000 | 20,000 |
| Tras G1 | ~78 | ~780 | ~7,800 |
| Tras G2 | ~34 | ~350 | ~3,510 |
| Tras G3 | ~18 | ~181 | ~1,810 |
| + Repechaje | +2 → 20 | +19 → 200 | +181 → 1,991 |
| Tras G4 | 8 | 35 | 159 |
| Finalistas (G5) | 3 | 6 | 13 |
| Ganador (G6) | 1 | 1 | 1 |

---

## 3. Calendario

### 3.1 Ciclo semanal (hora CDMX)

| Día | Hora | Evento | Responsable |
|---|---|---|---|
| Lun | 20:00 | **Reel REGLAS** (Ep N·a): resultado del voto comunitario, reglas del Juego N y apertura de ventana | Publicación |
| Lun–Mié | cada 12 h | **Historia "Conteo oficial"** con el estado agregado (en juegos públicos: % por opción). Todos reciben la misma información y nadie depende de tener scripts | Motor → plantilla |
| Mié | 18:00 | Historia "Quedan 2 horas" + aviso en el Canal de difusión | Plantilla |
| Mié | 20:00 | **Cierre** de la ventana de jugadores | Motor |
| Mié | 20:10 | Se publica la ronda drand prefijada (semilla) | Externo |
| Mié 20:15 → Jue | ≤ 8 h | Resolución, auditoría, paquete de hechos, guion, render y revisión | Pipeline (§5) |
| Jue | 20:00 | **Reel VEREDICTO** (Ep N·b) + carrusel **El Muro** + apertura del **voto comunitario** del juego N+1 | Publicación |
| Sáb | 20:00 | Cierre del voto comunitario | Motor |
| Dom | — | Historia de estado; producción del Ep (N+1)·a | Pipeline |

El camino crítico es de 24 h (Mié 20:00 → Jue 20:00). El objetivo interno es de 8 h y deja 16 h de colchón.
**Plan de contingencia:** si el render falla, el jueves a las 20:00 se publican igualmente El Muro y una Historia con el resultado, y el Reel sale el viernes. Los resultados nunca esperan al video.

### 3.2 Fechas

| Fecha | Hito |
|---|---|
| 16 nov – 13 dic 2026 | Construcción (§7.1) y calentamiento de la cuenta |
| 14 – 20 dic | **Gate Go/No-Go** (§7.2) |
| 21 dic – 3 ene | Colchón: teasers de fiestas y margen para el App Review |
| **Lun 4 ene 2027** | **Convocatoria** (ventana de inscripción de 6 días, cierra Dom 10 ene 20:00) |
| Lun 11 ene | Ep 1a: censo + G1 |
| Jue 14 ene | Ep 1b: veredicto G1 |
| Lun 18 / Jue 21 ene | G2 |
| Lun 25 / Jue 28 ene | G3 · Jue 28 abre La Grieta (repechaje) |
| Lun 1 / Jue 4 feb | G4 (con retornados) |
| Lun 8 / Jue 11 feb | G5 · se anuncian los finalistas |
| Lun 15 / **Jue 18 feb 2027** | **G6 · FINAL** |

---

## 4. Reglamentos

### 4.0 Inscripción (Semana 0)

- **Input:** comentario principal en el Reel de convocatoria con `ENTRO` + un emoji a elección (por ejemplo `ENTRO 🔥`). El emoji da variedad para esquivar el filtro antispam.
- **Válido si:** cuenta principal (no respuesta), timestamp anterior al cierre y cuenta no vista antes en la temporada. Duplicados → `duplicate`. Texto ofensivo → `rejected`.
- **IDs:** se asignan al cierre en orden de timestamp ascendente; si dos coinciden, gana el `comment_id` menor. El formato es `J-0001`, con 5 dígitos si se superan los 9,999.
- **Verificación del ID:** respuesta automática y espaciada al comentario de inscripción (`✅ J-0412`) mediante la API de comentarios. Respaldo: carrusel "Directorio" ordenado por alias. El vínculo handle↔ID ya es público en ese contexto, porque el usuario comentó en público.
- **Censo:** total de inscritos en el Ep 1a, junto al hash del archivo de censo.

### 4.1 G1 · LAS TRES PUERTAS — ficha técnica completa

| Campo | Especificación |
|---|---|
| **Nombre** | Las Tres Puertas |
| **Objetivo** | Elegir una puerta que no se cierre |
| **Elegibles** | Todos con `registration.status = accepted` y `player_status = active` |
| **Input exacto** | Comentario principal en el Reel Ep 1a: `J-XXXX A`, `J-XXXX B` o `J-XXXX C`. Regex sobre el texto normalizado (trim, mayúsculas, espacios colapsados): `^J-(\d{4,5})\s+([ABC])$`. El ID debe pertenecer al `ig_user_id` autor. Las respuestas a otros comentarios no cuentan. |
| **Múltiples comentarios** | Cuenta el **último comentario válido** existente en la captura oficial de cierre. Se puede cambiar de puerta hasta el final; borrar un comentario lo anula. |
| **Ventana** | Lun 11 ene 2027 20:00 CDMX (02:00 UTC del 12) → Mié 13 ene 2027 20:00:00 CDMX (02:00:00 UTC del 14). Solo cuentan comentarios con `timestamp < cierre`. |
| **Captura oficial** | Lecturas cada 10 min durante la ventana y captura final entre el cierre y cierre+6 h. Vale lo que exista en la captura final con hora anterior al cierre. |
| **Fórmula de resolución** | `n_A, n_B, n_C` = votos válidos por puerta; `p_X = n_X / (n_A+n_B+n_C)`. Semilla: aleatoriedad de la ronda drand `quicknet` cuyo tiempo es el primero ≥ cierre+10 min. El número de ronda se publica en el caption del Ep 1a, antes de abrir. `u = int(primeros 13 hex de randomness, 16) / 16^13` ∈ [0,1). Se cierra **A** si `u < p_A`; **B** si `u < p_A + p_B`; si no, **C**. Quien eligió la puerta cerrada → `eliminated`. |
| **Propiedad clave** | La probabilidad de cierre es igual a la popularidad. Una puerta con 0 votos nunca se cierra. El conteo público convierte el azar en lectura de multitudes. |
| **Desempate** | No hay empates en la elección. Para ordenar revividos (Último Aliento) se usa el orden por semilla (§5.3). |
| **Impacto comunitario** | Ninguno: todavía no hay fantasmas. La puerta de cada superviviente (`g1_door`) queda como **etiqueta narrativa** ("los de la B") sin efecto mecánico. |
| **AFK** | Sin input válido → `eliminated` con motivo `afk` ("No cruzó ninguna puerta"). |
| **Último Aliento** | Si quedan menos de `max(2, ⌈0.10 × elegibles⌉)` supervivientes, se revive a jugadores de la puerta cerrada por orden de semilla. |
| **Auditoría** | Caption del Ep 1a: hash SHA-256 de `game_config_G1.json` (reglas congeladas) + ronda drand. Caption del Ep 1b: hash de la captura final, `n_A/n_B/n_C`, `u` y hash de la cabeza de la cadena de auditoría. Cualquiera puede verificar la ronda drand en fuentes públicas y recalcular `u`. |
| **Resultados** | **El Muro**: carrusel donde cada ID es una celda de una cuadrícula de 50 columnas (verde = vivo, gris = eliminado, ámbar = AFK). J-4127 → lámina 1, fila 83, columna 27 (fila = ⌊(n−1)/50⌋+1, columna = ((n−1) mod 50)+1), con la fórmula impresa en la portada. 5,000 IDs por lámina, hasta 4 láminas para 20,000. |

**Hechos narrativos que se extraen automáticamente** (ejemplos de arcos emergentes):
- `margen`: distancia entre `u` y el umbral más cercano ("La puerta B se salvó por 0.8 %").
- `cambios_max`: el ID que más veces cambió de puerta según las capturas, y si acertó.
- `ultimo_segundo`: el último input válido y cuántos segundos faltaban para el cierre.
- `puerta_vacia`: si alguna puerta quedó casi vacía y quién la eligió.
- `afk_total`: "La Sala se cerró con 4,213 dentro".

### 4.2 G2 · EL MUELLE (Pactos) — ficha resumida

- **Elegibles:** supervivientes del G1.
- **Input:** comentario `J-XXXX PACTO J-YYYY`. YYYY tiene que estar activo y ser distinto de XXXX.
- **Resolución:** se forma un dúo solo si X→Y **y** Y→X. Los dúos sobreviven y se registran como `duo_id` para el G3. Quien queda sin pareja → `eliminated`. AFK → `eliminated`.
- **Voto comunitario (Sem 1, jue–sáb):** **Opción 1 "Un solo intento":** cuenta el **primer** comentario válido (compromiso). **Opción 2 "Corazón libre":** cuenta el **último** (se puede cambiar de pacto a última hora y dejar a alguien varado).
- **Último Aliento:** se revive por número de propuestas recibidas y después por semilla, emparejando a los revividos entre sí por semilla.
- **Hechos:** el ID más pretendido, triángulos (A→B→C→A), pactos rotos en el último minuto.

### 4.3 G3 · EL CONFESIONARIO (Dilema) — ficha resumida

- **Elegibles:** miembros de dúos del G2.
- **Input (DM):** `J-XXXX CONFÍO` o `J-XXXX TRAICIONO`. Cuenta el último DM antes del cierre.
- **Resolución:** CONFÍO+CONFÍO → ambos sobreviven. CONFÍO+TRAICIONO → sobrevive quien traiciona (`traitor_g3 = true`). TRAICIONO+TRAICIONO → ambos `eliminated`. Si la pareja es AFK, el que jugó sobrevive.
- **Voto comunitario (Sem 2):** **Opción 1 "Botín":** quien traiciona con éxito gana un ESCUDO para el G4. **Opción 2 "Lealtad":** los dúos CONFÍO+CONFÍO ganan ESCUDO para el G4.
- **Hechos:** % de lealtad mutua, traiciones dentro de facciones de puerta ("los de la B se traicionaron entre sí").

### 4.4 Repechaje · LA GRIETA

- **Elegibles:** `eliminated` (incluidos AFK). Quedan fuera `withdrawn` y `disqualified`.
- **Input:** comentario en el Ep 3b `J-XXXX NNN` (número del 000 al 999). Cuenta el último.
- **Resolución:** `X = int(primeros 13 hex, 16) mod 1000` de la ronda drand prefijada. Distancia circular `d = min(|n−X|, 1000−|n−X|)`. Regresan los R con menor `d`, con desempate por semilla, y se marcan `returned = true`.
- **Corre en paralelo** al voto comunitario de la Semana 3.

### 4.5 G4 · EL OBJETIVO — ficha resumida

- **Elegibles:** activos, incluidos los retornados.
- **Input (DM):** `J-XXXX NN` (entero de 0 a 100).
- **Resolución:** `T = m × promedio(inputs válidos)`. Se ordena por `|n − T|`. Pasan los escudados más los mejores hasta completar `S4`. Desempate por semilla. AFK → `eliminated` (un escudado AFK sí pasa).
- **Voto comunitario (Sem 3):** `m = ⅔` u `m = ½`.
- **Hechos:** el número más elegido, quien acertó exactamente, el retornado que llegó más lejos.

### 4.6 G5 · LA BALSA — ficha resumida

- **Elegibles:** supervivientes del G4.
- **Input (DM):** `J-XXXX BALSA J-YYYY` (un activo distinto de uno mismo).
- **Resolución:** se ordena por votos recibidos, de menos a más. Pasan `S5` finalistas. Desempate: menos votos emitidos contra quienes votaron por ti; después, semilla. AFK → `eliminated`.
- **Voto comunitario (Sem 4):** **Opción 1 "Memoria":** los votos contra traidores del G3 cuentan ×2. **Opción 2 "Olvido":** todos los votos valen igual. Esta opción no se puede manipular con multicuentas, porque castiga una conducta pasada y no promueve a una persona.

### 4.7 G6 · EL ÚLTIMO NÚMERO (Final) — ficha resumida

- **Elegibles:** finalistas.
- **Input (DM):** `J-XXXX NN`.
- **Resolución:** gana el **número único más bajo**. Si ningún número es único, gana quien tenga el número más bajo entre los repetidos según el orden por semilla.
- **Voto comunitario (Sem 5):** rango `1–[número de finalistas]` (más choques, más psicología) o `1–100`.
- **Resultado:** `winner`. El resto de finalistas queda con el estado `eliminated` y la etiqueta narrativa "Finalista".

### 4.8 Voto comunitario (igual en todas las semanas)

- **Votan:** todos los `accepted` que no estén `withdrawn` ni `disqualified`, sean vivos o fantasmas. Peso 1:1, una cuenta = un voto.
- **Input:** comentario en el Reel VEREDICTO: `J-XXXX VOTO 1` o `J-XXXX VOTO 2`. Cuenta el último.
- **Resolución:** gana la mayoría simple. Si hay empate, decide la semilla. El resultado se anuncia en el Ep REGLAS siguiente.
- **Alcance:** solo opciones predefinidas en este documento. La comunidad nunca decide quién cae, solo **cómo** se juega.

### 4.9 Retiro y moderación

- **Retiro:** comentario o DM `RETIRO J-XXXX` → `withdrawn`. Es inmediato e irreversible, y quien se retira no vota.
- **Descalificación:** acoso, doxxing o multicuenta con evidencia → `disqualified`. Se registra en la auditoría con un código de motivo, sin publicar detalles.
- **Multicuenta:** está prohibida en las bases. Riesgo residual aceptado: la API no expone la antigüedad ni los seguidores de las cuentas personales (§6, E6).

### 4.10 Bases mínimas (carrusel "REGLAMENTO", fijado y destacado)

Participación gratuita y sin compra · premio simbólico, sin valor monetario · solo actividades digitales ficticias · edad mínima según los términos de Instagram · uso exclusivo de alias e IDs · derecho de retiro · reglas publicadas antes de cada juego · aleatoriedad verificable por drand · *"Esta promoción no está patrocinada, avalada ni administrada por Instagram ni Meta, ni está asociada a ellos."*

---

## 5. Flujo de datos: motor ↔ narrativa

```
Instagram (comentarios / DMs)
   │  lecturas cada 10 min + captura final
   ▼
RAW STORE ──── JSON crudo de la API, solo-añadir, SHA-256 por captura
   ▼
REGISTRY / PARSER ── ig_user_id → J-XXXX; inputs válidos o inválidos con código de motivo
   ▼
GAME ENGINE ── resolve(config, elegibles, inputs, semilla, modificadores) → resultados
   │            función pura: misma entrada ⇒ misma salida, byte a byte
   ▼
AUDIT LOG ──── cadena de hashes (cada evento lleva el prev_hash); la cabeza se publica en el caption
   ▼
FACTS PACK (NFP) ── solo IDs y agregados; cero handles; cada hecho con fact_id
   ▼
EPISODE GENERATOR (Claude) ── guion donde cada cifra o ID cita un fact_id
   ▼
FACT LINTER ── rechaza el guion si contiene números o IDs que no estén en el NFP
   ▼
RENDER (plantillas + TTS + subtítulos) → REVISIÓN HUMANA (checklist de 30 min) → PUBLICACIÓN
```

### 5.1 Reglas de permisos
- El generador de episodios **solo lee** el NFP. No tiene acceso a la base de jugadores ni a los handles.
- La narrativa solo puede influir en el futuro **eligiendo cuáles de los modificadores predefinidos** se someten a voto. Nunca toca resultados.
- `game_config_GN.json` se congela y se publica su hash **antes** de abrir la ventana. Cambiar una coma cambia el hash.

### 5.2 Facts Pack (contrato)

```json
{
  "game": "G1", "audit_head": "sha256:…",
  "totals": {"eligible": 12000, "valid_inputs": 7310, "afk": 4690, "survivors": 4820},
  "facts": [
    {"fact_id": "G1-F01", "type": "margen", "text_hint": "puerta cerrada y margen",
     "data": {"closed": "A", "u": 0.4127, "threshold": 0.4210}},
    {"fact_id": "G1-F02", "type": "cambios_max", "ids": ["J-0412"], "data": {"changes": 7, "final": "A"}}
  ]
}
```

### 5.3 Orden por semilla (desempates y revividos)
`clave(jugador) = SHA-256(randomness_drand ‖ "|" ‖ game_id ‖ "|" ‖ player_id)`, ordenada de forma ascendente. Es determinista, verificable por cualquiera y nadie puede predecirla antes del cierre.

### 5.4 Banco de assets para producción modular
- **7 escenarios** con parallax: Sala de Puertas, Muelle, Confesionario, Grieta, Tablero, Balsa y Último Cuarto.
- **Avatar determinista por ID:** `hash(ID)` → 8 cuerpos × 12 paletas × 10 accesorios = 960 combinaciones. Cada jugador puede reconocer "su" muñeco.
- **4 animaciones base:** idle, correr, celebrar y **"desconexión"**: el sprite se pixeliza y se disuelve. Es una eliminación abstracta, sin violencia gráfica, para cumplir las políticas de Meta.
- **Multitudes:** mosaicos de avatares, mapas de calor por puerta o dúo y contadores diegéticos.
- **2 plantillas de episodio:** REGLAS y VEREDICTO, con los 5 segmentos del Documento Maestro (§8) y textos dentro de la zona segura 9:16.

### 5.5 Stack recomendado
- **Motor e ingesta:** Python + SQLite con WAL y tablas solo-añadir. A 20,000 jugadores no hace falta un servidor de base de datos.
- **Video:** render programático con Remotion (React → MP4); los datos entran en JSON.
- **Voz:** ElevenLabs con una voz fija de "Anfitrión".
- **Semilla:** drand `quicknet`. `ronda = ⌊(t − genesis_time) / period⌋ + 1`, con valores tomados de `/info` de la red.

---

## 6. Simulación de estrés conceptual

### 6.1 Supuestos de la trayectoria (§2.4)
Participación por juego: G1 60 % · G2 75 % · G3 70 % (fricción del DM) · G4 80 % · G5 90 % · G6 95 %. G1: se elimina ≈ 35 % de los activos (`Σp²` con puertas casi equilibradas). G2: 60 % de los activos logra un pacto mutuo. G3, entre dúos donde ambos juegan: 45 % CC, 35 % CT, 20 % TT.

### 6.2 Escenarios adversos

| # | Escenario | Qué pasa | Respuesta del sistema |
|---|---|---|---|
| E1 | 100 % elige la puerta A en el G1 | `p_A = 1` ⇒ A se cierra con certeza y caen todos | Último Aliento revive a ⌈10 %⌉ por semilla. Narrativa: "La Sala perdonó a 1,200". |
| E2 | Nadie juega en un juego | 0 inputs | Repetición con +24 h y, si vuelve a fallar, temporada anulada con auditoría publicada |
| E3 | G2: todos le proponen pacto a un mismo jugador famoso | 1 solo dúo | Último Aliento por propuestas recibidas y luego semilla; los revividos se emparejan entre sí |
| E4 | G3: todos traicionan | 0 supervivientes | Último Aliento revive a ⌈10 %⌉ de los TT por semilla. Narrativa: "Nadie confió en nadie". |
| E5 | G4: todos eligen el mismo número | Empate total | El cupo se llena por orden de semilla. Narrativa: "Mente colmena". |
| E6 | Una persona con 20 cuentas | Se empareja consigo misma en el G2 y coordina en el G5 | Prohibido en las bases y descalificación con evidencia. El diseño limita el beneficio: el G3 obliga a decidir a ciegas por dúo y el G5 premia o castiga conducta pasada, no popularidad. **Riesgo residual aceptado.** |
| E7 | La API cae durante el cierre | No hay captura final | Reintentos hasta cierre+6 h; vale todo comentario con `timestamp < cierre`. Las lecturas cada 10 min sirven de respaldo para auditar. |
| E8 | Instagram oculta comentarios como spam | Faltan inputs | Formato con ID único, filtros de comentarios ocultos desactivados en la cuenta y prueba en el calentamiento |
| E9 | Un jugador cambia su @handle | — | Sin efecto: la identidad es `ig_user_id` |
| E10 | Falla el render del jueves | No hay Reel | El Muro y la Historia salen a las 20:00 y el Reel el viernes |
| E11 | Meta rechaza el App Review | G3–G6 sin DMs | Plan B: herramienta de automatización de DMs de un Meta Business Partner con exportación auditable. Plan C: variantes públicas de G3–G6 (debe estar decidido antes del gate). |
| E12 | Un comentario llega con hora del cierre exacto (20:00:00.000) | Caso límite | Es inválido: la regla es `timestamp < cierre`, estrictamente menor |
| E13 | Un jugador comenta el ID de otro | Intento de suplantación | Input inválido con código de motivo `id_mismatch`; puede servir como evidencia de acoso |
| E14 | Inscripción viral: 80,000 personas | Supera el diseño | Cupos por fórmula (aguanta), El Muro con 16 láminas (cabe en 20) y respuestas de ID espaciadas en unas 44 h, que es demasiado: se activa el Directorio por carrusel |

### 6.3 Pruebas del gate (simulador con 1,000 jugadores ficticios)
1. **Replay determinista:** re-resolver cada juego da salidas idénticas byte a byte.
2. **Inyección:** 5 % duplicados, 3 % spam, 2 % suplantación de ID, 1 % comentarios fuera de hora y casos E1–E5 forzados.
3. **Conservación:** en cada paso, `activos + eliminados + retirados + descalificados = inscritos`.
4. **Linter de hechos:** un guion con una cifra inventada **tiene que ser rechazado**.

---

## 7. Plan de construcción y gate

### 7.1 Semanas de construcción

| Semana | Desarrollo (Codex) | Cuenta / producción |
|---|---|---|
| 16–22 nov | App en Meta for Developers, cuenta Business, verificación de negocio · ingesta + registry + SQLite + cadena de hashes | Identidad visual, 3 teasers de lore |
| 23–29 nov | Motor G1–G6 + simulador de 1,000 ficticios · **enviar el App Review de mensajería** | Minijuego de calentamiento "¿Qué puerta elegirías?" con **ingesta real** |
| 30 nov–6 dic | Extractor del NFP + linter · avatares deterministas · plantillas de Remotion | 2.º minijuego (pactos de prueba, sin consecuencias) |
| 7–13 dic | Integración completa | **Episodio 0 (SIMULACIÓN)** cronometrado de cierre a publicación |

### 7.2 Gate Go/No-Go (14–20 dic)
- [ ] Simulador: las 4 pruebas de §6.3 en verde.
- [ ] Ingesta real: un post de calentamiento conciliado al 100 % contra un conteo manual de una muestra.
- [ ] Filtro de comentarios ocultos probado con comentarios casi idénticos.
- [ ] Episodio 0: de cierre a publicación en ≤ 8 h.
- [ ] App Review aprobado **o** Plan B/C decidido para G3–G6.
- [ ] Reglamento y bases publicados.
- [ ] (Blando) ≥ 1,000 seguidores; si no se llega, se alarga el calentamiento.

---

## 8. Decisiones pendientes (no bloquean la construcción)
1. Voz del Anfitrión (tono e idioma neutro o mexicano).
2. Nombre definitivo ("LOS JUEGOS" es provisional) y registro de marca.
3. Premio simbólico concreto (insignia, cameo en T2, título "Superviviente S01").

---

## Adenda — 14/11/2026: lanzamiento adelantado

Por decisión del productor, la convocatoria se abre **hoy** y no el 4 de enero de 2027.

- **Nombre público:** IGram Games. Riesgo aceptado: las normas de marca de Instagram prohíben "Insta"/"Gram" en nombres de productos. El nombre es un solo parámetro en `episodio0/build/guion.py`, así que cambiarlo cuesta minutos.
- **Inscripción:** 14 nov → **dom 29 nov 2026, 20:00 CDMX**. Los comentarios persisten en el post, así que la ingesta (§5) puede terminarse durante la ventana. **Es bloqueante para el 29 de noviembre.**
- **Juego 1:** lun 30 nov 2026. Con la cadencia de §3.1, los veredictos caen el **jueves 24 de diciembre (Nochebuena)** y el **jueves 31 de diciembre (Año Nuevo)**. Hay que decidir antes del 10 de diciembre si esas semanas se adelantan al miércoles o se hace una pausa de fiestas.
- **Episodio 0** pasa a ser el Reel de convocatoria (`episodio0/`). El piloto con datos simulados del gate (§7.2) se sustituye por la producción real de este episodio: pipeline de render en ≈1 minuto.
- **App Review de mensajería:** se vuelve urgente, porque el G3 caería alrededor del 14 de diciembre. Si no se aprueba antes del 7 de diciembre, se activa el Plan B o C (§6.2, E11).
