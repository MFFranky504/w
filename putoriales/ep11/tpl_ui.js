// ---------- overlays + subtitles
const phrases=[];{let cur=[];words.forEach(w=>{cur.push(w);if(/[.?!,]|\.\.\.$/.test(w[0])||cur.length>=3){phrases.push(cur);cur=[]}});if(cur.length)phrases.push(cur)}
const $=id=>document.getElementById(id);
const subEl=$('sub'),endEl=$('end'),flash=$('flash'),speed=$('speed'),hook=$('hook'),title=$('title'),cnt=$('cnt'),pill=$('pill');
hook.innerHTML='<b>'+HOOK_TEXT+'</b>';title.innerHTML=TITLE_HTML;pill.textContent=PILL_TEXT;
function pop(d,amp=0.45,k=16){return d<0?1:1+amp*Math.exp(-d*k)}
const crackEl=document.getElementById('crack');
function applyUI(t){
  let idx=-1;for(let i=0;i<phrases.length;i++){const p=phrases[i],n=phrases[i+1];const st=p[0][1]-0.04,en=n?n[0][1]-0.04:p[p.length-1][2]+0.3;if(t>=st&&t<en){idx=i;break}}
  if(idx<0||t>END+0.1)subEl.innerHTML='';
  else subEl.innerHTML=phrases[idx].map(w=>{const sw=isSW(w[0]);const d=t-w[1];const act=d>=0&&t<w[2]+0.1;const sc=d<0?0.001:(pop(d,sw?0.5:0.4)*(sw?1.08:1));const rot=sw&&d>=0&&d<0.4?-4*Math.exp(-d*8):0;
    return `<span class="${sw?'sw':''}" style="transform:scale(${sc}) rotate(${rot}deg);color:${act&&!sw?'#ffe600':''}">${w[0].replace(/\.\.\.|[.,¿?]/g,'')}</span>`}).join('');
  const hk=t>=0&&t<T_HOOKEND;hook.style.display=hk?'block':'none';if(hk)hook.style.transform=`scale(${pop(t,0.3,14)}) rotate(${-2+Math.sin(t*30)*0.6}deg)`;
  const T3=K(TITLE_WORD);const ts=t>=T3&&t<T3+1.4;title.style.display=ts?'block':'none';if(ts){const d=t-T3;title.style.transform=`scale(${pop(d,1.4,11)}) rotate(${-4+Math.sin(t*25)*(d<0.3?2:0.4)}deg)`}
  cnt.style.display='none';
  let f=0;FLASH.forEach(([s,a])=>{const d=t-s;if(d>=0&&d<0.18)f=Math.max(f,a*(1-d/0.18))});
  swT.forEach(s=>{const d=t-s;if(d>=0&&d<0.1)f=Math.max(f,0.35*(1-d/0.1))});flash.style.opacity=f;
  let sp=0;swT.forEach(s=>{const d=t-s;if(d>=0&&d<0.45)sp=Math.max(sp,0.8*(1-d/0.45))});speed.style.opacity=sp;
  pill.style.display=(t>=PILL[0]&&t<PILL[1])?'block':'none';
  if(crackEl){crackEl.style.opacity=0}
  endEl.style.display=t>=END+0.1?'block':'none';$('logo').style.display=t<END+0.1?'block':'none';
}
window.renderFrame=(tn)=>{TN=tn;const t=tn;applyHero(t);applyProps(t);applyEffects(t);applyCam(t);renderer.render(scene,cam);applyUI(tn);return true};
window.ready=true;
</script></body></html>

window.getMeta=()=>({cuts:CUTS,sw:swT});
