const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const vs=(process.argv[2]||'1,2,3,4,5,6').split(',');
 for(const v of vs){const p=await b.newPage({viewport:{width:1080,height:1350}});
  p.on('console',m=>console.log(v,m.text())); p.on('pageerror',e=>console.log(v,'ERR',e.message));
  await p.goto('file://'+__dirname+'/scene.html?v='+v); await p.waitForFunction(()=>window.DONE,null,{timeout:180000});
  await p.screenshot({path:`raw${v}.png`}); await p.close(); console.log('ok',v);}
 await b.close();})();
