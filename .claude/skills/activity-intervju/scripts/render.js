// usage: node render2.js <startFrame> <endFrame> <outDir> [f1 f2 ...]
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [s, e, out, ...list0] = process.argv.slice(2); const D = '/home/user/work/act';
  const TL = JSON.parse(fs.readFileSync(`${D}/build/timeline.json`, 'utf8')); const NF = fs.readdirSync(`${D}/frames`).length;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', err => console.log('PAGEERR', err.message));
  await p.addInitScript(tl => { window.TL = tl }, TL);
  await p.goto(`file://${D}/overlay.html`); await p.evaluate(() => window.ready);
  fs.mkdirSync(out, { recursive: true });
  const list = list0.length ? list0.map(Number) : []; if (!list.length) for (let f = +s; f < +e; f++) list.push(f);
  for (const f of list) {
    const n = String(Math.min(f + 1, NF)).padStart(5, '0');
    await p.evaluate(async ([n, t, D]) => {
      const v = document.getElementById('vid'), src = `file://${D}/frames/f${n}.jpg`;
      const m = window.needMask(t); const P = document.getElementById('person');
      const jobs = [];
      if (v.src !== src) { v.src = src; jobs.push(v.decode()); }
      if (m && P.src !== src) { P.src = src; P.style.webkitMaskImage = P.style.maskImage = `url(file://${D}/masks/m${n}.png)`; jobs.push(P.decode()); }
      await Promise.all(jobs); window.render(t, m);
    }, [n, f / 30, D]);
    if (await p.evaluate(t => window.needMask(t), f / 30)) await p.waitForTimeout(30);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93 });
  }
  await b.close();
})();
