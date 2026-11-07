"""resultados.csv, comparación contra la línea base y reglas de decisión (2x mediana -> 3 variaciones; <0.5x en 3 seguidos -> retirar)."""
import csv
import pathlib
import statistics

from .config import BASELINE, RETIRE_STREAK, RETIRE_X, WIN_VARIATIONS, WIN_X

PATH = pathlib.Path(__file__).resolve().parent.parent / "resultados.csv"
COLS = ["fecha", "hora", "red", "tema", "gancho", "duracion_s", "cta", "estilo", "variante", "experimento", "vistas", "retencion_3s", "pct_visto_final", "likes", "comentarios", "compartidos", "guardados"]


def rows():
    if not PATH.exists():
        return []
    with PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(**kw):
    new = not PATH.exists()
    with PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow({c: kw.get(c, "") for c in COLS})


def _n(r, k):
    try:
        return float(r[k])
    except (KeyError, ValueError, TypeError):
        return None


def decisions(net=None):
    """Aplica las reglas por tema usando la mediana de vistas de la red (o la línea base si no hay datos)."""
    data = [r for r in rows() if (net is None or r["red"] == net) and _n(r, "vistas") is not None]
    if not data:
        return ["Sin datos todavía: llena resultados.csv (vistas, likes, comentarios, compartidos, guardados)."]
    med = statistics.median(_n(r, "vistas") for r in data)
    out = [f"Mediana de vistas ({net or 'todas las redes'}): {med:.0f}"]
    by = {}
    for r in sorted(data, key=lambda r: (r["fecha"], r["hora"])):
        by.setdefault(r["tema"], []).append(_n(r, "vistas"))
    for tema, v in by.items():
        if max(v) >= WIN_X * med:
            out.append(f"GANADOR  {tema}: {max(v):.0f} vistas (>= {WIN_X}x la mediana) -> haz {WIN_VARIATIONS} variaciones más.")
        if len(v) >= RETIRE_STREAK and all(x < RETIRE_X * med for x in v[-RETIRE_STREAK:]):
            out.append(f"RETIRAR  {tema}: {RETIRE_STREAK} videos seguidos por debajo de {RETIRE_X}x la mediana.")
    return out


def by_cta():
    """Comentarios y compartidos medios por CTA (para decidir cuál rotar más)."""
    g = {}
    for r in rows():
        c, s_ = _n(r, "comentarios"), _n(r, "compartidos")
        if c is not None and s_ is not None:
            g.setdefault(r["cta"], []).append((c, s_))
    return {k: (sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v), len(v)) for k, v in g.items()}


def vs_baseline():
    out = []
    for net, b in BASELINE.items():
        d = [r for r in rows() if r["red"] == net and _n(r, "vistas") is not None]
        if "vistas_mediana" in b and d:
            out.append(f"{net}: mediana {statistics.median(_n(r, 'vistas') for r in d):.0f} vs línea base {b['vistas_mediana']}")
        elif "vistas_media" in b and d:
            out.append(f"{net}: mediana {statistics.median(_n(r, 'vistas') for r in d):.0f} vs línea base (media) {b['vistas_media']}; objetivo 400-600")
    return out or ["Aún no hay filas para comparar con la línea base."]


MIN_VIEWS, MIN_VIDEOS, HOOK_POINTS, CTA_PER_1000 = 300, 5, 10.0, 3.0


def _med(v):
    return statistics.median(v) if v else None


def ab_report(experimento):
    """Informe A/B de UNA variable. Reglas:
    - gancho: gana quien supere por >= 10 puntos la retención a 3 s (mediana), con >= 300 vistas cada uno.
    - cta: métrica = comentarios por 1.000 vistas (mediana); gana A si >= 3 y B tiene 0.
    - menos de 5 videos por variante: no se concluye."""
    data = [r for r in rows() if r.get("experimento") == experimento and r.get("variante")]
    out = []
    by = {}
    for r in data:
        by.setdefault(r["variante"], []).append(r)
    if len(by) < 2:
        return [f"Experimento «{experimento}»: faltan filas de al menos 2 variantes."]
    meds = {}
    for v, rs in by.items():
        views = [_n(r, "vistas") for r in rs if _n(r, "vistas") is not None]
        ret = [_n(r, "retencion_3s") for r in rs if _n(r, "retencion_3s") is not None]
        fin = [_n(r, "pct_visto_final") for r in rs if _n(r, "pct_visto_final") is not None]
        c1000 = [_n(r, "comentarios") / _n(r, "vistas") * 1000 for r in rs if _n(r, "comentarios") is not None and _n(r, "vistas")]
        meds[v] = dict(n=len(rs), vistas=_med(views), ret=_med(ret), fin=_med(fin), c1000=_med(c1000))
        out.append(f"  {v}: n={len(rs)} · mediana de vistas={meds[v]['vistas']} · retención 3 s={meds[v]['ret']} · visto hasta el final={meds[v]['fin']} · comentarios/1000 vistas={meds[v]['c1000']}")
    if any(m["n"] < MIN_VIDEOS for m in meds.values()):
        out.append(f"  SIN CONCLUSIÓN: hace falta >= {MIN_VIDEOS} videos por variante (hoy: " + ", ".join(f"{k}={m['n']}" for k, m in meds.items()) + ").")
        return [f"Experimento «{experimento}»:"] + out
    if experimento == "gancho":
        if any((m["vistas"] or 0) < MIN_VIEWS for m in meds.values()):
            out.append(f"  EMPATE/SIN DECISIÓN: cada variante necesita >= {MIN_VIEWS} vistas (mediana).")
        else:
            (a, ma), (b, mb) = list(meds.items())[:2]
            diff = (ma["ret"] - mb["ret"]) * (100 if ma["ret"] <= 1 else 1)
            out.append(f"  Diferencia de retención 3 s: {diff:+.1f} puntos -> " + (f"gana {a}" if diff >= HOOK_POINTS else f"gana {b}" if diff <= -HOOK_POINTS else "EMPATE: no se decide."))
    elif experimento == "cta":
        (a, ma), (b, mb) = list(meds.items())[:2]
        if ma["c1000"] >= CTA_PER_1000 and (mb["c1000"] or 0) == 0:
            out.append(f"  gana {a} (>= {CTA_PER_1000} vs 0 comentarios por 1.000 vistas)")
        elif mb["c1000"] >= CTA_PER_1000 and (ma["c1000"] or 0) == 0:
            out.append(f"  gana {b} (>= {CTA_PER_1000} vs 0 comentarios por 1.000 vistas)")
        else:
            out.append("  EMPATE: no cumple el umbral (>= 3 vs 0 por 1.000 vistas).")
    return [f"Experimento «{experimento}»:"] + out
