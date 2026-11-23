const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1400},deviceScaleFactor:1});
 await p.goto('file://'+__dirname+'/karusel2.html'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(500);
 const out=process.argv[2]||'out'; require('fs').mkdirSync(out,{recursive:true});
 for(let i=1;i<=8;i++){ await p.locator('#s'+i).screenshot({path:`${out}/slajd${i}.png`}); }
 await b.close();
})();
