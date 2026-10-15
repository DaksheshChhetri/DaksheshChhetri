const { chromium } = require('playwright');
const S = process.argv[2], FILE = process.argv[3], OUT = process.argv[4] || 'cur', W = +(process.argv[5] || 1440);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: W, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('**/cdnjs.cloudflare.com/**', r => {
    const u = r.request().url();
    r.fulfill({ path: S + '/vendor/' + (u.includes('worker') ? 'pdf.worker.min.js' : 'pdf.min.js'), contentType: 'application/javascript' });
  });
  await p.route('**/fonts.*/**', r => r.abort());
  await p.goto('file://' + FILE);
  await p.evaluate(() => localStorage.clear());
  await p.reload();
  await p.waitForTimeout(400);
  const views = (process.argv[6] || 'chronology,signals,ledger,demand,review').split(',');
  for (const v of views) {
    await p.evaluate(v => { go(v); }, v);
    await p.waitForTimeout(400);
    if (v === 'demand') { await p.screenshot({ path: `${S}/shots/${OUT}-${v}.png` }); continue; }
    const h = await p.evaluate(() => document.querySelector('#main').scrollHeight);
    await p.setViewportSize({ width: W, height: h });
    await p.waitForTimeout(300);
    await p.screenshot({ path: `${S}/shots/${OUT}-${v}.png` });
    await p.setViewportSize({ width: W, height: 900 });
  }
  console.log(JSON.stringify(errs));
  await b.close();
})();
