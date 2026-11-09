const mk0=(...a)=>{const o=mk(...a);scene.add(o);return o};
const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,34),new THREE.MeshStandardMaterial({color:0xd9d2c0,roughness:.9}));floor.rotation.x=-Math.PI/2;floor.position.set(0,0,5);floor.receiveShadow=true;scene.add(floor);
const wallM=new THREE.MeshStandardMaterial({color:0xf2c14e,roughness:.9});
mk0(new THREE.BoxGeometry(34,18,0.4),wallM,0,9,-5.15);mk0(new THREE.BoxGeometry(0.4,18,40),wallM,-13,9,5);mk0(new THREE.BoxGeometry(0.4,18,40),wallM,13,9,5);
const bulb=new THREE.PointLight(0xfff0c0,80,32);bulb.position.set(0,9,3);scene.add(bulb);
const cTex=canvasTex(512,256,(g,w,h)=>{g.fillStyle='#fff';g.fillRect(0,0,w,h);g.fillStyle='#e63946';g.font='900 80px DejaVu Sans';g.textAlign='center';g.fillText('COCINA',w/2,110);g.fillStyle='#111';g.font='900 46px DejaVu Sans';g.fillText('SOLO ADULTOS',w/2,190)});
mk0(new THREE.BoxGeometry(4.4,2.4,0.15),mat(0x222),-4,7,-4.9);mk0(new THREE.PlaneGeometry(4.2,2.2),new THREE.MeshBasicMaterial({map:cTex}),-4,7,-4.8);
mk0(new THREE.BoxGeometry(14,2.4,2.2),mat(0x8d5a2b),0,1.2,0.5);mk0(new THREE.BoxGeometry(14.4,0.2,2.5),mat(0xeeeeee),0,2.5,0.5);
const sw=grp(0,2.6,0.5);scene.add(sw);
const bot=mk(new THREE.BoxGeometry(2.6,0.35,1.6),mat(0xe0b070),0,0.18,0,sw);const top=grp(0,0.5,0,sw);mk(new THREE.BoxGeometry(2.6,0.35,1.6),mat(0xe9c690),0,0.2,0,top);
const sau=grp(0,0.6,0,sw);mk(new THREE.CylinderGeometry(0.22,0.22,2.2,8).rotateZ(Math.PI/2),mat(0xe0707a),0,0,0,sau);
const sEyes=[-0.5,0.5].map(x=>{const e=mk(new THREE.SphereGeometry(0.14,6,5),mat(0xffffff),x,0.2,0.18,sau);mk(new THREE.SphereGeometry(0.07,5,4),mat(0),0,0,0.08,e);return e});
const sMouth=mk(new THREE.SphereGeometry(0.1,6,5),mat(0x330000),0,-0.02,0.22,sau);
const mayo=grp(-3.6,2.6,1.0);scene.add(mayo);mk(new THREE.CylinderGeometry(0.4,0.5,1.6,8),mat(0xffffff),0,0.8,0,mayo);mk(new THREE.ConeGeometry(0.2,0.5,6),mat(0xe63946),0,1.8,0,mayo);
const MB=[];for(let i=0;i<30;i++){const m=mk(new THREE.IcosahedronGeometry(0.3,0),mat(0xfff8dc),0,0,0);m.visible=false;MB.push(m)}
const press=grp(0,0,0.5);scene.add(press);mk(new THREE.BoxGeometry(3.2,0.8,2.2),mat(0x777788),0,0,0,press);mk(new THREE.CylinderGeometry(0.2,0.2,6,6),mat(0x555),0,3.2,0,press);press.visible=false;
const TE=K('tráguelo'),TS=K('salchicha'),TM=K('meter'),TC=K('crema'),TU=K('unte'),TA=K('aplástelo'),TH=K('hocico');
const T_HOOKEND=K('cómo')-0.3;
const SW=new Set(['pendejo','cabron','cabrón','culero','puta','mamada','puto','mierda','pinche']);
const isSW=w=>SW.has(norm(w));
const swT=words.filter(w=>isSW(w[0])).map(w=>w[1]);
const blinks=[1.5,5.0,9.0,14.0,19.0];
function applyHero(t){
  hero.position.set(0,0,-1.1);hero.rotation.set(0,0,0);hero.scale.set(1,1,1);
  legs.forEach(l=>{l.th.rotation.x=0;l.kn.rotation.x=0;l.th.scale.set(1,1,1);l.kn.scale.set(1,1,1)});
  const spread=t>=TU&&t<TA?1:0, grip=t<TS?1:0, eat=t>=TE;
  const swallow=eio(seg(t,K('vez'),K('vez')+1.2));
  torsoP.rotation.x=0.1;
  arms.forEach((g,i)=>{const s=i?1:-1;g.position.x=s*0.95;g.scale.set(1,1,1);g.rotation.z=s*(0.12+0.2*grip);
    g.rotation.x=-1.2+(spread&&i?0.5*Math.sin(t*28):0)+(t>=TA&&t<TA+0.5?-0.5:0)+(eat?-0.6*Math.sin(t*10):0)});
  headP.position.y=1.7;headP.rotation.set(0.05*Math.sin(t*3)+(eat?-0.4:0),0,0.05*Math.sin(t*1.4));
  skinM.color.set(t>=TC&&t<TU?0xf6efe0:0xf2b48a);PJ.color.set(0xffffff);PJP.color.set(0x222222);
  let blink=0;for(const b of blinks){const d=t-b;if(d>0&&d<0.14)blink=Math.sin(d/0.14*Math.PI)}
  eyeRig.forEach(r=>{r.lid.rotation.x=0.2+1.2*blink;r.e.scale.setScalar(1+(t>=TS&&t<TS+1?0.4:0));r.pup.visible=true;r.spiral.visible=false;r.pup.position.set(0,-0.1,0.25);r.brow.rotation.z=r.s*0.15;r.brow.position.y=0.62;r.bag.scale.set(1.1,0.5,0.45)});
  const w=wordAt(TN);let open=0;if(w)open=0.3+0.7*Math.abs(Math.sin((TN-w[1])*21));const sh=SW.has(norm((w||[''])[0]))?1:0;
  mouth.scale.set(0.3+0.1*sh+(eat?0.2:0),0.03+0.2*open+0.12*sh+(eat?0.2:0),0.14);drool.visible=false;
  hero.updateMatrixWorld(true);head.getWorldPosition(HP);hero.getWorldPosition(HEROPOS);
  hero.visible=!(t>=K('vez')+1.0&&t<K('vez')+99);
}
function applyProps(t){
  const scared=t>=TS-0.1;sEyes.forEach(e=>e.scale.setScalar(scared?1.8:1));sMouth.scale.set(scared?2:1,scared?3+Math.sin(t*30):1,1);
  sau.visible=t<TA;const sy=t>=TM?eio(seg(t,TM,TM+0.5)):0;sau.position.set(lerp(-3,0,eio(seg(t,TS,TS+0.5)))+0.1*Math.sin(t*40)*(t>=TS&&t<TM?1:0),lerp(0.6,0.55,sy),0);
  top.position.y=lerp(1.2,0.5,sy);if(t<TS)top.position.y=1.2;
  sw.scale.set(1,t>=TA?lerp(1,0.35,eio(seg(t,TA,TA+0.25))):1,1);
  const g=1+(t>=TE?4*eio(seg(t,TE,K('vez')+1.0)):0);sw.scale.set(g,(t>=TA?lerp(1,0.35,eio(seg(t,TA,TA+0.25))):1)*g,g);sw.position.y=2.6+(g-1)*0.0;
  MB.forEach((m,i)=>{const d=t-(TC+0.2);const on=d>0&&d<2.4;m.visible=on;if(!on)return;const a=(i/MB.length)*6.28;m.position.set(-3.6+Math.cos(a)*d*2.2*(1-0.3*d)+d*3.3,2.4+d*5-5*d*d+Math.sin(i)*0.3,1.0+Math.sin(a)*d*1.2);m.scale.setScalar(0.6+rnd(i))});
  const pk=eio(seg(t,TA-0.3,TA+0.15))*(1-eio(seg(t,TA+0.7,TA+1.2)));press.visible=pk>0.01;press.position.set(0,lerp(7,3.0,pk),0.5);
}
function applyEffects(t){}
const HC=[0,2.6,0.5];
const CUTS=[0,1.0,K('pendejo')-0.2,T_HOOKEND,K('agárrela'),K('cabrón'),TS-0.2,TM-0.15,K('báñela'),TC-0.1,K('humedad'),TU-0.1,K('descaro'),K('métele'),TA-0.4,K('compacta'),TE-0.3,K('vez'),K('así'),K('hocico')];
const hpa=(x,y,z)=>[HP.x+x,HP.y+y,HP.z+z];
const shots=[
 (u,t)=>({p:hpa(0,0.2,lerp(5.4,4.4,u)),l:HP.toArray(),f:38}),
 (u,t)=>({p:P([0,3.6,12],[0,3.4,10.5],u),l:[0,2.6,0.5],f:54}),
 (u,t)=>({p:hpa(0.8,0.1,lerp(4.4,3.6,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([0,3.8,14],[0.5,3.6,12.5],eout(u)),l:[0,2.6,0],f:54}),
 (u,t)=>({p:P([-2,3.4,8],[-1,3.4,6.5],u),l:HC,f:42}),
 (u,t)=>({p:hpa(0,0.1,lerp(5,4,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([2.4,3.6,6],[1.2,3.4,5],u),l:[0,2.9,0.5],f:38}),
 (u,t)=>({p:P([-1,3.0,7],[0,3.0,5.6],u),l:[0,2.9,0.5],f:36}),
 (u,t)=>({p:P([-1,3.8,11],[-2,3.6,9.5],u),l:[-2.5,3.0,0.8],f:54}),
 (u,t)=>({p:hpa(0,0.1,lerp(5,3.8,u)),l:HP.toArray(),f:36}),
 (u,t)=>({p:P([1.5,3.2,8],[0.5,3.0,6.4],u),l:[0.5,3.0,0.8],f:42}),
 (u,t)=>({p:P([0.5,3.6,9],[-0.5,3.4,7.5],u),l:[0,3.0,0.5],f:40}),
 (u,t)=>({p:hpa(-0.8,0,lerp(4.6,3.6,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([0,3.2,8],[0,3.0,6.4],u),l:HC,f:40}),
 (u,t)=>({p:P([0,2.4,12],[0,2.6,10.5],u),l:[0,3.6,0.5],f:58}),
 (u,t)=>({p:P([1.5,3.4,9],[0.5,3.2,7],u),l:[0,2.8,0.5],f:42}),
 (u,t)=>({p:hpa(0.8,0.2,lerp(4.6,3.6,u)),l:HP.toArray(),f:34}),
 (u,t)=>({p:P([0,3.6,11],[0,4.2,15],eio(u)),l:[0,4.4,0.5],f:56}),
 (u,t)=>({p:P([0,5,15],[0,5.6,12],u),l:[0,5,0.5],f:56}),
 (u,t)=>({p:P([0,5.4,12],[0,5.2,8],eio(u)),l:[0,5,0.5],f:48}),
];
function applyCam(t){
  let si=0;for(let i=0;i<CUTS.length;i++)if(t>=CUTS[i])si=i;
  const a=CUTS[si],b=CUTS[si+1]||END+1.5;const u=clamp((t-a)/(b-a));const r=shots[si](u,t);
  let fov=r.f;for(const ts of swT){const d=TN-ts;if(d>0&&d<0.5)fov-=9*Math.exp(-d*10)}
  const dc=t-a;if(dc<0.12&&si>0)fov-=4*(1-dc/0.12);
  let sh=0;[[TA+0.1,1.6],[TC,0.8],[TE,0.8],[K('vez')+1.0,1.4]].forEach(([ts,amp])=>{const d=t-ts;if(d>0&&d<0.6)sh+=amp*Math.exp(-d*7)});
  cam.position.set(r.p[0]+sh*0.12*Math.sin(t*95),r.p[1]+sh*0.12*Math.cos(t*81),r.p[2]);cam.up.set(0,1,0);cam.lookAt(r.l[0],r.l[1],r.l[2]);
  cam.fov=fov;cam.updateProjectionMatrix();
}
const FLASH=[[TA+0.1,1],[TC,0.6],[K('vez')+1.0,1],[T_HOOKEND,0.5]];
const HOOK_TEXT='SOLO MANOSEAS';const TITLE_HTML='CÓMO PREPARAR<br>UN SÁNDWICH';const TITLE_WORD='cómo';const PILL_TEXT='TUTORIAL #10 · CÓMO PREPARAR UN SÁNDWICH';const PILL=[K('cómo')+1.4,K('agárrela')+1.0];
