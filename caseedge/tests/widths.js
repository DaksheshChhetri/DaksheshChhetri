const { chromium } = require('playwright');
const S = process.argv[2], FILE = process.argv[3];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const out = [];
  for (const W of [1280, 1440, 1728, 1920]) for (const rail of [0, 1]) {
    const p = await b.newPage({ viewport: { width: W, height: 900 } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**/cdnjs.cloudflare.com/**', r => r.fulfill({ path: S + '/vendor/' + (r.request().url().includes('worker') ? 'pdf.worker.min.js' : 'pdf.min.js'), contentType: 'application/javascript' }));
    await p.route('**/fonts.*/**', r => r.abort());
    await p.goto('file://' + FILE); await p.evaluate(r => { localStorage.clear(); localStorage.setItem('ce-rail', r ? '1' : '0') }, rail); await p.reload(); await p.waitForTimeout(300);
    const res = [];
    for (const v of ['chronology', 'signals', 'ledger', 'demand', 'review']) {
      await p.evaluate(v => go(v), v); await p.waitForTimeout(150);
      if (v === 'ledger') { await p.click('#ledExpand'); await p.waitForTimeout(100) }
      if (v === 'chronology') { await p.click('#expandAll'); await p.waitForTimeout(100) }
      res.push(v[0] + ':' + await p.evaluate(() => [...document.querySelectorAll('.view:not([hidden]) .table-wrap')].filter(w => w.scrollWidth > w.clientWidth + 1).length + (document.querySelector('#main').scrollWidth > document.querySelector('#main').clientWidth + 1 ? 'H' : '')));
    }
    out.push(`${W}${rail ? ' rail' : ''}  ${res.join(' ')}  errs:${errs.length}`);
    await p.close();
  }
  console.log(out.join('\n'));
  await b.close();
})();
