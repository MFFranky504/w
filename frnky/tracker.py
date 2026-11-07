"""Registro de posts, reporte por categoría y plan semanal de 3 variantes."""
import datetime as dt
import json
import pathlib

from .config import CATEGORIES, NEW_CATEGORIES, POSTS_PER_DAY, VARIANTS_PER_WEEK, WEIGHTS
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
    """Semana de 7 días con 1-2 videos al día:
    - 3 situaciones NUEVAS (una de dinero, una de trabajo, una de amor) para probar;
    - el resto, variaciones de las situaciones GANADORAS (kind="ganadora"), repetidas con otro giro.
    Los ya publicados (data/posts.json) no se repiten."""
    today = dt.date.today()
    monday = monday or today
    used = {p["id"] for p in posts()}
    pool = [i for i in ideas() if i["id"] not in used]
    new = []
    for c in NEW_CATEGORIES[:VARIANTS_PER_WEEK]:
        idea = next((i for i in pool if i["category"] == c and i.get("kind") == "nueva"), None)
        if idea:
            new.append(idea); pool.remove(idea)
    winners = [i for i in pool if i.get("kind") == "ganadora"]
    slots = new + winners
    wk = monday.isocalendar()
    plan = {"week": f"{wk[0]}-W{wk[1]:02d}", "monday": str(monday),
            "variants": [{k: v[k] for k in ("id", "category", "title")} for v in new],
            "winners": [{k: v[k] for k in ("id", "category", "title")} for v in winners],
            "schedule": []}
    lo, hi = POSTS_PER_DAY
    for d in range(7):
        day = str(monday + dt.timedelta(days=d))
        todays = slots[d * 1: d * 1 + 1]
        extra = slots[3 + d: 4 + d] if d >= 4 and 3 + d >= 7 else []       # 2.º video solo los últimos días (máx. 2 al día)
        ids = [x["id"] for x in todays + extra][:hi] or ["(repite la mejor de la semana tras `report`)"]
        plan["schedule"].append({"date": day, "slots": ids})
    PLANS.mkdir(exist_ok=True)
    (PLANS / f"{plan['week']}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n")
    return plan
