const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{const TL=JSON.parse(fs.readFileSync('build/timeline.json'));const b=await chromium.launch();const p=await b.newPage();
await p.addInitScript(tl=>{window.TL=tl},TL);await p.goto('file:///home/user/work/act/overlay.html');await p.evaluate(()=>window.ready);
console.log(JSON.stringify(await p.evaluate(()=>A)));await b.close()})();
