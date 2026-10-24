const { chromium } = require('playwright');
const S = process.argv[2], FILE = process.argv[3];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const out = {};
  for (const [W, H, tag] of [[1440, 900, 'split'], [390, 844, 'phone']]) {
    const p = await b.newPage({ viewport: { width: W, height: H } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**/cdnjs.cloudflare.com/**', r => r.fulfill({ path: S + '/vendor/' + (r.request().url().includes('worker') ? 'pdf.worker.min.js' : 'pdf.min.js'), contentType: 'application/javascript' }));
    await p.route('**/fonts.*/**', r => r.abort());
    await p.goto('file://' + FILE); await p.evaluate(() => localStorage.clear()); await p.reload(); await p.waitForTimeout(300);
    for (const v of await p.evaluate(() => VIEWS)) {
      await p.evaluate(v => go(v), v); await p.waitForTimeout(250);
      if (tag === 'split') {
        await p.evaluate(() => { const c = document.querySelector('.view:not([hidden]) [data-cite]'); c && c.click(); });
        await p.waitForTimeout(1100);
      }
      const m = await p.evaluate(() => {
        const main = document.querySelector('#main'), pane = document.querySelector('#cpane');
        const over = [...document.querySelectorAll('.view:not([hidden]) .table-wrap')].filter(w => w.scrollWidth > w.clientWidth + 1).length;
        return { main: Math.round(main.getBoundingClientRect().width), pane: pane.hidden ? 0 : Math.round(pane.getBoundingClientRect().width), hscroll: main.scrollWidth > main.clientWidth + 1, tableScroll: over };
      });
      out[tag + ':' + v] = m;
      await p.screenshot({ path: `${S}/shots/${tag}-${v}.png` });
      if (tag === 'split') { await p.evaluate(() => closeCite()); await p.waitForTimeout(450); }
    }
    out[tag + ':errs'] = errs;
    await p.close();
  }
  console.log(JSON.stringify(out, null, 0));
  await b.close();
})();
