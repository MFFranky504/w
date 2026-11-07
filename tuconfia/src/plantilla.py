"""Plantilla fija de guion de TU CONF.IA:  GANCHO -> FRACASO/RECHAZO -> GIRO -> FRASE FINAL -> PREGUNTA.
Uso: python3 src/plantilla.py guiones_pendientes/gaga_despedida.json   (valida estructura, gancho y pregunta)

Cada línea del JSON lleva "rol": gancho | fracaso | giro | frase_final | pregunta.
- GANCHO (primeros 2 s, ≤ 40 caracteres): "Hasta [famoso] fue rechazado." o "[Famoso] podía [hacer X]... pero se negó."
- PREGUNTA (última línea): personal, termina en '?', pide comentario. Base: «¿Cuál fue tu mayor rechazo... y qué hiciste con él?»
- CTA en pantalla (cta.py): «Guárdalo para cuando lo necesites» + botón SUSCRÍBETE (YouTube) / SÍGUEME (TikTok, Instagram).
"""
import json, re, sys

ROLES = ['gancho', 'fracaso', 'giro', 'frase_final', 'pregunta']
PREGUNTA_BASE = '¿Cuál fue tu mayor rechazo... y qué hiciste con él?'
GANCHOS = [r'^Hasta .+ fue .+\.$', r'^.+ podía .+ pero se negó\.$']


def validar(path):
    d = json.load(open(path)); L = d['lines']; errs, avisos = [], []
    roles = [l.get('rol') for l in L]
    if any(r not in ROLES for r in roles): errs.append(f'roles inválidos: {roles}')
    # video corto: orden estricto. Video largo (>1 ciclo): fracaso y giro pueden alternarse, pero gancho va primero, frase_final y pregunta al final.
    largo = d.get('meta', {}).get('duracion_objetivo_s', 0) > 75
    if not largo and [ROLES.index(r) for r in roles if r in ROLES] != sorted(ROLES.index(r) for r in roles if r in ROLES): errs.append('los roles no siguen el orden gancho→fracaso→giro→frase_final→pregunta')
    if largo:
        mid = [r for r in roles[1:-1] if r != 'frase_final']
        if roles[-1] != 'pregunta' or roles[0] != 'gancho' or any(r not in ('fracaso', 'giro') for r in mid): errs.append('video largo: gancho al inicio, pregunta al final, fracaso/giro alternados en medio')
        if 'frase_final' in roles and roles.index('frase_final') < max(i for i, r in enumerate(roles) if r in ('fracaso', 'giro')): errs.append('frase_final debe ir después del último fracaso/giro')
    for r in ROLES:
        if r not in roles: errs.append(f'falta el rol {r}')
    g = clean(L[0]['t'])
    if roles[0] != 'gancho': errs.append('la primera línea debe ser el gancho')
    if not any(re.match(p, g.replace('...', '')) or re.match(p, g) for p in GANCHOS): avisos.append(f'el gancho no usa una fórmula fija: «{g}»')
    if len(g) > 40: avisos.append(f'gancho largo ({len(g)} car.): intenta ≤ 40 para decirlo en ~2 s')
    q = clean(L[-1]['t'])
    if not q.endswith('?'): errs.append('la última línea debe ser la pregunta')
    if 'rechazo' not in q.lower(): avisos.append('la pregunta final no menciona el rechazo (no es la pregunta base)')
    total = sum(len(l.get('tts', l['t'])) for l in L)
    limite = 760 if not largo else 3300
    if total > limite: avisos.append(f'texto largo ({total} car.): la voz pasará de ~{round(total / 17.2)} s')
    return errs, avisos


def clean(t): return t.replace('*', '')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        e, a = validar(p)
        print(p, '-> OK' if not e else '-> ERRORES', *(['\n  ✗ ' + x for x in e] + ['\n  ! ' + x for x in a]))
