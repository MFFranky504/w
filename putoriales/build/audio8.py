import numpy as np, wave, json, subprocess, re
SR=44100
words=json.load(open('assets8/words_t.json'))['words']
END=words[-1][2]; D=END+1.5; N=int(SR*D)
norm=lambda x:re.sub(r"[^a-záéíóúñü]","",x.lower())
def K(w,n=0):
    c=0
    for x in words:
        if norm(x[0])==norm(w):
            if c==n: return x[1]
            c+=1
    raise KeyError(w)
def add(t,x,g=1.0):
    i=int(t*SR)
    if i<0 or i>=N: return
    x=x*g; j=min(N,i+len(x)); sfx[i:j]+=x[:j-i]
sfx=np.zeros(N)
def _unused(t,x,g=1.0):
    i=int(t*SR); x=x*g
    j=min(N,i+len(x)); sfx[i:j]+=x[:j-i]
def tt(d): return np.arange(int(d*SR))/SR
def env(d,a=0.005,r=None):
    t=tt(d); r=r or d*0.8
    return np.minimum(t/a,1)*np.exp(-t/ (r/4))
def sweep(f0,f1,d,wave_='sin',g=1.0):
    t=tt(d); f=f0*(f1/f0)**(t/d); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph) if wave_=='sin' else np.sign(np.sin(ph))*0.6
    return s*env(d)*g
def noise(d,lp=0.2,g=1):
    n=np.random.RandomState(1).randn(int(d*SR));
    k=int(1/lp) if lp<1 else 1
    n=np.convolve(n,np.ones(k)/k,mode='same'); return n*g
def whoosh(d,up=True):
    n=noise(d,0.08); t=tt(d); e=np.sin(np.pi*(t/d))**2
    return n*e*0.9
def boom(d=0.6): return sweep(110,38,d,g=1.3)+noise(d,0.02,0.3)*env(d,0.001,0.3)
def tick(f=1800,d=0.04): return np.sin(2*np.pi*f*tt(d))*env(d,0.001,d)
def bell(f=880,d=1.0):
    t=tt(d); return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.76*t)+0.3*np.sin(2*np.pi*f*5.4*t))*np.exp(-t*4)*0.5
def thud(d=0.3): return sweep(160,50,d,g=1.4)
def boing(f0=200,f1=700,d=0.4): 
    t=tt(d); f=f0+(f1-f0)*np.sin(np.pi*t/d*0.5)**2*0+ (f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f+40*np.sin(t*60))/SR
    return np.sin(ph)*env(d,0.005,d)*0.8
def trombone(f,d,g=0.6):
    t=tt(d); fv=f*(1+0.01*np.sin(t*40)); ph=2*np.pi*np.cumsum(fv*(1-0.12*(t/d)))/SR
    s=np.sign(np.sin(ph))*0.5+np.sin(ph)*0.5
    return np.convolve(s,np.ones(12)/12,mode='same')*np.minimum(t/0.03,1)*np.minimum((d-t)/0.05,1)*g


def rasp(d,f0=180,f1=70):
    t=tt(d); f=f0*(f1/f0)**(t/d); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sign(np.sin(ph))*(0.6+0.4*np.sin(2*np.pi*38*t)); n=noise(d,0.25,0.4)
    return (s*0.7+n)*np.minimum(t/0.01,1)*np.minimum((d-t)/0.15,1)
def squeak(d=0.12,f=900): return sweep(f,f*1.8,d,g=0.6)*np.sin(np.pi*tt(d)/d)
def pop(): return noise(0.18,0.4,1.3)*env(0.18,0.001,0.1)+sweep(1400,120,0.18,g=1.0)

def load(name,gain=1.0,start=0.0,dur=None):
    cmd=['ffmpeg','-v','error','-ss',str(start)]+(['-t',str(dur)] if dur else [])+['-i',(next(p for p in (f'assets8/sfx/{name}.mp3',f'assets7/sfx/{name}.mp3',f'assets6/sfx/{name}.mp3',f'assets5/sfx/{name}.mp3',f'assets5/sfx/{name}.mp3',f'assets3/sfx/{name}.mp3') if __import__('os').path.exists(p))),'-ac','1','-ar',str(SR),'-f','f32le','-']
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,dtype=np.float32).astype(np.float64)
    pk=np.abs(x).max()+1e-9
    return x/pk*gain
