import json,re,sys,os,subprocess,base64,shutil,time
sys.path.insert(0,'build')
from gem import gem
EP=sys.argv[1]; STAGE=sys.argv[2]; D=f'assets{EP}'; W=f'ep{EP}'
os.makedirs(D+'/sfx',exist_ok=True);os.makedirs(W,exist_ok=True)
def js(txt):
    m=re.search(r'\{.*\}',txt,re.S);return json.loads(m.group(0))
def code(txt):
    m=re.search(r'```(?:javascript|js)?\n(.*?)```',txt,re.S);return (m.group(1) if m else txt).strip()
def gj(p,n=3):
    for i in range(n):
        try: return js(gem(p))
        except Exception as e: err=e;time.sleep(10)
    raise err
ADD="  OBLIGATORIO: mínimo 7 groserías mexicanas fuertes repartidas (pendejo, culero, chingada, verga, mamada, cabrón, hijo de puta, mierda, puto...), frases cortas y hablables (nada de lenguaje rebuscado), la línea 2 es SOLO el título hablado 'Cómo ...' (sin la palabra TÍTULO ni dos puntos), tono callejero seco, no literario."
USED="sentarse, respirar, dormir ocho horas, levantarse, ahorrar dinero, lavarse los dientes, jugar videojuegos, abrir una puerta"
if STAGE=='script':
    base=f"""Eres guionista de PUTOR.IALES (Shorts 3D absurdos: tutoriales de cosas sencillas, narrador seco y harto, groserías mexicanas fuertes, humor negro moderado, SIN discriminación ni deseo de daño real). Ya hechos: {USED}. Elige OTRO tema simple (p.ej. preparar un sándwich, cargar un teléfono, usar una cuchara, caminar, hacer una cama, encender una bombilla...) y escribe 6 líneas de locución (~70-85 palabras totales, gancho potente con insulto, línea 2 = título corto, 3 pasos escalando el absurdo, remate de humor negro)."""+ADD+""" Pasos en 'usted', gancho en 'tú'. Palabras clave de cada línea ÚNICAS en el guion. Da también 6 gags visuales 3D animables (uno por línea) y el nombre de un personaje/escenario nuevo."""
    a=gj(base+'\nJSON: {"tema":"","lineas":[],"gags":[],"escenario":""}')
    c=gj("ABOGADO DEL DIABLO. Critica sin piedad este guion (gancho, ritmo, riesgo de moderación, repetición, claridad del gag) y devuelve la versión CORREGIDA final, mismas reglas (6 líneas, ~70-85 palabras, palabras ancla únicas, sin tuteo/usted mezclado en pasos, remate sin desear daño real). OBLIGATORIO: mínimo 7 groserías mexicanas fuertes repartidas (pendejo, culero, chingada, verga, mamada, cabrón, hijo de puta, mierda, puto...), frases cortas y hablables (nada de lenguaje rebuscado), la línea 2 es SOLO el título hablado 'Cómo ...' (sin la palabra TÍTULO ni dos puntos), tono callejero seco, no literario.\n"+json.dumps(a,ensure_ascii=False)+'\nJSON: {"debilidades":[],"tema":"","lineas":[],"gags":[],"escenario":""}')
    for _ in range(4):
        n=len(' '.join(c['lineas']).split())
        if 62<=n<=100: break
        c=gj(f"El guion tiene {n} palabras y DEBE tener entre 70 y 85 (Short de ~28 s). Reescríbelo con esa extensión: líneas de 12-16 palabras cada una (la línea 2 puede ser corta), manteniendo groserías fuertes, humor negro y reglas. JSON {{\"tema\":\"\",\"lineas\":[6],\"gags\":[6],\"escenario\":\"\"}}\n"+json.dumps(c,ensure_ascii=False))
    json.dump(c,open(W+'/script.json','w'),ensure_ascii=False,indent=1);json.dump(c['lineas'],open(D+'/lines.json','w'),ensure_ascii=False)
    print(c['tema'],'|',c['escenario']);print('\n'.join(c['lineas']))
if STAGE=='voice':
    t=open('build/tts7.py').read();a=t.index('LINES=[');b=t.index(']\ntext=')
    t=t[:a]+'LINES='+open(D+'/lines.json').read()+'\ntext='+t[b+len(']\ntext='):]
    t=t.replace('assets7/',D+'/');open('build/_tts.py','w').write(t)
    subprocess.run(['python3','-I','build/_tts.py'],check=True,capture_output=True)
    subprocess.run(['python3','-I','-c',open('build/tighten7.py').read().replace('assets7/',D+'/')],check=True,capture_output=True)
    w=json.load(open(D+'/words_t.json'))['words'];print(len(w),'words, end',round(w[-1][2],1))
