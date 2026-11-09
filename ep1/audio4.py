import numpy as np, subprocess, wave, json
SR=44100; DUR=75.0; N=int(SR*DUR); t=np.arange(N)/SR
def lo(f,extra=""):
    return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-af',extra or 'anull','-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout,np.float32)
def put(b,x,tt,g=1.0):
    i=int(tt*SR); x=x[:max(0,N-i)]; b[i:i+len(x)]+=x*g
def wr(f,x):
    with wave.open(f,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())
TR="silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse"
slots=[]; plan=json.load(open('v4plan.json')); v=np.zeros(N,np.float32); prev=0; place=[]
for i,(p,t0,s) in enumerate(plan):
    nxt=plan[i+1][1] if i+1<len(plan) else 75
    d=len(lo(p,TR))/SR; slot=nxt-t0
    tempo=min(1.12,d/(slot-.08)) if d>slot-.08 else 1.0
    x=lo(p,TR+(f",atempo={tempo:.3f}" if tempo!=1 else ""))
    st=max(t0,prev+.08); put(v,x,st); prev=st+len(x)/SR; place.append((round(st,2),round(prev,2),s))
    if st-t0>.2: print('shift',s,round(st-t0,2))
json.dump(place,open('place.json','w'),ensure_ascii=False)
wr('voice_raw.wav',v)
subprocess.run(['ffmpeg','-y','-v','error','-i','voice_raw.wav','-af','highpass=f=100,equalizer=f=140:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=0.05:ratio=4:attack=5:release=120:makeup=6,aecho=0.85:0.4:60:0.10,alimiter=limit=0.95','voice_fx.wav'])
w_=wave.open('voice_fx.wav'); vf=np.frombuffer(w_.readframes(10**9),np.int16).astype(np.float32)/32768; vf=np.pad(vf,(0,max(0,N-len(vf))))[:N]
rs=np.random.default_rng(3); sine=lambda f:np.sin(2*np.pi*f*t)
drone=(sine(55)+.8*sine(55.45)+.5*sine(82.4)+.25*sine(27.5))*(.75+.25*np.sin(2*np.pi*t/9))*.14
strings=(sine(220)+sine(233.1)+.6*sine(311.1))*(.5+.5*np.sin(2*np.pi*5.5*t))**.5*.04*np.clip((t-4)/10,0,1)
music=drone+strings
pl=np.zeros(N,np.float32)
def pulse(t0,g):
    i=int(t0*SR); n=int(.35*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*(52-18*tt/.35)*tt)*np.exp(-tt*9)*g; n=min(n,N-i); pl[i:i+n]+=x[:n]
q=0.4
while q<72: pulse(q,.35); q+=.9 if q<6 else 1.1
music+=pl
open('music_raw.wav','wb')
wr('music_raw.wav',music/np.max(np.abs(music)))
subprocess.run(['ffmpeg','-y','-v','error','-i','music_raw.wav','-af','equalizer=f=2000:t=q:w=0.7:g=-5,lowpass=f=5000','music_fx.wav'])
w_=wave.open('music_fx.wav'); music=np.frombuffer(w_.readframes(10**9),np.int16).astype(np.float32)/32768; music=np.pad(music,(0,max(0,N-len(music))))[:N]*.55
env=np.abs(vf); k=int(.2*SR); env=np.clip(np.convolve(env,np.ones(k)/k,'same')*7,0,1)
duck=1-.8*env
for a,b in [(8.9,9.2)]: duck[int(a*SR):int(b*SR)]*=.2
music*=duck*np.clip((75-t)/3,0,1)
def ld(f): return lo(f)
boom=ld('audio/boom.mp3'); creak=ld('audio/creak.mp3'); wind=ld('audio/wind.mp3')
s=np.zeros(N,np.float32)
for tt,g in [(0,.9),(1.6,.35),(3.2,.4),(4.6,.5),(6.4,.5),(52.3,.4),(53.2,.5),(64.45,.4),(71.85,.6)]: put(s,boom,tt,g)
put(s,creak,8.9,.3)
w=np.zeros(N,np.float32); i=0
while i<N: put(w,wind,i/SR,1.0); i+=len(wind)-SR
w*=.18*np.clip(t/2,0,1)*duck
for tt in np.arange(67.6,69.6,.5):
    i=int(tt*SR); n=int(.05*SR); s[i:i+n]+=rs.normal(0,1,n)*np.exp(-np.arange(n)/(.012*SR))*.25
mix=vf*1.25+music*.5+s*.35*(1-.6*env)+w
mix=np.tanh(mix*1.0)
wr('mix4.wav',mix/np.max(np.abs(mix))*.95); print('ok')
