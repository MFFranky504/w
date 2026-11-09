<!doctype html>
<html><head><meta charset="utf-8">
<style>
html,body{margin:0;background:#000;overflow:hidden}
#c{display:block;width:1080px;height:1920px;filter:contrast(1.08) saturate(1.18)}
#ui{position:absolute;left:0;top:0;width:1080px;height:1920px;pointer-events:none;font-family:"DejaVu Sans","Inter Display",sans-serif;font-weight:900;overflow:hidden}
#vig{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.5) 100%)}
#sub{position:absolute;left:30px;right:30px;top:1280px;text-align:center;line-height:1.05;font-size:100px;color:#fff;text-transform:uppercase;-webkit-text-stroke:15px #000;paint-order:stroke fill;letter-spacing:-1px;text-shadow:0 9px 0 #000}
#sub span{display:inline-block;margin:0 30px}
#sub .sw{color:#ff3b30}
#flash{position:absolute;inset:0;background:#fff;opacity:0}
#speed{position:absolute;inset:0;opacity:0;background:repeating-conic-gradient(from 0deg at 50% 45%,rgba(255,255,255,0) 0deg 4deg,rgba(255,255,255,.55) 4deg 5deg,rgba(255,255,255,0) 5deg 9deg);-webkit-mask:radial-gradient(circle at 50% 45%,transparent 25%,#000 70%);mask:radial-gradient(circle at 50% 45%,transparent 25%,#000 70%)}
.big{position:absolute;left:0;right:0;text-align:center;color:#fff;-webkit-text-stroke:16px #000;paint-order:stroke fill;text-shadow:0 12px 0 #000;display:none}
#hook{top:250px;font-size:72px;line-height:1.0;white-space:nowrap}
#hook b{background:#ff2d2d;padding:0 28px;display:inline-block;border:10px solid #000;-webkit-text-stroke:0;text-shadow:none;transform:rotate(-3deg)}
#title{top:560px;font-size:118px;line-height:.95;color:#ffe600}
#cnt{top:420px;font-size:520px;color:#ffe600}
#pill{position:absolute;left:50%;top:150px;transform:translateX(-50%);background:#ffe600;color:#000;font-size:34px;padding:14px 26px;border-radius:60px;border:6px solid #000;white-space:nowrap;box-shadow:0 8px 0 #000;display:none}
#logo{position:absolute;right:36px;top:60px;color:#fff;font-size:38px;-webkit-text-stroke:8px #000;paint-order:stroke fill;opacity:.9}
#end{position:absolute;inset:0;background:#000;display:none;color:#fff;text-align:center}
#end .a{position:absolute;top:760px;width:100%;font-size:130px;color:#ffe600}
#end .b{position:absolute;top:960px;width:100%;font-size:54px;opacity:.85}
#end .c{position:absolute;top:1100px;width:100%;font-size:44px;color:#ff3b30}
</style></head><body>
<canvas id="c" width="1080" height="1920"></canvas>
<div id="ui"><div id="vig"></div><div id="speed"></div>
<div id="pill">TUTORIAL #8 · CÓMO ABRIR UNA PUERTA</div><div id="logo">PUTOR.IALES</div>
<div class="big" id="hook"><b>12 AÑOS ENCERRADO</b></div><div class="big" id="title">CÓMO ABRIR<br>UNA PUERTA</div><div class="big" id="cnt">1</div>
<svg id="crack" viewBox="0 0 1080 1920" style="position:absolute;inset:0;opacity:0"><g stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".9"><path d="M540 760 L470 600 L500 470 M540 760 L650 640 L640 500 M540 760 L420 840 L300 800 M540 760 L690 880 L820 860 M540 760 L520 930 L580 1080 M470 600 L390 580 M650 640 L740 620 M420 840 L380 960"/></g></svg>
<div id="sub"></div><div id="flash"></div>
<div id="end"><div class="a">FIN</div><div class="b">PUTOR.IALES</div><div class="c">tutoriales que nadie necesita</div></div></div>
<script type="module">
import * as THREE from './node_modules/three/build/three.module.js';
const W=1080,H=1920;
const words=(await (await fetch('assets11/words_t.json')).json()).words;
const END=words[words.length-1][2];
const norm=x=>x.toLowerCase().replace(/[^a-záéíóúñü]/g,'');
const K=(w,n=0)=>{let c=0;for(const x of words){if(norm(x[0])===norm(w)){if(c===n)return x[1];c++}}throw new Error('no '+w)};
const renderer=new THREE.WebGLRenderer({canvas:document.getElementById('c'),antialias:true});
renderer.setPixelRatio(1);renderer.setSize(W,H,false);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x14120d);
const cam=new THREE.PerspectiveCamera(45,W/H,0.1,200);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const seg=(t,a,b)=>clamp((t-a)/(b-a));
const eio=x=>x*x*(3-2*x), eout=x=>1-Math.pow(1-x,3), ein=x=>x*x*x, eback=x=>{const c=1.70158;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const lerp=(a,b,k)=>a+(b-a)*k;
const mat=(c,o={})=>new THREE.MeshStandardMaterial({color:c,flatShading:true,roughness:.85,metalness:0,...o});
const mk=(geo,m,x=0,y=0,z=0,par=null)=>{const o=new THREE.Mesh(geo,m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;if(par)par.add(o);return o};
const grp=(x=0,y=0,z=0,par=null)=>{const g=new THREE.Group();g.position.set(x,y,z);if(par)par.add(g);return g};
const rnd=(i)=>{const s=Math.sin(i*127.1+311.7)*43758.5453;return s-Math.floor(s)};
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
function canvasTex(w,h,draw){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.userData={c};return t}

// ---------- lights (night, cozy)
const hemi=new THREE.HemisphereLight(0xb8b8ff,0x4a3a6a,1.25);scene.add(hemi);
const moonL=new THREE.DirectionalLight(0xcfd8ff,1.9);moonL.position.set(-8,16,10);moonL.castShadow=true;
moonL.shadow.mapSize.set(2048,2048);const sc=moonL.shadow.camera;sc.left=-14;sc.right=14;sc.top=14;sc.bottom=-14;sc.near=1;sc.far=50;moonL.shadow.bias=-0.0005;
scene.add(moonL);
const warm=new THREE.PointLight(0xffb060,28,26);warm.position.set(4.6,4.2,-1.5);scene.add(warm);

// ---------- hero
const SKINC=new THREE.Color(0xf2b48a),PALE=new THREE.Color(0xc8b6b0);
const skinM=mat(0xf2b48a);
const hero=grp();scene.add(hero);
const pelvis=grp(0,1.8,0,hero);
const PJ=mat(0x4d7c3a),PJP=mat(0x5a4a3a);
mk(new THREE.SphereGeometry(0.58,8,6),PJP,0,0,0,pelvis).scale.set(1.1,0.6,0.85);
const torsoP=grp(0,0,0,pelvis);
const torso=mk(new THREE.IcosahedronGeometry(1,1),PJ,0,0.68,0,torsoP);torso.scale.set(0.85,0.78,0.78);
for(let i=0;i<3;i++)mk(new THREE.BoxGeometry(0.16,0.16,0.05),mat(0xffffff),0,0.35+i*0.45,0.72,torsoP);
const arms=[-1,1].map(s=>{const g=grp(s*0.95,1.05,0,torsoP);mk(new THREE.CylinderGeometry(0.2,0.17,1.3,6).translate(0,-0.65,0),PJ,0,0,0,g);mk(new THREE.SphereGeometry(0.24,6,5),skinM,0,-1.38,0,g);return g});
const neck=mk(new THREE.CylinderGeometry(0.2,0.24,0.4,6).translate(0,0.2,0),skinM,0,1.3,0,torsoP);
const headP=grp(0,1.7,0,torsoP);
const head=grp(0,0.78,0,headP);
mk(new THREE.IcosahedronGeometry(0.88,1),skinM,0,0,0,head).scale.set(1,0.98,0.96);
mk(new THREE.SphereGeometry(0.2,6,5),skinM,-0.9,0,0,head);mk(new THREE.SphereGeometry(0.2,6,5),skinM,0.9,0,0,head);
mk(new THREE.IcosahedronGeometry(0.2,0),new THREE.MeshStandardMaterial({color:0xe0976d,flatShading:true}),0,-0.08,0.88,head).scale.set(1,1,1.3);
const spiralTex=canvasTex(128,128,(g,w,h)=>{g.fillStyle='#fff';g.fillRect(0,0,w,h);g.strokeStyle='#111';g.lineWidth=8;g.beginPath();for(let a=0;a<22;a+=0.1){const r=a*2.6;g.lineTo(w/2+Math.cos(a)*r,h/2+Math.sin(a)*r)}g.stroke()});
const eyeRig=[-1,1].map(s=>{
  const e=mk(new THREE.SphereGeometry(0.29,10,8),mat(0xffe3e3),s*0.36,0.16,0.7,head);
  const pup=mk(new THREE.SphereGeometry(0.1,7,6),mat(0),0,0,0.25,e);
  const spiral=new THREE.Mesh(new THREE.CircleGeometry(0.2,16),new THREE.MeshBasicMaterial({map:spiralTex}));spiral.position.set(0,0,0.275);e.add(spiral);spiral.visible=false;
  const lid=mk(new THREE.SphereGeometry(0.31,10,5,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({color:0xd99a72,flatShading:true}),0,0,0,e);
  const bag=mk(new THREE.SphereGeometry(0.28,7,4),mat(0x5a3a8a),s*0.36,-0.16,0.72,head);bag.scale.set(1.1,0.35,0.45);
  const brow=mk(new THREE.BoxGeometry(0.5,0.1,0.12),mat(0x2a1a0a),s*0.36,0.66,0.78,head);
  return {e,pup,spiral,lid,bag,brow,s};
});
const mouth=mk(new THREE.SphereGeometry(0.5,8,6),mat(0x4a0d0d),0,-0.46,0.7,head);
const drool=mk(new THREE.CylinderGeometry(0.05,0.07,0.8,5).translate(0,-0.4,0),mat(0x9fe8ff,{transparent:true,opacity:.85}),0.2,-0.6,0.86,head);
const legs=[-1,1].map(s=>{
  const th=grp(s*0.45,-0.1,0,pelvis);mk(new THREE.CylinderGeometry(0.26,0.22,0.9,6).translate(0,-0.45,0),PJP,0,0,0,th);
  const kn=grp(0,-0.9,0,th);mk(new THREE.CylinderGeometry(0.22,0.2,0.9,6).translate(0,-0.45,0),PJP,0,0,0,kn);
  mk(new THREE.SphereGeometry(0.3,7,5),mat(0xffffff),0,-0.8,0.1,kn).scale.set(1,0.7,1.25);
  return {th,kn};
});
const HP=new THREE.Vector3(),HEROPOS=new THREE.Vector3();

// ---------- extras: beard, hands, pizza, zzz
const beard=grp(0,-0.78,0.35,head);
const beardM=mat(0x4a2f1a);
const beardCone=mk(new THREE.ConeGeometry(0.75,1.6,7).translate(0,0.8,0),beardM,0,0,0,beard);beardCone.scale.set(1,1,0.8);
const HANDS=[[-1.5,1.7,0.9],[1.5,1.7,0.9],[-1.5,1.7,-2.4],[1.5,1.7,-2.4]].map((p,i)=>{
  const g=grp(p[0],p[1],p[2]);scene.add(g);const sk=mat(0xf2b48a);
  mk(new THREE.SphereGeometry(0.5,7,5),sk,0,0.4,0,g);
  for(let f=0;f<4;f++){const fg=grp((f-1.5)*0.24,0.8,0,g);mk(new THREE.CylinderGeometry(0.09,0.08,0.55,5).translate(0,0.27,0),sk,0,0,0,fg);fg.userData.f=f}
  mk(new THREE.CylinderGeometry(0.28,0.3,1.4,6).translate(0,-0.6,0),mat(0xe9ecff),0,0,0,g);g.visible=false;g.userData.home=p;return g});
const pizzas=[[-3.2,3.2],[-4.2,4.6],[3.6,4.2],[5.0,2.4]].map(([x,z],i)=>{const g=grp(x,i*0.01,z);scene.add(g);for(let k=0;k<=i%3+1;k++){mk(new THREE.BoxGeometry(1.8,0.22,1.8),mat(k%2?0xd9a066:0xe9c58a),0,0.12+k*0.24,0,g).rotation.y=k*0.4}mk(new THREE.CylinderGeometry(0.5,0.5,0.05,8),mat(0xc0392b),0.2,0.12+(i%3+1)*0.24+0.05,0.1,g);return g});
const zTex=canvasTex(128,128,(g,w,h)=>{g.fillStyle='#fff';g.strokeStyle='#111';g.lineWidth=10;g.font='900 110px DejaVu Sans';g.textAlign='center';g.strokeText('Z',64,100);g.fillText('Z',64,100)});
const ZZ=[0,1,2].map(i=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(1.2,1.2),new THREE.MeshBasicMaterial({map:zTex,transparent:true}));m.visible=false;scene.add(m);return m});


HANDS.forEach(h=>h.visible=false);beard.visible=false;pizzas.forEach(p=>p.visible=false);


let TN=0;
const wordAt=t=>words.find(w=>t>=w[1]&&t<w[2]+0.02);
const P=(a,b,k)=>a.map((v,i)=>lerp(v,b[i],k));
