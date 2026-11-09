// room: basement
const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,34),new THREE.MeshStandardMaterial({color:0x4a4a52,roughness:.95}));floor.rotation.x=-Math.PI/2;floor.position.set(0,0,5);floor.receiveShadow=true;scene.add(floor);
const wallM=new THREE.MeshStandardMaterial({color:0x6d7380,roughness:.95});
mk(new THREE.BoxGeometry(34,18,0.4),wallM,0,9,-5.15);mk(new THREE.BoxGeometry(0.4,18,40),wallM,-13,9,5);mk(new THREE.BoxGeometry(0.4,18,40),wallM,13,9,5);
const bulb=new THREE.PointLight(0xffe4a0,90,32);bulb.position.set(0,8.5,2);scene.add(bulb);
// big outlet on wall with face
const oTex=canvasTex(256,256,(g,w,h)=>{g.fillStyle='#e8e8e8';g.fillRect(0,0,w,h);g.fillStyle='#222';g.fillRect(70,60,22,70);g.fillRect(164,60,22,70);g.beginPath();g.arc(128,170,22,0,7);g.fill()});
const outlet=grp(3.2,3.2,-4.8);scene.add(outlet);mk(new THREE.BoxGeometry(3.4,3.4,0.3),mat(0xdddddd),0,0,0,outlet);mk(new THREE.PlaneGeometry(3,3),new THREE.MeshBasicMaterial({map:oTex}),0,0,0.17,outlet);
const oEyes=[-0.55,0.55].map(x=>{const e=mk(new THREE.SphereGeometry(0.2,6,5),mat(0xffffff),x,0.8,0.3,outlet);mk(new THREE.SphereGeometry(0.1,5,4),mat(0),0,0,0.12,e);return e});
// phone (dead) with canvas screen
const pTex=canvasTex(128,256,()=>{});
function drawPhone(pct,face){const g=pTex.userData.c.getContext('2d');g.fillStyle=pct>0?'#0b3d91':'#050505';g.fillRect(0,0,128,256);g.fillStyle=pct>=100?'#39ff14':'#ff2d2d';g.font='900 54px DejaVu Sans';g.textAlign='center';g.fillText(Math.floor(pct)+'%',64,120);g.fillStyle='#fff';g.font='900 18px DejaVu Sans';g.fillText(face?'MEDIOCRE':(pct>0?'CARGANDO':'MUERTO'),64,170);pTex.needsUpdate=true}
const phone=grp(-1.0,0,2.6);scene.add(phone);mk(new THREE.BoxGeometry(1.5,2.6,0.2),mat(0x111111),0,1.4,0,phone);mk(new THREE.PlaneGeometry(1.3,2.3),new THREE.MeshBasicMaterial({map:pTex}),0,1.4,0.11,phone);
const port=mk(new THREE.BoxGeometry(0.4,0.12,0.1),mat(0x555555),0,0.18,0,phone);
// cable snake (segments) + charger idol
const SEG=[];for(let i=0;i<14;i++)SEG.push(mk(new THREE.SphereGeometry(0.16,6,5),mat(0xf2f2f2),0,0,0));
const plug=mk(new THREE.BoxGeometry(0.5,0.35,0.5),mat(0xdddddd),0,0,0);
const charger=grp(0,0,4.6);scene.add(charger);mk(new THREE.BoxGeometry(1.2,1.6,1.0),mat(0xffffff),0,0.8,0,charger);mk(new THREE.TorusGeometry(0.9,0.06,5,16),new THREE.MeshBasicMaterial({color:0xffee66}),0,2.0,0,charger);
const sparks=[];for(let i=0;i<40;i++){const m=mk(new THREE.IcosahedronGeometry(0.14,0),new THREE.MeshBasicMaterial({color:i%2?0xffd54a:0x9ee7ff}),0,0,0);m.visible=false;sparks.push(m)}
// timeline
const T_HOOKEND=K('cómo')-0.3;
const T_CABLE=K('empuja'),T_WALL=K('chingada',0),T_PORT=K('mete'),T_PRAY=K('rézale'),T_SPARK=K('chispazo'),T_MED=K('mediocre');
const SW=new Set(['pendejo','culero','chingada','verga','mamada','cabron','cabrón','puta','pinche','mierda','puto']);
const isSW=w=>SW.has(norm(w));
const swT=words.filter(w=>isSW(w[0])).map(w=>w[1]);
const blinks=[2.0,6.0,11.0,16.0];
const HEROP=V(1.4,0,2.0);
function applyHero(t){
  const pray=t>=T_PRAY&&t<T_SPARK;
  hero.position.set(HEROP.x,pray?-0.55:0,HEROP.z);hero.rotation.set(0,-0.5,0);hero.scale.set(1,1,1);
  const a=pray?1.2:0;legs.forEach((l,i)=>{l.th.rotation.x=-a;l.kn.rotation.x=pray?2.4:0;l.th.scale.set(1,1,1);l.kn.scale.set(1,1,1)});
  torsoP.rotation.x=pray?0.35:0.05;
  const cry=t<T_HOOKEND;
  arms.forEach((g,i)=>{const s=i?1:-1;g.position.x=s*0.95;g.scale.set(1,1,1);g.rotation.z=s*0.12;g.rotation.x=pray?-1.7:(cry?-1.0+0.1*Math.sin(t*20):-0.2+0.1*Math.sin(t*1.5+i))});
  headP.position.y=1.7;headP.rotation.set((cry?0.3:0)+(pray?0.4:0)+0.04*Math.sin(t*3),0,0.05*Math.sin(t*1.4)+(cry?0.1*Math.sin(t*25):0));
  const soot=t>=T_SPARK?1:0;skinM.color.set(soot?0x3a3a3a:0xf2b48a);
  PJ.color.set(0xe63946);PJP.color.set(0x274060);
  let blink=0;for(const b of blinks){const d=t-b;if(d>0&&d<0.14)blink=Math.sin(d/0.14*Math.PI)}
  eyeRig.forEach(r=>{r.lid.rotation.x=0.25+1.2*blink+(cry?0.5:0);r.e.scale.setScalar(1+(t>=T_SPARK?0.6:0));r.pup.visible=!(t>=T_SPARK);r.spiral.visible=t>=T_SPARK;r.spiral.rotation.z=-t*12;r.pup.position.set(0,0,0.25);r.brow.rotation.z=r.s*(cry?0.4:0.1);r.brow.position.y=0.62;r.bag.scale.set(1.1,0.5,0.45)});
  const w=wordAt(TN);let open=0;if(w)open=0.3+0.7*Math.abs(Math.sin((TN-w[1])*21));const sh=SW.has(norm((w||[''])[0]))?1:0;
  mouth.scale.set(0.3+0.1*sh+(cry?0.1:0),0.03+0.2*open+0.12*sh,0.14);drool.visible=false;
  hero.updateMatrixWorld(true);head.getWorldPosition(HP);hero.getWorldPosition(HEROPOS);
}
function applyProps(t){
  const pct=t<T_PORT+1.0?0:Math.min(100,(t-(T_PORT+1.0))*(100/(T_SPARK-T_PORT-1.0))*(t<K('lento')?0.5:1));
  drawPhone(t>=T_SPARK?0:pct,t>=T_MED);
  const wire=eio(seg(t,T_CABLE,T_WALL+0.2)); // cable crawls from plug at phone to the wall
  const end=V(3.2,1.6,-4.4),st=V(-0.5,0.3,2.6);
  const joined=t>=T_PORT+0.8?1:0;
  SEG.forEach((m,i)=>{const k=i/(SEG.length-1);const reach=wire;const target=joined?V(-1.0,0.25,2.6):end;const p=st.clone().lerp(joined?V(3.2,1.6,-4.4):end,k*reach);p.y+=Math.sin(k*Math.PI*3+t*6)*0.5*(1-joined*0.6)*reach;p.x+=Math.sin(k*5+t*4)*0.3*reach;m.position.copy(p);m.visible=t>=T_CABLE-0.1});
  plug.position.copy(SEG[SEG.length-1].position);plug.visible=t>=T_CABLE-0.1;
  oEyes.forEach(e=>e.scale.setScalar(1+0.8*(t>=T_WALL&&t<T_WALL+0.8?1:0)+0.6*(t>=T_SPARK?1:0)));
  charger.visible=t>=T_PRAY-0.3;charger.rotation.y=t*1.5;
  const sk=t-T_SPARK;sparks.forEach((m,i)=>{const on=sk>0&&sk<1.2;m.visible=on;if(!on)return;const a=rnd(i)*6.28,v=3+rnd(i+9)*6;m.position.set(-1.0+Math.cos(a)*v*sk*0.5,1.6+Math.sin(a)*v*sk*0.6-6*sk*sk,2.6+(rnd(i+3)-.5)*v*sk*0.6);m.scale.setScalar(1-sk/1.2)});
  phone.rotation.z=t>=T_SPARK&&t<T_SPARK+0.8?0.3*Math.sin(t*50):0;
}
function applyEffects(t){}
const hpa=(x,y,z)=>[HP.x+x,HP.y+y,HP.z+z];
const PH=[-1.0,1.6,2.6],WL=[3.2,3.2,-4.4];
const CUTS=[0,1.1,K('culero')-0.1,K('cómo')-0.3,K('teléfono'),T_CABLE,K('pared')-0.2,K('verga')-0.4,T_PORT,K('puerto')-0.2,K('conciencia')-0.1,T_PRAY,K('cargador'),K('energía')+0.3,K('pinche',1)-0.1,T_SPARK-0.2,T_SPARK+0.5,K('cara')-0.1,T_MED-0.1];
const shots=[
 (u,t)=>({p:hpa(1.5,0.2,lerp(5.2,4.2,u)),l:HP.toArray(),f:38}),
 (u,t)=>({p:P([2,3,10],[0,2.8,8.5],u),l:[0,2.2,2.6],f:54}),
 (u,t)=>({p:P([0.5,1.4,6],[0,1.4,5],u),l:PH,f:44}),
 (u,t)=>({p:P([0,3.6,14],[0.5,3.4,12.5],eout(u)),l:[1,2.4,1.5],f:54}),
 (u,t)=>({p:P([-2.5,2.2,7.5],[-1.5,2.0,6.2],u),l:PH,f:40}),
 (u,t)=>({p:P([1.5,3.6,10],[2.5,3.4,8],u),l:[1.2,2.4,0],f:56}),
 (u,t)=>({p:P([4,3.4,6],[3.6,3.4,4],u),l:WL,f:42}),
 (u,t)=>({p:hpa(-1.2,0.1,lerp(5.0,3.8,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([-1,1.6,6.6],[-1,1.2,4.8],u),l:[-1,0.4,2.6],f:40}),
 (u,t)=>({p:P([-3.5,1.0,7],[-2,1.0,5.5],u),l:PH,f:48}),
 (u,t)=>({p:hpa(1.0,0.0,lerp(5.0,3.8,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([2,2.0,11],[1.2,2.0,9],u),l:[1.3,1.4,3],f:56}),
 (u,t)=>({p:P([-1.5,3.0,9],[-0.5,2.4,7],u),l:[0,1.6,4.2],f:46}),
 (u,t)=>({p:P([-1.8,2.4,8.5],[-1.2,2.0,6.8],u),l:PH,f:40}),
 (u,t)=>({p:hpa(1.4,0.2,lerp(4.6,3.8,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([0,2.6,10],[-0.5,2.4,8],u),l:[-0.5,1.6,2.6],f:50}),
 (u,t)=>({p:hpa(0.8,0.0,lerp(4.2,3.4,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([-1.4,2.2,6.4],[-1.0,2.0,5.2],u),l:PH,f:38}),
 (u,t)=>({p:hpa(1.5,0.2,lerp(5.2,3.9,u)),l:HP.toArray(),f:38}),
];
function applyCam(t){
  let si=0;for(let i=0;i<CUTS.length;i++)if(t>=CUTS[i])si=i;
  const a=CUTS[si],b=CUTS[si+1]||END+1.5;const u=clamp((t-a)/(b-a));const r=shots[si](u,t);
  let fov=r.f;for(const ts of swT){const d=TN-ts;if(d>0&&d<0.5)fov-=9*Math.exp(-d*10)}
  const dc=t-a;if(dc<0.12&&si>0)fov-=4*(1-dc/0.12);
  let sh=0;[[T_SPARK,1.6],[T_WALL,0.8]].forEach(([ts,amp])=>{const d=t-ts;if(d>0&&d<0.6)sh+=amp*Math.exp(-d*7)});
  cam.position.set(r.p[0]+sh*0.12*Math.sin(t*95),r.p[1]+sh*0.12*Math.cos(t*81),r.p[2]);cam.up.set(0,1,0);cam.lookAt(r.l[0],r.l[1],r.l[2]);
  cam.fov=fov;cam.updateProjectionMatrix();
}
const FLASH=[[T_SPARK,1],[T_WALL,0.5],[T_HOOKEND,0.5]];
const HOOK_TEXT='CEL MUERTO';const TITLE_HTML='CÓMO CARGAR<br>UN TELÉFONO';const TITLE_WORD='cómo';const PILL_TEXT='TUTORIAL #9 · CÓMO CARGAR UN TELÉFONO';const PILL=[K('cómo')+1.4,K('mete')+0.8];
