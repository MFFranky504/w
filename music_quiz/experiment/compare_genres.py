"""Compare genres (and hooks) from your own post results.  usage: python3 experiment/compare_genres.py experiment/results.csv [genre|hook]
Uses medians (tiny audiences => averages get dominated by one post). Warns when a group has fewer than 3 posts."""
import csv, sys, statistics as st
from collections import defaultdict
path = sys.argv[1]; key = sys.argv[2] if len(sys.argv) > 2 else "genre"
rows = [r for r in csv.DictReader(open(path)) if r.get("comments", "").strip() != ""]
g = defaultdict(list)
for r in rows: g[(r["platform"], r[key])].append(r)
num = lambda r, k: float(r[k] or 0)
print(f"{'plataforma':10} {key:12} {'n':>2} {'coment. (mediana)':>18} {'coment/1k vistas':>17} {'likes (med.)':>13} {'vistas (med.)':>14}")
for (plat, k), rs in sorted(g.items()):
    cm = st.median(num(r, "comments") for r in rs); vw = st.median(num(r, "views") for r in rs); lk = st.median(num(r, "likes") for r in rs)
    per1k = sum(num(r, "comments") for r in rs) / max(sum(num(r, "views") for r in rs), 1) * 1000
    print(f"{plat:10} {k:12} {len(rs):>2} {cm:>18.1f} {per1k:>17.1f} {lk:>13.1f} {vw:>14.1f}" + ("   <- pocas muestras (<3)" if len(rs) < 3 else ""))
