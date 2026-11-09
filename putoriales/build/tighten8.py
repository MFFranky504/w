import json,subprocess,numpy as np,wave
SR=44100
d=json.load(open('assets8/words.json'));W=d['words']
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','assets8/voice.mp3','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,dtype=np.float32)
caps={'Uno...':0.75,'dos...':0.75,'pinche':0.0}
out=[];shift=0.0;nw=[]
pos=0  # sample position copied so far in source
src=lambda t:int(t*SR)
for i,w in enumerate(W):
    nxt=W[i+1] if i+1<len(W) else None
    nw.append([w[0],w[1]-shift,w[2]-shift])
    if nxt:
        gap=nxt[1]-w[2]
        cap=0.75 if w[0] in('Uno...','dos...') else 0.28
        if gap>cap:
            keep=cap/2
            cut_a=w[2]+keep; cut_b=nxt[1]-keep
            seg=x[pos:src(cut_a)]
            out.append(seg); pos=src(cut_b)
            # crossfade by short fade
            shift+=cut_b-cut_a
out.append(x[pos:])
y=np.concatenate(out)
# fades at joins are tiny; apply 5ms fade at each join point
join=0
json.dump({'lines':d['lines'],'words':nw},open('assets8/words_t.json','w'),ensure_ascii=False)
pcm=(np.clip(y,-1,1)*32767).astype(np.int16)
w=wave.open('assets8/voice_t.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes());w.close()
print(len(y)/SR, nw[-1])
