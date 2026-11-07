"""Captions/títulos de TU CONF.IA por plataforma, a partir del guion (script_*.json con roles).
Uso:  python3 src/captions.py script_dolly.json            -> caption_dolly_{youtube,tiktok,instagram}.txt
      python3 src/captions.py guiones_pendientes/gaga_despedida.json
Reglas fijas: gancho del guion arriba, pregunta personal para comentarios, petición de guardar, suscribirse/seguir,
hashtags SIEMPRE iguales y con la misma capitalización: #Motivación #Superación #HistoriasQueInspiran + 1 de la persona."""
import json, os, re, sys, unicodedata

HASHTAGS_FIJOS = '#Motivación #Superación #HistoriasQueInspiran'
GUARDAR = '🔖 Guárdalo para cuando lo necesites.'
SEGUIR = {'youtube': '▶️ Suscríbete: una historia que inspira cada día.', 'tiktok': '➕ Sígueme para más historias que inspiran.', 'instagram': '➕ Sígueme para más historias que inspiran.'}
COMENTA = {'youtube': '👇 Cuéntamelo en los comentarios.', 'tiktok': '👇 Respóndeme en los comentarios.', 'instagram': '👇 Cuéntamelo en los comentarios.'}


def clean(t): return t.replace('*', '')


def hashtag_persona(nombre):
    """un único hashtag de la persona: '#' + palabras con inicial mayúscula, sin tildes (Dolly Parton -> #DollyParton)."""
    t = unicodedata.normalize('NFD', nombre)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return '#' + ''.join(w.capitalize() for w in re.sub(r'[^A-Za-z0-9 ]', ' ', t).split())


def hashtags(persona): return f'{HASHTAGS_FIJOS} {hashtag_persona(persona)}'


def caption(d, plataforma):
    L = d['lines']; m = d.get('meta', {})
    gancho = clean(next(l['t'] for l in L if l.get('rol') == 'gancho'))
    pregunta = clean(L[-1]['t']).replace('Y tú... ', '').strip()
    pregunta = re.sub(r'¿(\w)', lambda m_: '¿' + m_.group(1).upper(), pregunta, count=1)
    resumen = ' '.join(clean(l['t']) for l in L if l.get('rol') in ('fracaso', 'giro'))
    resumen = re.sub(r'\.\.\.', '…', resumen)
    persona = m.get('famoso', d.get('titulo', 'Historia').split(':')[0])
    partes = []
    if plataforma == 'youtube': partes.append(gancho)                               # el título de YouTube = gancho
    else: partes.append(gancho)
    partes.append(resumen if plataforma != 'tiktok' else resumen[:160].rsplit(' ', 1)[0].rstrip('.…,') + '…')
    partes.append(f'{pregunta} {COMENTA[plataforma]}')
    partes.append(GUARDAR + ' ' + SEGUIR[plataforma])
    partes.append(hashtags(persona))
    return '\n\n'.join(partes)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        d = json.load(open(p)); base = os.path.splitext(os.path.basename(p))[0].replace('script_', '')
        for pl in ('youtube', 'tiktok', 'instagram'):
            out = os.path.join(os.path.dirname(os.path.abspath(p)), f'caption_{base}_{pl}.txt')
            open(out, 'w').write(caption(d, pl) + '\n'); print('->', out)
