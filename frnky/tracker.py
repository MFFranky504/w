"""Registro de posts, reporte por categoría y plan semanal de 3 variantes."""
import datetime as dt
import json
import pathlib

from .config import CATEGORIES, POSTS_PER_DAY, VARIANTS_PER_WEEK, WEIGHTS
from .captions import cta_for

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
POSTS, IDEAS, PLANS = DATA / "posts.json", DATA / "ideas.json", DATA / "plans"


def _load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def posts():
    return _load(POSTS, [])


def ideas():
    return _load(IDEAS, [])


def _save(items):
    POSTS.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n")


def register(post_id, category, hook, today=None):
    """Reserva el siguiente CTA de la rotación para este video (idempotente)."""
    items = posts()
    for p in items:
        if p["id"] == post_id:
            return p
    p = {"id": post_id, "category": category, "hook": hook,
         "cta": cta_for(len(items)), "date": str(today or dt.date.today()),
         "metrics": {}}
    items.append(p)
    _save(items)
    return p


def log_metrics(post_id, **metrics):
    items = posts()
    p = next(p for p in items if p["id"] == post_id)
    p["metrics"].update({k: v for k, v in metrics.items() if v is not None})
    _save(items)


def score(p):
    m = p["metrics"]
    return sum(w * m.get(k, 0) for k, w in WEIGHTS.items())


def report():
    """Promedio de puntaje por categoría, de mejor a peor (solo posts con métricas)."""
    rows = {}
    for p in posts():
        if p["metrics"]:
            rows.setdefault(p["category"], []).append(score(p))
    return sorted(((c, sum(v) / len(v), len(v)) for c, v in rows.items()),
                  key=lambda r: -r[1])


def posts_on(day):
    return [p for p in posts() if p["date"] == str(day)]


def schedule_check(day=None):
    n = len(posts_on(day or dt.date.today()))
    lo, hi = POSTS_PER_DAY
    if n < lo:
        return f"Faltan videos hoy: {n}/{lo} mínimo."
    if n > hi:
        return f"Demasiados hoy: {n} (máximo {hi}); no subas más."
    return f"OK: {n} video(s) hoy (meta {lo}-{hi})."


def plan_week(monday=None):
    """3 variantes de situación (3 categorías distintas) para probar esta semana.

    Si ya hay métricas: la mejor categoría + las 2 menos probadas.
    Sin datos: rota las categorías por número de semana.
    Los días 4-7 quedan para duplicar la ganadora tras ver resultados.
    """
    today = dt.date.today()
    monday = monday or today  # el plan arranca hoy (7 días)
    used = {p["id"] for p in posts()}
    pool = [i for i in ideas() if i["id"] not in used]
    tested = {c: n for c, _, n in report()}
    ranked = [c for c, _, _ in report()]
    wk = monday.isocalendar()[1]
    rotation = [CATEGORIES[(wk + k) % len(CATEGORIES)] for k in range(len(CATEGORIES))]
    least = sorted(rotation, key=lambda c: tested.get(c, 0))
    cats = ([ranked[0]] if ranked else []) + [c for c in least if c not in ranked[:1]]
    variants = []
    for c in cats:
        idea = next((i for i in pool if i["category"] == c), None)
        if idea:
            variants.append(idea)
            pool.remove(idea)
        if len(variants) == VARIANTS_PER_WEEK:
            break
    plan = {"week": f"{monday.isocalendar()[0]}-W{wk:02d}", "monday": str(monday),
            "variants": [{k: v[k] for k in ("id", "category", "title")} for v in variants],
            "schedule": []}
    for d in range(7):
        day = str(monday + dt.timedelta(days=d))
        if d < len(variants):
            plan["schedule"].append({"date": day, "slot": variants[d]["id"]})
        else:
            plan["schedule"].append({"date": day, "slot": "ganadora (decide con `report` tras el día 3)"})
    PLANS.mkdir(exist_ok=True)
    (PLANS / f"{plan['week']}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n")
    return plan
