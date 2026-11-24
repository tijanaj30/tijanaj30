const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1400}});
 await p.goto('file://'+__dirname+'/karusel.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(700);
 const out=process.argv[2]||'out';require('fs').mkdirSync(out,{recursive:true});
 const n=await p.locator('.s').count();for(let i=1;i<=n;i++){await p.locator('.s').nth(i-1).screenshot({path:`${out}/slajd${i}.png`});}
 await b.close();})();
