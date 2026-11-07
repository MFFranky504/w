import numpy as np, wave, json, subprocess, re
SR=44100
words=json.load(open('assets2/words_t.json'))['words']
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
T_BLAST=K('verga',1); LAND=T_BLAST+1.85; POPT=K('verga',0)+0.12
CUTS=[0,1.39,2.2,2.9,K('sí'),K('alguien'),K('primero'),K('ese'),K('cochino')+0.2,K('ahora',0),K('no'),K('sostenga'),K('uno'),K('dos'),K('pinche'),K('ahora',1),T_BLAST,LAND-1.15,LAND,LAND+1.1]
for c in CUTS[1:]: add(c-0.04,whoosh(0.3),0.35)
SWS={'chingada','pendejo','cochino','verga','pinche','chingue','animal'}
for w in words:
    if norm(w[0]) in SWS:
        i=int((w[1]-0.02)*SR); x=boom(0.5)*0.5; sfx[i:i+len(x)]+=x[:N-i]
# hook: gasp + balloon squeaks
add(0.0,noise(0.35,0.08,0.7)*np.hanning(int(0.35*SR)),0.5)
for k in range(9): add(0.25+k*0.2,squeak(0.14,800+60*(k%3)),0.5)
add(POPT,pop(),1.0); add(POPT,noise(1.2,0.1,0.5)*env(1.2,0.001,1.2),0.5); add(POPT+0.05,bell(1568,0.6),0.25)
add(K('cómo')-0.02,boom(0.7),0.8); add(K('cómo')+0.05,bell(988,0.9),0.3)
add(K('pendejo')-0.2,boing(250,600,0.2),0.6)
add(K('alguien'),sweep(600,300,0.25,g=0.4),0.5)
add(K('abra'),sweep(200,500,0.3,g=0.4),0.4)
add(K('mete')-0.4,sweep(300,120,0.5,g=0.5),0.6); 
for k in range(5): add(K('mete')+k*0.08,tick(500+60*k,0.03),0.5)
add(K('cochino')+0.25,trombone(220,0.5),0.7)
add(K('cochino')+0.35,noise(0.4,0.05,0.4)*env(0.4,0.01,0.4),0.5)
# inhale
add(12.35,noise(3.3,0.04,0.5)*np.hanning(int(3.3*SR)),0.9)
add(12.35,sweep(180,1000,3.3,g=0.5),0.5)
for it in [12.7,13.1,13.5,14.1,14.45,14.85]: add(it+0.78,sweep(700,140,0.14,g=0.9),0.9); add(it+0.78,tick(300,0.04),0.7)
for k in range(10): add(14.2+k*0.14,squeak(0.12,500+80*k),0.35)
# tension: creaks + heartbeat
for k in range(14): add(15.8+k*0.4+(0.1 if k%2 else 0),squeak(0.16,420+25*k),0.28)
t=K('uno')-0.3;step=0.62
while t<T_BLAST-0.2:
    add(t,thud(0.14),0.7);add(t+0.17,thud(0.12),0.5);t+=step;step=max(0.28,step*0.92)
for nm,k in (('uno',0),('dos',0),('tres',0)):
    add(K(nm),tick(1000,0.2)*0.9,0.7)
add(K('pinche')-0.02,tick(1400,0.25),0.7)
# blast
add(T_BLAST-0.03,boom(0.9),1.2); add(T_BLAST-0.02,pop(),0.9); add(T_BLAST,noise(0.5,0.05,0.8)*env(0.5,0.001,0.5),0.9)
add(T_BLAST+0.36,noise(0.5,0.02,1.2)*env(0.5,0.001,0.4),1.0); add(T_BLAST+0.36,thud(0.5),1.2); add(T_BLAST+0.4,bell(2200,0.6),0.25)
for i in range(5): add(T_BLAST+0.05*i+1.15+0.1*i,thud(0.2),0.6)
add(T_BLAST+0.12,rasp(1.7,200,60),0.8); add(T_BLAST+0.12,whoosh(1.7),0.4)
for k in range(6): add(T_BLAST+0.3+k*0.25,rasp(0.12,260,120),0.4)
add(LAND,thud(0.5),1.1)
add(K('felicidades'),bell(784,1.0),0.35)
add(K('respira',0)-0.0,bell(1046,0.8),0.2)
# end: stinger
add(END+0.08,boom(0.7),0.9)
add(END+0.2,trombone(311,0.5),0.9); add(END+0.75,trombone(294,0.5),0.9); add(END+1.25,trombone(262,0.9),0.5)

# music (offset into track for variety)
m=subprocess.run(['ffmpeg','-v','error','-ss','20','-t',str(D),'-i','assets/music.m4a','-vn','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
mus=np.zeros(N); mm=np.frombuffer(m,dtype=np.float32).astype(np.float64); mus[:min(N,len(mm))]=mm[:N]
fi=int(0.4*SR); mus[:fi]*=np.linspace(0,1,fi)
fo=int(1.4*SR); mus[-fo:]*=np.linspace(1,0,fo)
mus*=0.065
v=subprocess.run(['ffmpeg','-v','error','-i','assets2/voice_t.wav','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
voice=np.frombuffer(v,dtype=np.float32).astype(np.float64)
vo=np.zeros(N); vo[:min(N,len(voice))]=voice[:N]
envv=np.convolve(np.abs(vo),np.ones(int(0.1*SR))/int(0.1*SR),mode='same'); duck=1-0.5*np.clip(envv*8,0,1)
mix=vo+sfx*0.42*(1-0.25*np.clip(envv*8,0,1))+mus*duck
mix/=max(1.0,np.abs(mix).max()/0.95)
pcm=(mix*32767).astype(np.int16)
w=wave.open('build/mix2.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes());w.close()
print('ok',np.abs(mix).max(),D)
