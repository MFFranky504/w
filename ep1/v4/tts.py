import json,os,subprocess,time,hashlib,sys
sys.path.insert(0,'v4'); from scenes import S
BILL="pqHfZKP75CvOlQylNhV4"
def tts(p,text):
    b={"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":.5,"similarity_boost":.8,"style":.45,"speed":.95}}
    for _ in range(3):
        subprocess.run(["curl","-s","-m","90","-o",p,"https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128"%BILL,"-H","xi-api-key: proxy-injected","-H","content-type: application/json","-d",json.dumps(b)])
        if os.path.getsize(p)>3000: return
        print('retry',open(p,'rb').read(150)); time.sleep(8)
out=[]
for i,(v,tit,x,who) in enumerate(S):
    parts=[]
    for k,seg in enumerate(x.split('||')):
        if seg.startswith('@'): f,txt=seg[1:].split('|')
        else:
            txt=seg.replace('...','... '); f=f"v4/s{i:02d}_{k}.mp3"
            if not os.path.exists(f) or os.path.getsize(f)<3000: tts(f,txt)
            txt=seg
        parts.append((f,txt))
    out.append(parts)
json.dump(out,open('v4/clips.json','w'),ensure_ascii=False); print('ok',len(out))
