const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+__dirname+'/'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
 await p.locator('.s').first().screenshot({path:process.argv[3]});await b.close();})();
