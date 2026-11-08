import numpy as np, wave, json, subprocess, re
SR=44100
words=json.load(open('assets4/words_t.json'))['words']
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
    cmd=['ffmpeg','-v','error','-ss',str(start)]+(['-t',str(dur)] if dur else [])+['-i',f'assets3/sfx/{name}.mp3','-ac','1','-ar',str(SR),'-f','f32le','-']
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,dtype=np.float32).astype(np.float64)
    pk=np.abs(x).max()+1e-9
    return x/pk*gain
def addfx(t,name,g=1.0,start=0.0,dur=None): add(t,load(name,1.0,start,dur),g)
T_HOOKEND=K('cómo')-0.3
T_SIT=K('siéntese'); T_STAND=K('póngase'); T_YANK=K('suelta')-0.3; T_FELI=K('felicidades')
T_EYE2=K('dos',1)-0.15
CUTS=[0,0.9,K('hasta')-0.1,K('antes')-0.15,T_HOOKEND,K('primero'),K('sí',0)-0.05,K('ahora',0),K('despacio')-0.15,K('no')-0.1,T_SIT,K('sí',1),K('ahora',1),K('ah')-0.1,T_FELI-0.1,K('regrese')-0.1,K('son')]
for c in CUTS[1:]: add(c-0.04,whoosh(0.3),0.3)
SWS={'pendejo','cabrón','puta','pinche','culero','hijo'}
for w in words:
    if norm(w[0]) in SWS:
        i=int((w[1]-0.02)*SR); x=boom(0.5)*0.5; sfx[i:i+len(x)]+=x[:N-i]
# hook: snore + clock ticks
for k in range(4): addfx(0.1+k*0.8,'zombie',0.5,0,0.8)
for k in range(10): add(0.2+k*0.3,tick(900,0.05),0.4)
add(K('barba')-0.1,sweep(120,400,0.7,g=0.5),0.7); addfx(K('levantó',0),'boing',0.7,0,0.6)
add(K('cómo')-0.02,boom(0.7),0.8); add(K('cómo')+0.05,bell(988,0.9),0.25)
# eyes
add(K('ojos')-0.25,tick(600,0.1),0.7); addfx(T_EYE2,'pop',1.0,0,0.5); addfx(T_EYE2,'boing',0.5,0,0.4)
# leg stretch + hands
addfx(K('pierna'),'boing',0.9,0,1.0)
add(K('pierna')+0.1,sweep(200,900,0.5,g=0.6),0.5)
for k in range(4): add(K('despacio')-0.1+0.1*k,thud(0.15),0.8)
addfx(K('despacio')-0.1,'springs',0.5,0,1.0)
# sit / sheep hop
addfx(T_SIT-0.2,'bleat',0.9,0,0.8); addfx(T_SIT+0.1,'bleat',0.7,0.1,0.7)
addfx(K('milagro'),'pop',0.8,0,0.5); add(K('milagro')+0.05,bell(1318,0.8),0.3)
# stand attempt + yank
add(T_STAND,sweep(150,500,0.5,g=0.5),0.6)
add(T_YANK,sweep(900,120,0.35,g=0.8),0.8); addfx(T_YANK+0.25,'boing',1.0,0,0.8); addfx(T_YANK+0.3,'crash',0.8,0,0.8)
addfx(K('suelta')+0.2,'scratch',0.6)
# victory + night
add(T_FELI,bell(784,1.0),0.35); add(T_FELI+0.05,bell(1175,1.0),0.25)
addfx(K('regrese'),'alarm',0.45,0,0.8)
for k in range(5): add(K('regrese')+0.7+k*0.55,sweep(150,110,0.4,g=0.4),0.3)
add(END+0.08,boom(0.7),0.9)
addfx(END+0.1,'trombone',0.9,0,1.4)

m=subprocess.run(['ffmpeg','-v','error','-ss','70','-t',str(D),'-i','assets/music.m4a','-vn','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
mus=np.zeros(N); mm=np.frombuffer(m,dtype=np.float32).astype(np.float64); mus[:min(N,len(mm))]=mm[:N]
fi=int(0.4*SR); mus[:fi]*=np.linspace(0,1,fi)
fo=int(1.4*SR); mus[-fo:]*=np.linspace(1,0,fo)
mus*=0.065
v=subprocess.run(['ffmpeg','-v','error','-i','assets4/voice_t.wav','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
voice=np.frombuffer(v,dtype=np.float32).astype(np.float64)
vo=np.zeros(N); vo[:min(N,len(voice))]=voice[:N]
envv=np.convolve(np.abs(vo),np.ones(int(0.1*SR))/int(0.1*SR),mode='same'); duck=1-0.5*np.clip(envv*8,0,1)
mix=vo+sfx*0.42*(1-0.25*np.clip(envv*8,0,1))+mus*duck
mix/=max(1.0,np.abs(mix).max()/0.95)
pcm=(mix*32767).astype(np.int16)
w=wave.open('build/mix4.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes());w.close()
print('ok',np.abs(mix).max(),D)
