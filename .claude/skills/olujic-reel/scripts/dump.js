const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{ const TL=JSON.parse(fs.readFileSync('/home/user/work/build/timeline.json','utf8'));
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.error('PAGEERR',e.message)); p.on('console',m=>{if(/MISSING/.test(m.text()))console.error(m.text())});
 await p.addInitScript(tl=>{window.TL=tl},TL); await p.goto('file:///home/user/work/v2/overlay.html'); await p.evaluate(()=>window.ready);
 const r=await p.evaluate(()=>({K:window.K,SFX:window.SFX})); fs.writeFileSync('/home/user/work/v2/sfx_events.json',JSON.stringify(r)); await b.close(); })();
