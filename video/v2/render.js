// usage: node render.js <startFrame> <endFrame> <outDir> [times...]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [s, e, out, ...times] = process.argv.slice(2);
  const TL = JSON.parse(fs.readFileSync('/home/user/work/build/timeline.json', 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  p.on('console', m => { if (/MISSING|Error/.test(m.text())) console.log('PAGE:', m.text()); });
  p.on('pageerror', err => { console.log('PAGEERR', err.message); });
  await p.addInitScript(tl => { window.TL = tl; }, TL);
  await p.goto('file:///home/user/work/v2/overlay.html');
  await p.evaluate(() => window.ready);
  fs.mkdirSync(out, { recursive: true });
  const list = times.length ? times.map(Number).map(t => Math.round(t * 30)) : [];
  if (!list.length) for (let f = +s; f < +e; f++) list.push(f);
  for (const f of list) {
    await p.evaluate(t => window.render(t), f / 30);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.png`, omitBackground: true });
  }
  await b.close();
})();
