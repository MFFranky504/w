const {chromium}=require('playwright');
const fs=require('fs');
const [,, start, end, step, outdir, port]=process.argv;
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto(`http://localhost:${port||8765}/scene.html`);
  await p.waitForFunction('window.ready===true',{timeout:60000});
  fs.mkdirSync(outdir,{recursive:true});
  const s=+start,e=+end,st=+step; // frame indices at 30fps
  for(let f=s;f<=e;f+=st){
    await p.evaluate(t=>window.renderFrame(t),f/30);
    await p.screenshot({path:`${outdir}/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});
  }
  await b.close();
})();
