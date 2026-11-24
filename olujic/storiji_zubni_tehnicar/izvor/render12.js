const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+__dirname+'/story12.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
 for(let i=1;i<=2;i++) await p.locator('#s'+i).screenshot({path:`s${i}.png`});await b.close();})();
