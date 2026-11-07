import argparse
import importlib
import json
import pathlib
import sys

from . import tracker
from .captions import build_captions
from .config import BIO, CTAS, HASHTAGS, CATEGORIES

ROOT = pathlib.Path(__file__).resolve().parent.parent


def cmd_render(a):
    from .engine import render_video
    ep = importlib.import_module(f"frnky.episodes.{a.episode.replace('-', '_')}").EP
    m = ep["meta"]
    post = tracker.register(m["id"], m["category"], m["caption_hook"])
    out = ROOT / "videos"; out.mkdir(exist_ok=True)
    mp4 = render_video(ep, post["cta"], out / f"{m['id']}.mp4", ROOT / "build" / m["id"])
    caps = build_captions(m["caption_hook"], post["cta"])
    (out / f"{m['id']}.captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1) + "\n")
    print(mp4, "| CTA:", post["cta"])


def cmd_caption(a):
    p = next(p for p in tracker.posts() if p["id"] == a.id)
    for k, v in build_captions(p["hook"], p["cta"]).items():
        print(f"--- {k}\n{v}\n")


def cmd_ideas(a):
    for i, x in enumerate(tracker.ideas(), 1):
        print(f"{i}. **{x['title']}** ({x['category']}, {x.get('kind', 'nueva')})\n"
              f"   - Gancho (0-2 s): {x['hook']}\n   - Situación: {x['situation']}\n   - Remate: {x['payoff']}\n   - CTA en pantalla: «{x['cta']}»\n")


def cmd_plan(a):
    p = tracker.plan_week()
    print(f"Semana {p['week']}")
    for v in p["variants"]:
        print(f"  variante [{v['category']}] {v['id']}: {v['title']}")
    for w in p["winners"]:
        print(f"  ganadora [{w['category']}] {w['id']}: {w['title']}")
    for s in p["schedule"]:
        print(f"  {s['date']}  {', '.join(s['slots'])}")


def cmd_log(a):
    tracker.log_metrics(a.id, likes=a.likes, comments=a.comments, shares=a.shares,
                        saves=a.saves, followers=a.followers)
    print("ok", a.id, "puntaje", tracker.score(next(p for p in tracker.posts() if p["id"] == a.id)))


def cmd_report(a):
    rows = tracker.report()
    if not rows:
        print("Aún no hay métricas. Usa: python -m frnky log <id> --likes N --comments N --shares N")
    for c, s, n in rows:
        print(f"{c:9s} puntaje medio {s:6.1f}  ({n} posts)")
    if rows:
        print("Mejor categoría:", rows[0][0])


def main():
    ap = argparse.ArgumentParser(prog="frnky")
    sub = ap.add_subparsers(required=True)
    r = sub.add_parser("render"); r.add_argument("episode"); r.set_defaults(f=cmd_render)
    c = sub.add_parser("caption"); c.add_argument("id"); c.set_defaults(f=cmd_caption)
    sub.add_parser("ideas").set_defaults(f=cmd_ideas)
    sub.add_parser("plan-week").set_defaults(f=cmd_plan)
    l = sub.add_parser("log"); l.add_argument("id")
    for k in ("likes", "comments", "shares", "saves", "followers"):
        l.add_argument(f"--{k}", type=int)
    l.set_defaults(f=cmd_log)
    sub.add_parser("report").set_defaults(f=cmd_report)
    sub.add_parser("schedule").set_defaults(f=lambda a: print(tracker.schedule_check()))
    sub.add_parser("bio").set_defaults(f=lambda a: [print(f"--- {k}\n{v}\n") for k, v in __import__("frnky.config", fromlist=["BIOS"]).BIOS.items()])
    a = ap.parse_args()
    a.f(a)


main()
