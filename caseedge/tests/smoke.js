const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('**/cdnjs.cloudflare.com/**', r => {
    const u = r.request().url();
    const f = u.includes('worker') ? 'pdf.worker.min.js' : 'pdf.min.js';
    r.fulfill({ path: process.argv[2] + '/vendor/' + f, contentType: 'application/javascript' });
  });
  await p.route('**/fonts.*/**', r => r.abort());
  await p.goto('file://' + process.argv[3]);
  await p.waitForTimeout(800);
  const vis = await p.evaluate(() => [...document.querySelectorAll('[id^=view], section[data-view], .view')].filter(e => e.offsetParent).length);
  const cite = await p.$('[data-cite], .cite');
  if (cite) { await cite.click(); await p.waitForTimeout(1500); }
  const pane = await p.evaluate(() => { const c = document.querySelector('.cpane'); return c ? Math.round(c.getBoundingClientRect().width) : null; });
  const canv = await p.evaluate(() => document.querySelectorAll('.cpane canvas').length);
  console.log(JSON.stringify({ errs, vis, pane, canv }));
  await b.close();
})();
