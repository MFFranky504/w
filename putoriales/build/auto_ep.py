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
if STAGE=='code':
    s8=open('scene8.html').read()
    head=s8[:s8.index("// ---------- room: moldy hallway")].replace('assets8/',D+'/')
    hero=s8[s8.index("// ---------- hero"):s8.index("// ---------- timeline")]
    hero=re.sub(r"\[\[0\.3,0\.82,0\.1\].*?\}\);\n","",hero,flags=re.S)
    ui=s8[s8.index("// ---------- overlays + subtitles"):]
    ui=ui.replace("[[T_BLOQ,1],[T_ARR,0.7],[T_EMP,0.6],[T_HOOKEND,0.5]]","FLASH").replace("K('localice')+0.8","PILL[1]").replace("t>=K('cómo')+1.5","t>=PILL[0]").replace("const T3=K('cómo');","const T3=K(TITLE_WORD);")
    ui=ui.replace("function pop(","hook.innerHTML='<b>'+HOOK_TEXT+'</b>';title.innerHTML=TITLE_HTML;pill.textContent=PILL_TEXT;\nfunction pop(",1)
    ui+="\nwindow.getMeta=()=>({cuts:CUTS,sw:swT});\n"
    # template pre-declares
    pre="let TN=0;\nconst wordAt=t=>words.find(w=>t>=w[1]&&t<w[2]+0.02);\nconst P=(a,b,k)=>a.map((v,i)=>lerp(v,b[i],k));\n"
    room=s8[s8.index("// ---------- room: moldy hallway"):s8.index("// ---------- hero")]
    tail=s8[s8.index("// ---------- timeline"):s8.index("// ---------- overlays + subtitles")]
    for l in ["let TN=0;\n","const wordAt=t=>words.find(w=>t>=w[1]&&t<w[2]+0.02);\n","const P=(a,b,k)=>a.map((v,i)=>lerp(v,b[i],k));\n"]: tail=tail.replace(l,"")
    open(W+'/tpl_head.js','w').write(head+hero+pre);open(W+'/tpl_ui.js','w').write(ui)
    sc=json.load(open(W+'/script.json'));words=json.load(open(D+'/words_t.json'))['words']
    wl=' '.join(f"{w[0]}@{w[1]:.1f}" for w in words)
    API="""API disponible en el ámbito del módulo (three.js r170 ya importado como THREE): helpers clamp(x,a,b), seg(t,a,b)->0..1, lerp, eio/eout/ein/eback (easings), mat(color,opts) (MeshStandard flat), mk(geo,mat,x,y,z,parent) (Mesh con sombras), grp(x,y,z,parent), V(x,y,z), rnd(i), canvasTex(w,h,drawFn(ctx,w,h)) (texto/dibujo en canvas; .userData.c es el canvas; .needsUpdate=true para redibujar), scene, cam, renderer; luces ya creadas: hemisphere, moonL (direccional con sombra), warm (PointLight) — puedes añadir más; K(palabra,n=0)=tiempo en segundos de la palabra n-ésima (normalizada sin acentos de puntuación; con acentos sí) del guion; END (fin de la voz); norm(). Personaje (ya construido, NO lo recrees): hero(group raíz, pies en y=0), pelvis(y=1.8), torsoP, torso(mesh), arms[0..1] (grupos hombro; rotation.x negativo = brazo adelante; scale.y estira), neck, headP, head, legs[{th,kn}] (th.rotation.x=-a muslo adelante; kn.rotation.x=a rodilla), eyeRig[{e,pup,spiral,lid,bag,brow,s}] (lid.rotation.x 0..1.4 cierra), mouth(scale.y abre), skinM(material piel), PJ/PJP (materiales de camiseta/pantalón: PJ.color.set(0x...)), HP (Vector3 posición mundo de la cabeza, actualizada al final de applyHero), HEROPOS. Ya declarados (NO los redeclares): TN (tiempo actual de la voz), wordAt(t), P(a,b,k) lerp de arrays. Ya existen y puedes reutilizar: HANDS,pizzas,beard,ZZ,sheep? NO (ignóralos; no los muestres). Debes DEFINIR: const T_HOOKEND (fin del gancho, ~K de la palabra del título menos 0.3); const SW=new Set([...palabras groseras normalizadas sin acentos ni puntuación... usa norm()]); const isSW=w=>SW.has(norm(w)); const swT=words.filter(w=>isSW(w[0])).map(w=>w[1]); (words es el array [[palabra,ini,fin],...] ya cargado); const blinks=[...]; function applyHero(t) (posiciona/anima hero y termina con hero.updateMatrixWorld(true);head.getWorldPosition(HP);hero.getWorldPosition(HEROPOS); usa TN y wordAt para la boca); function applyProps(t); function applyEffects(t){}; const CUTS=[0,...] (tiempos de inicio de cada plano, un cambio de plano cada 1-2 s, crecientes); const shots=[(u,t)=>({p:[x,y,z],l:[x,y,z],f:fovVertical}),...] (mismo número que CUTS); function applyCam(t) idéntica al ejemplo (usa swT, shake); const FLASH=[[tiempo,amp],...] (destellos en golpes); const HOOK_TEXT='texto corto gancho en pantalla (MAYÚSCULAS, ≤16 caracteres)'; const TITLE_HTML='TÍTULO<br>EN 2 LÍNEAS'; const TITLE_WORD='palabra de K() donde aparece el título'; const PILL_TEXT='TUTORIAL #9 · ...'; const PILL=[t0,t1]. Cámara 9:16 vertical (fov vertical 36-62). Todo determinista en función de t (sin Math.random). Los subtítulos, tarjeta final y overlays ya los pone la plantilla. El personaje mide ~4.4 unidades; el suelo y las paredes los creas tú en tu 'room'. Cámara siempre a z>0 mirando hacia -z o lateral; mantén los elementos importantes dentro de |x|<5 a distancia ~12."""
    prompt=f"""Eres programador three.js. Crea la escena 3D low-poly de un Short vertical cómico (PUTOR.IALES): tema '{sc['tema']}', escenario '{sc['escenario']}'.
Locución con tiempos (palabra@segundo): {wl}
Gags a animar (uno por línea del guion): {json.dumps(sc['gags'],ensure_ascii=False)}
{API}
Entrega SOLO un bloque ```javascript``` con: (1) tu 'room' y props nuevos (suelo, paredes, utilería con gags 3D animables), (2) la sección timeline: constantes T_*, SW, isSW, swT, blinks, applyHero, applyProps, applyEffects, CUTS, shots, applyCam, FLASH, HOOK_TEXT, TITLE_HTML, TITLE_WORD, PILL_TEXT, PILL. Mínimo 14 planos (CUTS). El código debe ser COMPLETO y extenso (≥ 220 líneas): al menos 8 props 3D distintos con gags animados (con canvasTex para carteles/pantallas), animación expresiva del personaje (brazos, piernas, cara, pose por fase) y un gag visual distinto por línea del guion. NO dejes nada como TODO ni comentarios vacíos. Usa K('palabra',n) para sincronizar; verifica que cada palabra exista en la lista con ese n. Referencia (escena anterior, estilo y estructura a seguir; adapta, no copies sus props):\n\n{room}\n{tail}"""
    out=code(gem(prompt));open(W+'/gen.js','w').write(out);print(len(out),'chars generados')
