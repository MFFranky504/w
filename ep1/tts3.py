import json,os,re,hashlib,subprocess,time
src=open('render2.py').read(); SUBS2=eval(re.search(r"SUBS2 = (\[.*?\])\nR\.SUBS",src,re.S).group(1))
old=eval(re.search(r"SUBS = (\[.*?\])\n\ndef subs",open('render.py').read(),re.S).group(1))
plan_old=json.load(open('v2/plan.json')); oldmap={}
for p,t0,d,slot in plan_old:
    i=int(os.path.basename(p)[1:3]); oldmap[old[i][2].replace('ESCAPE: WORLD SURVIVAL','Escape: World Survival').replace('...','... ')]=p
BILL="pqHfZKP75CvOlQylNhV4"; os.makedirs('v3',exist_ok=True)
def tts(path,text):
    b={"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":.5,"similarity_boost":.8,"style":.45,"speed":.95}}
    for _ in range(3):
        subprocess.run(["curl","-s","-m","90","-o",path,"https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128"%BILL,"-H","xi-api-key: proxy-injected","-H","content-type: application/json","-d",json.dumps(b)])
        if os.path.getsize(path)>3000: return
        print('retry',open(path,'rb').read(160)); time.sleep(8)
out=[]
for i,(t0,t1,s) in enumerate(SUBS2):
    txt=re.sub(r'^([ABC]): ',r'\1... ',s.replace('...','... '))
    if txt in oldmap: p=oldmap[txt]
    else:
        p=f"v3/n{i:02d}.mp3"
        if not os.path.exists(p) or os.path.getsize(p)<3000: tts(p,txt)
    nxt=SUBS2[i+1][0] if i+1<len(SUBS2) else 65
    out.append((p,t0,0,nxt-t0)); print(p,t0,txt[:28])
json.dump(out,open('v3/plan.json','w'))
