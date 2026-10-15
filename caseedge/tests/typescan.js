const { chromium } = require('playwright');
const S = process.argv[2], FILE = process.argv[3];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.route('**/cdnjs.cloudflare.com/**', r => r.fulfill({ path: S + '/vendor/' + (r.request().url().includes('worker') ? 'pdf.worker.min.js' : 'pdf.min.js'), contentType: 'application/javascript' }));
  await p.route('**/fonts.*/**', r => r.abort());
  await p.goto('file://' + FILE); await p.evaluate(() => localStorage.clear()); await p.reload(); await p.waitForTimeout(300);
  const SKIP = 'h1,h2,h3,th,button,.btn,.cite,.tmap,.tgl,.chips,.score label,.score b,.tl-facts b,.facts dt,.doc,.pane-h,.pane-f,.tb,.crumbs,.tabbar,.mbar,.sidebar,.pop,.mseg,.box-t,kbd,.tmap-legend,.lg';
  for (const v of ['chronology', 'signals', 'ledger', 'demand', 'review']) {
    await p.evaluate(x => go(x), v); await p.waitForTimeout(150);
    if (v === 'ledger') await p.click('#ledExpand');
    if (v === 'chronology') await p.evaluate(() => toggleRow(3, true));
    await p.waitForTimeout(150);
    const res = await p.evaluate(SKIP => {
      const roots = [document.querySelector('.view:not([hidden])'), document.querySelector('#head')];
      const seen = {};
      roots.forEach(root => {
        const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        let n; while ((n = w.nextNode())) {
          if (!n.textContent.trim()) continue;
          const el = n.parentElement; if (!el || el.closest(SKIP) || !el.getClientRects().length) continue;
          const cs = getComputedStyle(el);
          const fam = cs.fontFamily.split(',')[0].replace(/"/g, '');
          const k = cs.fontSize + ' ' + fam;
          (seen[k] = seen[k] || []).push(n.textContent.trim().slice(0, 28));
        }
      });
      return Object.entries(seen).map(([k, v]) => `${k} ×${v.length}  e.g. "${v[0]}"`);
    }, SKIP);
    console.log(v.padEnd(10), '\n   ' + res.join('\n   '));
  }
  await b.close();
})();