if STAGE=='build':
    g=open(W+'/gen.js').read()
    html=open(W+'/tpl_head.js').read()
    full=open('scene8.html').read()
    # wrap with original html shell
    open(f'scene{EP}.html','w').write(html+"\n"+g+"\n"+open(W+'/tpl_ui.js').read())
    print('built scene%s.html'%EP)
if STAGE=='test':
    END_=json.load(open(D+'/words_t.json'))['words'][-1][2]
    fr=[0,int(END_*10),int(END_*20),int(END_*28)]
    (curl:=subprocess.run("curl -s -o /dev/null localhost:8765/ || (setsid nohup python3 -m http.server 8765 >/dev/null 2>&1 &) ; sleep 1",shell=True))
    for attempt in range(5):
        errs=[]
        for f in fr:
            r=subprocess.run(['node','build/render.js',str(f),str(f),'1',f'build/t{EP}','8765'],env={**os.environ,'SCENE':f'scene{EP}.html'},capture_output=True,text=True)
            o=(r.stdout+r.stderr)
            if 'ERR' in o or 'Error' in o or r.returncode: errs.append(f'frame {f}: '+o.strip()[:700]);break
        if not errs: print('OK sin errores JS (intento',attempt,')');break
        print('error:',errs[0][:300])
        g=open(W+'/gen.js').read()
        fixed=code(gem(f"Corrige este código three.js (módulo; helpers y personaje ya existen y NO deben redeclararse). Error al renderizar:\n{errs[0]}\nDevuelve SOLO el bloque ```javascript``` con el código COMPLETO corregido.\n\n{g}"))
        open(W+'/gen.js','w').write(fixed)
        subprocess.run(['python3','build/auto_ep.py',EP,'build'],capture_output=True)
