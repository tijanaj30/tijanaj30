const { chromium } = require('playwright'); const fs=require('fs');
(async () => { const [mode,s,e,out,...times]=process.argv.slice(2);
 const TL=JSON.parse(fs.readFileSync('/home/user/work/r8/build/timeline.json','utf8'));
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',err=>console.log('PAGEERR',err.message));
 await p.addInitScript(([tl,m])=>{window.TL=tl;window.MODE=m},[TL,mode]);
 await p.goto('file:///home/user/work/r8/overlay.html'); await p.evaluate(()=>window.ready);
 fs.mkdirSync(out,{recursive:true});
 const list=times.length?times.map(Number).map(t=>Math.round(t*30)):[]; if(!list.length) for(let f=+s;f<+e;f++) list.push(f);
 for(const f of list){ await p.evaluate(t=>window.render(t),f/30);
   if(mode==='K') await p.screenshot({path:`${out}/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:95});
   else await p.screenshot({path:`${out}/f${String(f).padStart(5,'0')}.png`,omitBackground:true}); }
 await b.close(); })();