def addfx(t,name,g=1.0,start=0.0,dur=None): add(t,load(name,1.0,start,dur),g)
T_HOOKEND=K('cómo')-0.3
T_LOC=K('localice');T_POMO=K('pomo');T_CUL=K('culero');T_ARR=K('arrancárselo');T_GIRE=K('gire');T_EMP=K('empuje');T_RAIN=K('lloviendo');T_FELI=K('felicidades');T_BLOQ=K('bloquear')
CUTS=[0,K('mueble')-0.1,K('aprende'),K('pendejo')-0.2,T_HOOKEND,T_LOC,K('pomo')-0.1,T_CUL-0.1,K('cerebro')-0.1,T_ARR-0.2,T_GIRE,K('fuerza')-0.1,K('escapar')-0.4,T_EMP,T_RAIN-0.1,K('mamada')-0.2,T_FELI,K('cagarla')-0.2,T_BLOQ-0.5,T_BLOQ+0.55]
for c in CUTS[1:]: add(c-0.04,whoosh(0.3),0.3)
SWS={'pendejo','maldita','culero','chingada','mamada','verga','cagarla'}
for w in words:
    if norm(w[0]) in SWS:
        i=int((w[1]-0.02)*SR); x=boom(0.5)*0.5; sfx[i:i+len(x)]+=x[:N-i]
addfx(0.1,'zombie',0.5,0,1.5)
add(K('cómo')-0.02,boom(0.7),0.8); add(K('cómo')+0.05,bell(988,0.9),0.25)
add(T_LOC,thud(0.3),0.8); addfx(T_LOC,'springs',0.5,0,0.8)
for k in range(8): add(T_LOC+0.5+0.35*k,thud(0.12),0.4)
addfx(T_POMO+0.2,'boing',0.9,0,0.9); addfx(T_CUL,'scream',0.9,0,1.2)
addfx(T_ARR,'rip',1.0,0,1.2); addfx(T_ARR+0.2,'boing',0.5,0,0.5)
addfx(T_GIRE,'scream',0.8,0,1.2)
for k in range(10): add(T_GIRE+0.3+0.2*k,tick(300+30*k,0.06),0.5)
addfx(T_EMP,'creak',0.9,0,2.0)
addfx(T_RAIN-0.2,'keys',1.0,0,3.0)
addfx(K('felicidades'),'ping',0.5,0,0.5)
addfx(T_BLOQ-0.2,'slam',1.0,0,1.5); add(T_BLOQ,boom(0.9),1.0); addfx(T_BLOQ+0.1,'boing',0.5,0,0.6)
add(END+0.08,boom(0.7),0.9); addfx(END+0.1,'trombone',0.9,0,1.4)
m=subprocess.run(['ffmpeg','-v','error','-ss','175','-t',str(D),'-i','assets/music.m4a','-vn','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
mus=np.zeros(N); mm=np.frombuffer(m,dtype=np.float32).astype(np.float64); mus[:min(N,len(mm))]=mm[:N]
fi=int(0.4*SR); mus[:fi]*=np.linspace(0,1,fi)
fo=int(1.4*SR); mus[-fo:]*=np.linspace(1,0,fo)
mus*=0.065
v=subprocess.run(['ffmpeg','-v','error','-i','assets8/voice_t.wav','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
voice=np.frombuffer(v,dtype=np.float32).astype(np.float64)
vo=np.zeros(N); vo[:min(N,len(voice))]=voice[:N]
envv=np.convolve(np.abs(vo),np.ones(int(0.1*SR))/int(0.1*SR),mode='same'); duck=1-0.5*np.clip(envv*8,0,1)
mix=vo+sfx*0.42*(1-0.25*np.clip(envv*8,0,1))+mus*duck
mix/=max(1.0,np.abs(mix).max()/0.95)
pcm=(mix*32767).astype(np.int16)
w=wave.open('build/mix8.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes());w.close()
print('ok',np.abs(mix).max(),D)
