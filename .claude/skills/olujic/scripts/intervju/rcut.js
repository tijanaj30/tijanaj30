const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{ const [cfg,out,...times]=process.argv.slice(2); const C=JSON.parse(cfg);
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.addInitScript(c=>{window.CUT=c},C); await p.goto('file:///home/user/work/r5/cut.html'); await p.evaluate(()=>window.ready);
 fs.mkdirSync(out,{recursive:true}); const N=Math.round((C.t1-C.t0)*30);
 const list=times.length?times.map(Number).map(t=>Math.round(t*30)):[...Array(N).keys()];
 for(const f of list){ await p.evaluate(t=>window.render(t),f/30); await p.screenshot({path:`${out}/f${String(f).padStart(4,'0')}.png`,omitBackground:true}); }
 await b.close(); })();
