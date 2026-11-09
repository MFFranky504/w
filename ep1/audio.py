import numpy as np, subprocess, wave
SR=44100; DUR=88.0; N=int(SR*DUR)
def load(f,deep=False):
    af="asetrate=44100*0.87,aresample=44100,atempo=1.1494" if deep else "anull"
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-af',af,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(r,np.float32)
def put(buf,x,t,g=1.0):
    i=int(t*SR); x=x[:max(0,len(buf)-i)]; buf[i:i+len(x)]+=x*g
def wr(f,x):
    x=np.clip(x,-1,1); s=(x*32767).astype(np.int16)
    with wave.open(f,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())
t=np.arange(N)/SR
# voice
v=np.zeros(N,np.float32)
put(v,load('audio/n1.mp3',True),.3); put(v,load('audio/n2.mp3',True),8.0)
put(v,load('audio/d1.mp3'),9.8,.8); put(v,load('audio/d2.mp3'),12.1,.8); put(v,load('audio/d3.mp3'),14.1,.7)
put(v,load('audio/vo.mp3',True),17.0)
wr('voice_raw.wav',v)
subprocess.run(['ffmpeg','-y','-v','error','-i','voice_raw.wav','-af','highpass=f=60,equalizer=f=110:t=q:w=1:g=5,equalizer=f=3500:t=q:w=1:g=-2,acompressor=threshold=0.1:ratio=3,aecho=0.8:0.55:70|140:0.25|0.12,alimiter=limit=0.9','voice_fx.wav'])
vf=np.array(wave.open('voice_fx.wav').readframes(10**9) and np.frombuffer(wave.open('voice_fx.wav').readframes(10**9),np.int16),np.float32)/32768
vf=np.pad(vf,(0,max(0,N-len(vf))))[:N]
# music
rs=np.random.default_rng(3)
def sine(f,ph=0): return np.sin(2*np.pi*f*t+ph)
swell=np.clip(t/20,0,1)*.5+.5
drone=(sine(55)+.8*sine(55.45)+.5*sine(82.4)+.3*sine(110.2)+.25*sine(27.5))*(.75+.25*np.sin(2*np.pi*t/9))*.16*swell
strings=(sine(220)+sine(233.1)+.6*sine(311.1)+.5*sine(466.2))*(.5+.5*np.sin(2*np.pi*5.5*t))**.5*.05
sfade=np.clip((t-18)/12,0,1)*np.clip((88-t)/3,0,1)*(1+1.2*np.clip((t-64)/6,0,1)*(t<76))
music=drone+strings*sfade
# pulses
pl=np.zeros(N,np.float32)
def pulse(t0,g=.5):
    i=int(t0*SR); n=int(.35*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*(52-18*tt/.35)*tt)*np.exp(-tt*9)*g; pl[i:i+n]+=x[:max(0,N-i)] if i+n<=N else x[:N-i]
tt_=17.3
while tt_<83: pulse(tt_,.45); tt_+=1.0 if tt_<75 else .7
for hb in np.arange(1.0,4.2,.9): pulse(hb,.3); pulse(hb+.25,.2)
music+=pl
# ducks: silence before reveals + under voice
env=np.abs(vf); k=int(.18*SR); env=np.convolve(env,np.ones(k)/k,'same'); env=np.clip(env*6,0,1)
duck=1-.55*env
for a,b in [(7.2,8.0),(8.8,9.5),(16.3,17.0)]: duck[int(a*SR):int(b*SR)]*=.15
music*=duck
# sfx
s=np.zeros(N,np.float32)
boom=load('audio/boom.mp3'); creak=load('audio/creak.mp3'); wind=load('audio/wind.mp3')
for tt,g in [(0.0,.6),(8.0,.9),(17.0,.9),(32.3,.6),(64.0,.7),(75.25,.7),(85.3,.8)]: put(s,boom,tt,g)
for tt in (6.4,63.4): put(s,creak,tt,.7)
w=np.zeros(N,np.float32); i=0
while i<N: put(w,wind,i/SR,1.0); i+=len(wind)-SR
w*=0.35*np.clip(t/2,0,1)*(1+np.clip((t-40)/40,0,.6))
for tt in np.arange(81.0,83.0,.5):
    i=int(tt*SR); n=int(.05*SR); s[i:i+n]+=rs.normal(0,1,n)*np.exp(-np.arange(n)/(.012*SR))*.5
# eliminated hit
mix=vf*1.0+music*.85+s*.75+w*.6
mix=mix/np.max(np.abs(mix))*.89
wr('mix.wav',mix); print('ok',len(mix)/SR)
