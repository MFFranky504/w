import numpy as np, subprocess, wave, json, sys
sys.path.insert(0,'v4'); from scenes import S
SR=44100
def lo(f,af='anull'): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-af',af,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout,np.float32)
def wr(f,x):
    with wave.open(f,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())
def rd(f): w=wave.open(f); return np.frombuffer(w.readframes(10**9),np.int16).astype(np.float32)/32768
TR="silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse"
clips=json.load(open('v4/clips.json'))
TAIL={'hook_lighter':.35,'speaker':.6,'arg_talk':.25,'ven_talk':.25,'per_talk':.4,'note':1.2,'opt_A':.7,'opt_B':.7,'opt_C':.9,'ask':1.3,'cta_end':1.8,'obj_map':.9,'thermo':.6}
t=.15; scenes=[]; caps=[]; vparts=[]
for (v,tit,x,who),parts in zip(S,clips):
    st=t; t+=.2
    for f,txt in parts:
        a=lo(f,TR+(",atempo=1.12" if who=="n" else "")); g=.9 if who!='n' else 1.0
        vparts.append((t,a*g)); caps.append((round(t,2),round(t+len(a)/SR,2),txt,who)); t+=len(a)/SR+.18
    t+=TAIL.get(v,.35); scenes.append((v,tit,round(st,3),round(t,3)))
DUR=t+.3; N=int(DUR*SR); tt=np.arange(N)/SR
v=np.zeros(N,np.float32)
for s0,a in vparts: i=int(s0*SR); v[i:i+len(a)]+=a[:N-i]
wr('v4/voice_raw.wav',v)
subprocess.run(['ffmpeg','-y','-v','error','-i','v4/voice_raw.wav','-af','highpass=f=90,equalizer=f=140:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=0.05:ratio=4:attack=5:release=120:makeup=6,aecho=0.85:0.35:55:0.08,alimiter=limit=0.95','v4/voice_fx.wav'])
vf=rd('v4/voice_fx.wav'); vf=np.pad(vf,(0,max(0,N-len(vf))))[:N]
sine=lambda f:np.sin(2*np.pi*f*tt)
m=(sine(55)+.8*sine(55.45)+.5*sine(82.4)+.25*sine(27.5))*(.75+.25*np.sin(2*np.pi*tt/9))*.14+(sine(220)+sine(233.1)+.6*sine(311.1))*(.5+.5*np.sin(2*np.pi*5.5*tt))**.5*.035*np.clip((tt-3)/8,0,1)
q=.3
while q<DUR-2:
    i=int(q*SR); n=min(int(.35*SR),N-i); x=np.arange(n)/SR; m[i:i+n]+=np.sin(2*np.pi*(52-18*x/.35)*x)*np.exp(-x*9)*.35; q+=1.05
wr('v4/m_raw.wav',m/np.max(np.abs(m)))
subprocess.run(['ffmpeg','-y','-v','error','-i','v4/m_raw.wav','-af','equalizer=f=2000:t=q:w=0.7:g=-5,lowpass=f=5000','v4/m_fx.wav'])
m=rd('v4/m_fx.wav'); m=np.pad(m,(0,max(0,N-len(m))))[:N]*.55
env=np.abs(vf); k=int(.2*SR); env=np.clip(np.convolve(env,np.ones(k)/k,'same')*7,0,1); duck=1-.8*env
m*=duck*np.clip((DUR-tt)/2.5,0,1)
s=np.zeros(N,np.float32); boom=lo('audio/boom.mp3'); wind=lo('audio/wind.mp3')
def put(b,x,s0,g):
    i=int(s0*SR); n=min(len(x),N-i); b[i:i+n]+=x[:n]*g
for v_,tit,s0,e in scenes:
    if v_ in('hook_lighter','speaker','rule_vote','obj_axe','note','opt_A','ask','cta_end'): put(s,boom,s0,.8 if v_=='hook_lighter' else .45)
    if v_=='cta_24h':
        for q in np.arange(s0,e,.5):
            i=int(q*SR); n=int(.05*SR); s[i:i+n]+=np.random.default_rng(int(q*10)).normal(0,1,n)*np.exp(-np.arange(n)/(.012*SR))*.25
w=np.zeros(N,np.float32); i=0
while i<N: put(w,wind,i/SR,1.0); i+=len(wind)-SR
mix=np.tanh(vf*1.25+m*.5+s*.35*(1-.6*env)+w*.16*duck)
wr('v4/mix.wav',mix/np.max(np.abs(mix))*.95)
json.dump({'dur':DUR,'scenes':scenes,'caps':caps},open('v4/timeline.json','w'),ensure_ascii=False)
print('dur',round(DUR,1)); [print(x) for x in scenes]
