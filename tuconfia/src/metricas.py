"""Registro y resumen de métricas por video y plataforma (metricas.csv).
  python3 src/metricas.py add "Dolly Parton (se negó a Elvis)" youtube 2026-11-08 vistas=1200 likes=80 guardados=15 comentarios=9
  python3 src/metricas.py resumen"""
import csv, os, sys
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'metricas.csv')
COLS = ['video', 'plataforma', 'fecha_publicacion', 'vistas', 'likes', 'guardados', 'comentarios', 'compartidos', 'seguidores_ganados', 'hora_publicacion', 'notas']
num = lambda v: float(v) if v not in ('', None) else None


def add(video, plat, fecha, **kv):
    rows = list(csv.DictReader(open(P)))
    for r in rows:
        if r['video'] == video and r['plataforma'] == plat:
            r.update({'fecha_publicacion': fecha, **{k: str(v) for k, v in kv.items()}}); break
    else: rows.append({c: '' for c in COLS} | {'video': video, 'plataforma': plat, 'fecha_publicacion': fecha, **{k: str(v) for k, v in kv.items()}})
    w = csv.DictWriter(open(P, 'w', newline=''), COLS); w.writeheader(); w.writerows(rows)


def resumen():
    rows = [r for r in csv.DictReader(open(P)) if num(r['vistas'])]
    for plat in sorted({r['plataforma'] for r in rows}):
        rs = [r for r in rows if r['plataforma'] == plat]
        m = lambda c: (sum(num(r[c]) or 0 for r in rs) / len(rs))
        print(f"{plat}: {len(rs)} videos | vistas medias {m('vistas'):.0f} | likes {m('likes'):.1f} | guardados {m('guardados'):.1f} | comentarios {m('comentarios'):.1f}")
        for r in sorted(rs, key=lambda r: -num(r['vistas']))[:3]: print('   top:', r['video'], r['vistas'], 'vistas')
    print('Con menos de 14 videos por plataforma no hay conclusión fiable (compara tendencias, no cifras sueltas).')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'add': add(a[1], a[2], a[3], **dict(x.split('=') for x in a[4:]))
    else: resumen()
