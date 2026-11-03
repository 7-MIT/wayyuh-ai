// Renders trailer.html frame by frame: node render.js <outDir> [fps] [workers] [t1,t2,...]
const { chromium } = require('playwright'); const fs = require('fs');
const out = process.argv[2], fps = +(process.argv[3] || 24), workers = +(process.argv[4] || 4), only = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
const DUR = 48; fs.mkdirSync(out, { recursive: true });
(async () => {
  const frames = only ? only.map(t => ({ n: Math.round(t * fps), t })) : Array.from({ length: DUR * fps }, (_, n) => ({ n, t: n / fps }));
  const b = await chromium.launch(); let done = 0;
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
    p.on('pageerror', e => console.log('pageerror', e.message));
    await p.goto('http://localhost:8099/trailer/trailer.html'); const missing = await p.evaluate(() => window.ready);
    if (w === 0 && missing.length) console.log('missing assets:', missing);
    for (let i = w; i < frames.length; i += workers) {
      const f = frames[i]; await p.evaluate(t => window.draw(t), f.t);
      const buf = await p.locator('#c').screenshot({ type: 'jpeg', quality: 93 });
      fs.writeFileSync(`${out}/f${String(f.n).padStart(5, '0')}.jpg`, buf);
      if (++done % 100 === 0) console.log('frames', done, '/', frames.length);
    }
  }));
  await b.close(); console.log('done', frames.length);
})();
