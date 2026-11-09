import json,subprocess,sys
def gem(q,n=1500):
    r=subprocess.run(['curl','-s','-m','100','https://generativelanguage.googleapis.com/v1beta/openai/chat/completions','-H','Authorization: Bearer proxy-injected','-H','content-type: application/json','-d',json.dumps({"model":"gemini-3.1-flash-lite","messages":[{"role":"user","content":q}],"max_tokens":n})],capture_output=True,text=True).stdout
    try: return json.loads(r)['choices'][0]['message']['content']
    except Exception: return r[:300]
def nv(q,n=400):
    r=subprocess.run(['curl','-s','-m','100','https://integrate.api.nvidia.com/v1/chat/completions','-H','Authorization: Bearer proxy-injected','-H','content-type: application/json','-d',json.dumps({"model":"minimaxai/minimax-m3.1-flash","messages":[{"role":"user","content":q}],"max_tokens":n})],capture_output=True,text=True).stdout
    try:
        m=json.loads(r)['choices'][0]['message']; return m.get('content') or m.get('reasoning_content')
    except Exception: return r[:300]
if __name__=='__main__':
    ctx="Serie animada oscura de escape room para Reels: 10 países hispanos (banderas con ojos) atrapados en cabaña nevada, termómetro 6°C bajando 3°C/hora, objetos: hacha, encendedor 'una sola chispa', cuchillo, mapa con X junto a chimenea, 5 velas, troncos húmedos, 3 leños secos. El público vota A/B/C en comentarios. Primer video tuvo pocas vistas."
    print(gem(ctx+" Dame 6 ganchos (hooks) de 0-3 segundos, texto en pantalla (máx 8 palabras) + frase del narrador grave (máx 14 palabras), en español latino, que obliguen a quedarse: usa riesgo/consecuencia, pregunta al espectador, o promesa de que casi nadie acierta. NO reveles la solución. Formato numerado breve.",900))
