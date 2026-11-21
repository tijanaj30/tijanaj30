// usage: node render.js <startFrame> <endFrame> <outDir> [f1 f2 ...]   (renders final composited JPG frames)
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [s, e, out, ...list0] = process.argv.slice(2); const D = '/home/user/work/act';
  const TL = JSON.parse(fs.readFileSync(`${D}/build/timeline.json`, 'utf8'));
  const NF = fs.readdirSync(`${D}/frames`).length;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', err => console.log('PAGEERR', err.message)); p.on('console', m => console.log('CONSOLE', m.text()));
  await p.addInitScript(tl => { window.TL = tl }, TL);
  await p.goto(`file://${D}/overlay.html`); await p.evaluate(() => window.ready);
  fs.mkdirSync(out, { recursive: true });
  const list = list0.length ? list0.map(Number) : []; if (!list.length) for (let f = +s; f < +e; f++) list.push(f);
  for (const f of list) {
    const src = `file://${D}/frames/f${String(Math.min(f + 1, NF)).padStart(5, '0')}.jpg`;
    await p.evaluate(async ([src, t]) => { const v = document.getElementById('vid'); if (v.src !== src) { v.src = src; await v.decode(); } window.render(t) }, [src, f / 30]);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93 });
  }
  await b.close();
})();
