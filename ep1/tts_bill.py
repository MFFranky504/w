import json,subprocess,os,time,re,sys
sys.argv=['x']; import importlib
src=open('render.py').read(); m=re.search(r"SUBS = (\[.*?\])\n\ndef subs",src,re.S); SUBS=eval(m.group(1))
E_="https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128"
def tts(path,text,voice,model="eleven_multilingual_v2",st=.5,sty=.45):
    b={"text":text,"model_id":model,"voice_settings":{"stability":st,"similarity_boost":.8,"style":sty,"speed":.95}}
    for _ in range(3):
        subprocess.run(["curl","-s","-m","90","-o",path,E_%voice,"-H","xi-api-key: proxy-injected","-H","content-type: application/json","-d",json.dumps(b)])
        if os.path.getsize(path)>3000: return True
        time.sleep(10)
    print("FAIL",path,open(path,'rb').read(200)); return False
BILL="pqHfZKP75CvOlQylNhV4"
plan=[]
for i,(t0,t1,s) in enumerate(SUBS):
    if 9.8<=t0<16.5: continue
    s=s.replace('ESCAPE: WORLD SURVIVAL','Escape: World Survival').replace('...','... ')
    s=re.sub(r'^([ABC]): ',r'\1... ',s)
    plan.append((i,t0,s))
nxt=lambda i:SUBS[i+1][0] if i+1<len(SUBS) else 88
out=[]
for i,t0,s in plan:
    p=f"v2/n{i:02d}.mp3"
    if not os.path.exists(p) or os.path.getsize(p)<3000: tts(p,s,BILL)
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout or 0)
    out.append((p,t0,d,nxt(i)-t0)); print(p,t0,round(d,2),'slot',round(nxt(i)-t0,2),s[:30])
json.dump(out,open('v2/plan.json','w'))
tts("v2/d1.mp3","Tenemos que hablar. Ahora.","N2lVS1w4EtoT3dr4eOWO",st=.4,sty=.5)
tts("v2/d2.mp3","¡Aquí se viene a pelear!","SOYHLrjzK2X1ezoPC6cr",st=.35,sty=.6)
tts("v2/d3.mp3","Ya no queda nada por hacer...","cjVigY5qzO86Huf0OWal",st=.5,sty=.4)
