const LIGHTS=scene.children.filter(o=>o.isLight);const L0=LIGHTS.map(l=>l.intensity);
const mk0=(...a)=>{const o=mk(...a);scene.add(o);return o};
mk0(new THREE.PlaneGeometry(40,34),new THREE.MeshStandardMaterial({color:0x5b5144,roughness:.95}),0,0,5).rotation.x=-Math.PI/2;
const wallM=new THREE.MeshStandardMaterial({color:0x7a7566,roughness:.95});
mk0(new THREE.BoxGeometry(34,18,0.4),wallM,0,9,-5.15);mk0(new THREE.BoxGeometry(0.4,18,40),wallM,-13,9,5);mk0(new THREE.BoxGeometry(0.4,18,40),wallM,13,9,5);
// bulb light
const bl=new THREE.PointLight(0xfff2c0,0,40);bl.position.set(1.8,6.2,1.5);scene.add(bl);
// socket lamp stand
const stand=grp(1.8,0,0.6);scene.add(stand);mk(new THREE.CylinderGeometry(0.15,0.15,3.4,6),mat(0x333),0,1.7,0,stand);mk(new THREE.CylinderGeometry(0.6,0.7,0.2,8),mat(0x333),0,0.1,0,stand);
const sock=grp(0,3.6,0,stand);mk(new THREE.CylinderGeometry(0.4,0.4,0.7,8),mat(0xc9a227),0,0,0,sock);
const sEyes=[-0.15,0.15].map(x=>{const e=mk(new THREE.SphereGeometry(0.1,6,5),mat(0xffffff),x,0.1,0.38,sock);mk(new THREE.SphereGeometry(0.05,5,4),mat(0),0,0,0.07,e);return e});
const sMouth=mk(new THREE.SphereGeometry(0.1,6,5),mat(0x330000),0,-0.15,0.4,sock);
// bulb
const bulb=grp(0,0,0);scene.add(bulb);const bulbM=new THREE.MeshStandardMaterial({color:0xffffff,transparent:true,opacity:.55,emissive:0x000000});mk(new THREE.SphereGeometry(0.5,10,8),bulbM,0,0.55,0,bulb);mk(new THREE.CylinderGeometry(0.22,0.22,0.4,8),mat(0xaaaaaa),0,0,0,bulb);
// roaches with rent envelopes
const ROACH=[0,1,2,3,4,5].map(i=>{const g=grp();scene.add(g);mk(new THREE.IcosahedronGeometry(0.28,0),mat(0x2a1a0a),0,0.2,0,g).scale.set(1,0.6,1.5);[-0.1,0.1].forEach(x=>mk(new THREE.SphereGeometry(0.06,5,4),new THREE.MeshBasicMaterial({color:0xffee33}),x,0.3,0.38,g));mk(new THREE.BoxGeometry(0.3,0.04,0.2),mat(0xffffff),0,0.55,0,g);return g});
// tombstone
const tTex=canvasTex(256,256,(g,w,h)=>{g.fillStyle='#bbb';g.fillRect(0,0,w,h);g.fillStyle='#222';g.font='900 54px DejaVu Sans';g.textAlign='center';g.fillText('R.I.P.',w/2,90);g.font='900 34px DejaVu Sans';g.fillText('TU DIGNIDAD',w/2,150);g.fillText('(SAT)',w/2,200)});
const tomb=grp(-3.4,-3,0.8);scene.add(tomb);mk(new THREE.BoxGeometry(1.8,2.4,0.4),mat(0x999999),0,1.2,0,tomb);mk(new THREE.PlaneGeometry(1.6,1.6),new THREE.MeshBasicMaterial({map:tTex}),0,1.4,0.22,tomb);
// bubble AY
const aTex=canvasTex(256,128,(g,w,h)=>{g.fillStyle='#fff';g.strokeStyle='#111';g.lineWidth=8;g.beginPath();g.roundRect(8,8,240,100,30);g.fill();g.stroke();g.fillStyle='#d62828';g.font='900 64px DejaVu Sans';g.textAlign='center';g.fillText('¡AY!',w/2,84)});
const ay=new THREE.Mesh(new THREE.PlaneGeometry(1.8,0.9),new THREE.MeshBasicMaterial({map:aTex,transparent:true}));ay.visible=false;scene.add(ay);
// mirror with gremlin
const mTex=canvasTex(256,320,(g,w,h)=>{g.fillStyle='#bfe3ff';g.fillRect(0,0,w,h);g.fillStyle='#6a8a3a';g.beginPath();g.ellipse(128,170,90,110,0,0,7);g.fill();g.fillStyle='#fff';[[90,140],[166,140]].forEach(([x,y])=>{g.beginPath();g.arc(x,y,26,0,7);g.fill();g.fillStyle='#000';g.beginPath();g.arc(x,y,9,0,7);g.fill();g.fillStyle='#fff'});g.fillStyle='#3a0a0a';g.fillRect(80,215,96,26);g.fillStyle='#fff';g.font='900 24px DejaVu Sans';g.fillText('TÚ',116,300)});
const mir=grp(-5.6,3.6,-4.8);scene.add(mir);mk(new THREE.BoxGeometry(3.2,4.2,0.2),mat(0x7a5230),0,0,0,mir);mk(new THREE.PlaneGeometry(2.8,3.7),new THREE.MeshBasicMaterial({map:mTex}),0,0,0.12,mir);
// debris + shards
const SH=[];for(let i=0;i<24;i++){const m=mk(new THREE.IcosahedronGeometry(0.15,0),new THREE.MeshBasicMaterial({color:0xcfefff}),0,0,0);m.visible=false;SH.push(m)}
// timeline
const T_HOOKEND=K('cómo')-0.3,T_FOCO=K('foco'),T_ENT=K('enterró'),T_ENR=K('enrosca'),T_MET=K('métela'),T_SW=K('switch'),T_FEL=K('felicidades'),T_MIS=K('miseria'),T_OJ=K('ojalá'),T_END=K('fracasado');
const SW=new Set(['pendejo','culero','madre','puta','cabrón','cabron','puto','mierda']);
const isSW=w=>SW.has(norm(w));
const swT=words.filter(w=>isSW(w[0])).map(w=>w[1]);
const blinks=[2.0,6.0,10.0,16.0,23.0];
const HPOS=V(-0.8,0,2.2);
function applyHero(t){
  hero.position.set(HPOS.x,0,HPOS.z);hero.rotation.set(0,0.2,0);hero.scale.set(1,1,1);
  legs.forEach(l=>{l.th.rotation.x=0;l.kn.rotation.x=0;l.th.scale.set(1,1,1);l.kn.scale.set(1,1,1)});
  const up=t>=T_ENR&&t<T_SW,cover=t>=T_SW&&t<T_SW+2.2,rise=eio(seg(t,T_ENR,T_ENR+0.4));
  torsoP.rotation.x=0.05;
  arms.forEach((g,i)=>{const s=i?1:-1;g.position.x=s*0.95;g.scale.set(1,1,1);g.rotation.z=s*(0.12-0.1*(up?1:0));
    g.rotation.x=up?lerp(-0.1,-2.9,rise)+(t>=T_ENR&&t<T_MET?0.3*Math.sin(t*20+i):0)+(t>=T_MET&&t<T_SW?0.15*Math.sin(t*6+i):0):(cover?-2.0:(-0.1+0.05*Math.sin(t*1.3+i)))});
  headP.position.y=1.7;headP.rotation.set(up?-0.5:0.04*Math.sin(t*3)+(cover?0.4:0),0,0.05*Math.sin(t*1.4));
  skinM.color.set(0xd9b89a);PJ.color.set(0x5f6f8f);PJP.color.set(0x3a3a3a);
  const dark=t<T_SW;let blink=0;for(const b of blinks){const d=t-b;if(d>0&&d<0.14)blink=Math.sin(d/0.14*Math.PI)}
  eyeRig.forEach(r=>{r.lid.rotation.x=0.15+1.2*blink+(cover?1.0:0);r.e.scale.setScalar(1+(t>=T_MET&&t<T_SW?0.3:0)+(t>=T_MIS&&t<T_MIS+1?0.5:0));r.e.material.emissive.setHex(dark?0xffffff:0x000000);r.e.material.emissiveIntensity=dark?0.9:0;
    r.pup.visible=true;r.spiral.visible=false;r.pup.position.set(0,up?0.12:0,0.25);r.brow.rotation.z=r.s*0.2;r.brow.position.y=0.62;r.bag.scale.set(1.1,0.55,0.45)});
  const w=wordAt(TN);let open=0;if(w)open=0.3+0.7*Math.abs(Math.sin((TN-w[1])*21));const sh=SW.has(norm((w||[''])[0]))?1:0;
  mouth.scale.set(0.3+0.1*sh,0.03+0.2*open+0.12*sh,0.14);drool.visible=false;
  hero.updateMatrixWorld(true);head.getWorldPosition(HP);hero.getWorldPosition(HEROPOS);
}
function applyProps(t){
  // light: dark until switch, flicker, dies at end
  const lit=t>=T_SW&&t<T_OJ+1.4;const fl=lit?(0.7+0.3*Math.sin(t*37)):0;
  LIGHTS.forEach((l,i)=>l.intensity=L0[i]*(lit?0.55:0.24));bl.intensity=lit?140*fl:0;
  bulbM.emissive.setHex(lit?0xffe9a0:0x000000);bulbM.emissiveIntensity=lit?1.2:0;
  // bulb path: hand-held high -> screwed into socket -> falls at end
  const hold=V(HPOS.x+0.3,6.0,HPOS.z+0.2),skt=V(1.8,4.05,0.6);
  const bk=eio(seg(t,T_MET-0.2,T_MET+1.8));const p=t<T_ENR?V(-6,0.5,3):hold.clone().lerp(skt,bk);
  bulb.position.copy(p);bulb.rotation.y=t>=T_ENR&&t<T_MET+1.8?t*12:0;bulb.visible=t>=T_FOCO-0.3;
  const fall=t-(T_END-0.3);if(fall>0){bulb.position.set(skt.x-0.8*fall,Math.max(0.5,skt.y-4*fall*fall*3),skt.z+2.0*fall);bulb.visible=fall<0.7}
  const hit=t>=T_END+0.3;SH.forEach((m,i)=>{const d=t-(T_END+0.3);m.visible=d>0&&d<1.5;if(!m.visible)return;const a=rnd(i)*6.28,v=2+rnd(i+5)*4;m.position.set(1.0+Math.cos(a)*v*d,0.5+3*d-6*d*d+(rnd(i+9)),2.2+Math.sin(a)*v*d*0.5)});
  // socket reacts
  const pl=t>=T_MET&&t<T_SW;sEyes.forEach(e=>e.scale.setScalar(pl?2:1));sMouth.scale.set(pl?2.5:1,pl?3:1,1);sock.rotation.z=pl?0.1*Math.sin(t*18):0;
  ay.visible=t>=T_MET+0.6&&t<T_SW+0.4;ay.position.set(2.6,5.4+0.1*Math.sin(t*6),0.8);ay.quaternion.copy(cam.quaternion);
  // roaches (hook)
  ROACH.forEach((g,i)=>{const on=t<T_HOOKEND+0.8||t>=T_OJ;g.visible=on&&(t<T_SW||t>=T_OJ);const x=-5+((t*0.9+i*1.7)%10);g.position.set(x,0,3.8+0.4*(i%3));g.rotation.y=Math.PI/2;g.children[0].position.y=0.2+0.05*Math.abs(Math.sin(t*12+i))});
  // tombstone rises
  tomb.position.y=lerp(-3,0,eio(seg(t,T_ENT-0.3,T_ENT+0.4)));
  // mirror gremlin visible after switch (always drawn; dark before)
}
function applyEffects(t){}
const hpa=(x,y,z)=>[HP.x+x,HP.y+y,HP.z+z];
const SK=[1.8,3.9,0.6];
const CUTS=[0,K('rata')-0.1,K('pendejo')-0.3,T_HOOKEND,T_FOCO-0.2,K('culero'),K('tu'),T_ENT-0.2,T_ENR-0.2,K('madre'),K('soquet'),K('conecta'),K('gira'),T_MET-0.1,K('hijo')-0.1,K('aquí'),T_SW-0.3,T_FEL-0.1,T_MIS-0.2,K('espejo')-0.1,T_OJ,T_END-0.5];
const shots=[
 (u,t)=>({p:hpa(0.3,0.1,lerp(5.4,4.2,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([-1,0.9,8],[0,1.1,6.5],u),l:[0,0.3,3.8],f:50}),
 (u,t)=>({p:hpa(0.6,0.0,lerp(4.4,3.4,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([0,3.6,14],[0.5,3.4,12.5],eout(u)),l:[0.5,2.6,1.5],f:54}),
 (u,t)=>({p:P([-4,2.6,8],[-2,2.8,6.5],u),l:[1.2,2.8,0.5],f:44}),
 (u,t)=>({p:hpa(0,0.2,lerp(5,4,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([-1,3.0,10],[-2.5,2.6,8.5],u),l:[-3.2,2.0,0.8],f:46}),
 (u,t)=>({p:P([-4.2,1.8,8],[-3.2,2.0,6.8],u),l:[-3.4,2.0,0.8],f:42}),
 (u,t)=>({p:P([0,2.2,11],[0.5,2.6,9.5],u),l:[0.5,4.2,1.5],f:58}),
 (u,t)=>({p:hpa(0.8,0.4,lerp(4.6,3.6,u)),l:hpa(0,0.4,0),f:36}),
 (u,t)=>({p:P([3.4,3.8,7],[2.8,3.9,5.5],u),l:SK,f:36}),
 (u,t)=>({p:hpa(-0.6,0.2,lerp(4.4,3.5,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([1.8,4.2,8],[1.2,4.2,6.4],u),l:SK,f:40}),
 (u,t)=>({p:P([3.6,4.0,6.5],[3.0,4.1,5.2],eio(u)),l:SK,f:30}),
 (u,t)=>({p:hpa(1.0,0.2,lerp(4.4,3.4,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([2,3.8,10],[2.4,3.9,8],u),l:SK,f:44}),
 (u,t)=>({p:P([0,3.4,14],[0,3.6,12],u),l:[0,3.0,1.5],f:58}),
 (u,t)=>({p:hpa(0.4,0.1,lerp(5.0,3.8,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([-1,3.4,11],[-3,3.6,8.5],eio(u)),l:[-5.2,3.6,-4.8],f:46}),
 (u,t)=>({p:P([-2,3.2,9],[-4,3.6,6.5],u),l:[-5.6,3.6,-4.8],f:36}),
 (u,t)=>({p:hpa(0.8,0.2,lerp(5.2,4.0,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([0,4.4,12],[0.5,3.6,9],eio(u)),l:[0.5,2.6,1.8],f:50}),
];
function applyCam(t){
  let si=0;for(let i=0;i<CUTS.length;i++)if(t>=CUTS[i])si=i;
  const a=CUTS[si],b=CUTS[si+1]||END+1.5;const u=clamp((t-a)/(b-a));const r=shots[si](u,t);
  let fov=r.f;for(const ts of swT){const d=TN-ts;if(d>0&&d<0.5)fov-=9*Math.exp(-d*10)}
  const dc=t-a;if(dc<0.12&&si>0)fov-=4*(1-dc/0.12);
  let sh=0;[[T_SW,1.6],[T_END+0.3,1.4],[T_MET+0.6,0.7]].forEach(([ts,amp])=>{const d=t-ts;if(d>0&&d<0.6)sh+=amp*Math.exp(-d*7)});
  cam.position.set(r.p[0]+sh*0.12*Math.sin(t*95),r.p[1]+sh*0.12*Math.cos(t*81),r.p[2]);cam.up.set(0,1,0);cam.lookAt(r.l[0],r.l[1],r.l[2]);
  cam.fov=fov;cam.updateProjectionMatrix();
}
const FLASH=[[T_SW,1],[T_END+0.3,0.8],[T_MET+0.6,0.4],[T_HOOKEND,0.5]];
const HOOK_TEXT='SIN LUZ, PENDEJO';const TITLE_HTML='CÓMO ENCENDER<br>UNA BOMBILLA';const TITLE_WORD='cómo';const PILL_TEXT='TUTORIAL #11 · CÓMO ENCENDER UNA BOMBILLA';const PILL=[K('cómo')+1.4,K('busca')+1.0];
