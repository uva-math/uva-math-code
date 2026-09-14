// Check every rendered table page after a Jekyll build and local preview start.
// Usage: node scripts/test_table_accessibility.cjs SITE [URL]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const site = path.resolve(process.argv[2] || '_site');
const base = process.argv[3] || 'http://127.0.0.1:4173';

function tablePages(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) return tablePages(file);
    if (!file.endsWith('.html')) return [];
    return /<main\b[\s\S]*<table\b/i.test(fs.readFileSync(file, 'utf8'))
      ? [path.relative(site, file)] : [];
  });
}

(async () => {
  const pages = tablePages(site);
  assert(pages.length, 'No table pages found');
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  let keyboardChecks = 0;
  try {
    for (const [width, theme] of [[320, 'dark'], [400, 'light'], [1280, 'light']]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await context.addInitScript(value => localStorage.setItem('theme', value), theme);
      // Calendar contents are unrelated to the static tables being tested.
      await context.route('**/calendar/v3/calendars/**', route => route.fulfill({ json: { items: [] } }));
      const page = await context.newPage();
      for (const file of pages) {
        await page.goto(base + '/' + file.split('/').map(encodeURIComponent).join('/'), { waitUntil: 'load' });
        await page.evaluate(async () => { await document.fonts.ready; });
        const result = await page.evaluate(() => {
          const splitWords = [];
          for (const cell of document.querySelectorAll('main td, main th')) {
            const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
            for (let text; (text = walker.nextNode());) {
              if (text.parentElement.closest('math, .katex, mjx-container, script, style')) continue;
              for (const word of text.data.matchAll(/[A-Za-z]{4,}/g)) {
                const range = document.createRange();
                range.setStart(text, word.index);
                range.setEnd(text, word.index + word[0].length);
                const lines = new Set([...range.getClientRects()].filter(r => r.width > 0).map(r => Math.round(r.top)));
                if (lines.size > 1) splitWords.push(word[0]);
              }
            }
          }
          const wrappers = [...document.querySelectorAll('main .table-responsive')];
          const invalidNames = wrappers.flatMap(el => {
            const ids = (el.getAttribute('aria-labelledby') || '').trim().split(/\s+/).filter(Boolean);
            const targets = ids.map(id => document.getElementById(id));
            const name = (ids.length
              ? targets.map(target => target?.textContent || '').join(' ')
              : el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim();
            if (ids.some(id => document.querySelectorAll('#' + CSS.escape(id)).length !== 1)) {
              return [{ name, reason: 'Label reference must identify one element' }];
            }
            if (!name || /^(?:table|region|table region)(?:\s+\d+)?$/i.test(name)) {
              return [{ name, reason: 'Table region needs a descriptive name' }];
            }
            return [];
          });
          const inaccessible = wrappers
            .filter(el => el.scrollWidth > el.clientWidth + 1 && (el.tabIndex < 0 || !(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby'))));
          return {
            overflow: document.documentElement.scrollWidth > innerWidth + 1,
            splitWords: splitWords.slice(0, 10), inaccessible: inaccessible.length, invalidNames
          };
        });
        if (result.overflow || result.splitWords.length || result.inaccessible || result.invalidNames.length) errors.push({ file, width, theme, ...result });
        if (width === 320 && ['schedule/index.html', 'seminars/algebra/2009-10/index.html'].includes(file)) {
          const wrappers = page.locator('main .table-responsive');
          for (let i = 0; i < await wrappers.count(); i++) {
            const wrapper = wrappers.nth(i);
            if (!await wrapper.evaluate(el => el.scrollWidth > el.clientWidth + 10)) continue;
            await wrapper.focus();
            await page.keyboard.press('ArrowRight');
            await page.waitForFunction(el => el.scrollLeft > 0, await wrapper.elementHandle());
            keyboardChecks++;
            break;
          }
        }
      }
      await context.close();
      console.log(`Checked ${pages.length} table pages at ${width}px (${theme}).`);
    }
    console.log(JSON.stringify({ pages: pages.length, keyboardChecks, errors }, null, 2));
    assert(keyboardChecks >= 2, 'Both schedule and legacy archive must support keyboard scrolling');
    assert.equal(errors.length, 0, 'Table readability or scrolling regressions found');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
