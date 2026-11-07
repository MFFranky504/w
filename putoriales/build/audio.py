import numpy as np, wave, json, subprocess
SR=44100
WP=json.load(open('assets/warp.json'))
WA=WP['warp']
def warpn(t):
    if t<=WA[0][0]: return t
    for i in range(1,len(WA)):
        if t<=WA[i][0]:
            o0,n0=WA[i-1];o1,n1=WA[i];return n0+(t-o0)/(o1-o0)*(n1-n0)
    return WA[-1][1]+(t-WA[-1][0])
D=WP['end']+1.5
N=int(SR*D)
sfx=np.zeros(N)
def add(t,x,g=1.0):
    i=int(warpn(t)*SR); x=x*g
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

words=json.load(open('assets/words.json'))['words']
sw=['chingada...','puto','imbécil.','cabrón...','carajos','culo.','verga.']
import re
SWS={'chingada','puto','pinche','pendejo','mamada','imbécil','cabrón','carajos','culo','puta','verga','culero'}
for w in words:
    if re.sub(r'[^a-záéíóúñü]','',w[0].lower()) in SWS: sfx_i=int((w[1]-0.02)*SR); x=boom(0.5)*0.55; sfx[sfx_i:sfx_i+len(x)]+=x[:N-sfx_i]
# zoom whoosh
add(2.15,whoosh(0.5),0.5); add(5.7,whoosh(0.45),0.4); add(7.2,whoosh(0.4),0.4); add(11.4,whoosh(0.35),0.35); add(21.7,whoosh(0.5),0.45)
add(34.0,whoosh(0.5),0.35); add(35.7,whoosh(1.6),0.5)
# planet sigh
add(6.3,sweep(500,180,0.6,g=0.4),0.7)
# chair
add(8.5,tick(1500,0.05),0.9); add(8.65,bell(1318,0.8),0.35); add(8.65,whoosh(0.5),0.35)
for k in range(4): add(10.2+k*0.17,boing(300,500,0.14),0.7)
add(12.9,thud(0.2),0.8)  # snap cut thud
# eyebrow
add(12.97,sweep(300,900,0.15,g=0.5),0.5)
# knee creaks
for k in range(6): add(14.4+k*0.3,sweep(380+k*40,150,0.18,'sq',0.5),0.35)
# neck
add(18.78,thud(0.4),0.9); add(19.5,boing(150,900,1.0),0.7); add(19.8,whoosh(1.3),0.35)
for k in range(8): add(19.9+k*0.16,tick(900+80*k,0.05),0.6)
add(21.4,boing(900,160,0.5),0.7)
# slow sit
add(22.65,sweep(60,40,3.8,g=0.9),0.7); add(22.6,noise(4.2,0.15,0.1)*np.hanning(int(4.2*SR)),1)
add(26.95,thud(0.4),0.9)
# silence then chair flees: pitter patter
add(28.7,sweep(900,300,0.3,'sq',0.4),0.6)
for k in range(32): add(29.05+k*0.048,tick(1100+(k%2)*300,0.03),0.9)
add(29.6,sweep(200,260,0.3,g=0.3),0.4)
add(29.3,sweep(250,500,0.5,g=0.4),0.4) # door creak
# furniture hops
for k in range(10): add(31.15+k*0.12,thud(0.12),0.9)
add(32.38,thud(0.5),1.3); add(32.38,noise(0.3,0.05,0.6)*env(0.3,0.001,0.3),0.8) # slam
# felicidades party
add(33.06,bell(1046,1.2),0.6); add(33.2,bell(1568,1.2),0.5)
add(33.06,sweep(400,1600,0.5,'sq',0.4),0.5)
add(33.06,noise(1.2,0.1,0.5)*env(1.2,0.001,1.2),0.6)
# crickets (silencio incomodo)
for k in range(10): add(35.0+k*0.09,tick(4200,0.03),0.12) if False else None
add(34.8,np.concatenate([tick(4300,0.02),np.zeros(int(0.05*SR)),tick(4300,0.02)]*3),0.25)
# floor collapse
add(35.4,noise(2,0.03,0.4)*np.hanning(int(2*SR)),0.9); add(35.5,sweep(300,40,1.8,g=0.7),0.7)
# stand up pop
add(37.55,sweep(150,500,0.25,g=0.5),0.6); add(38.4,thud(0.2),0.7)
# final
add(40.6,boom(0.7),0.9)
add(40.75,trombone(311,0.55),0.9); add(41.3,trombone(294,0.5),0.9); add(41.8,trombone(262,1.0),0.5)

# music: Not Like Us instrumental, low volume under voice
m=subprocess.run(['ffmpeg','-v','error','-ss','0','-t',str(D),'-i','assets/music.m4a','-vn','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
mus=np.zeros(N); mm=np.frombuffer(m,dtype=np.float32).astype(np.float64); mus[:min(N,len(mm))]=mm[:N]
fi=int(0.6*SR); mus[:fi]*=np.linspace(0,1,fi)
fo=int(1.8*SR); mus[-fo:]*=np.linspace(1,0,fo)
mus*=0.065
# mix voice
v=subprocess.run(['ffmpeg','-v','error','-i','assets/voice.mp3','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
voice=np.frombuffer(v,dtype=np.float32).astype(np.float64)
vo=np.zeros(N); vo[:min(N,len(voice))]=voice[:N]*1.0
# duck music/sfx under voice slightly
envv=np.convolve(np.abs(vo),np.ones(int(0.1*SR))/int(0.1*SR),mode='same'); duck=1-0.5*np.clip(envv*8,0,1)
mix=vo+ (sfx*0.5)*duck*0+sfx*0.45+mus*duck
mix/= max(1.0,np.abs(mix).max()/0.95)
pcm=(mix*32767).astype(np.int16)
w=wave.open('build/mix.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes());w.close()
print('ok',np.abs(mix).max())
