"""resultados.csv, comparación contra la línea base y reglas de decisión (2x mediana -> 3 variaciones; <0.5x en 3 seguidos -> retirar)."""
import csv
import pathlib
import statistics

from .config import BASELINE, RETIRE_STREAK, RETIRE_X, WIN_VARIATIONS, WIN_X

PATH = pathlib.Path(__file__).resolve().parent.parent / "resultados.csv"
COLS = ["fecha", "hora", "red", "tema", "gancho", "duracion_s", "cta", "estilo", "vistas", "likes", "comentarios", "compartidos", "guardados"]


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
            out.append(f"{net}: media {statistics.mean(_n(r, 'vistas') for r in d):.0f} vs línea base {b['vistas_media']}")
    return out or ["Aún no hay filas para comparar con la línea base."]
