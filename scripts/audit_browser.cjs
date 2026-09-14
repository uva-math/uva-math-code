// Browser-based WCAG regression scan. Manual task testing remains necessary.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const args = process.argv.slice(2);
function option(name, fallback) { const index = args.indexOf(name); return index < 0 ? fallback : args[index + 1]; }
const site = path.resolve(option('--site', '_site'));
const base = option('--url', 'http://127.0.0.1:4173');
const report = option('--report', '/tmp/uva-browser-accessibility.json');
const theme = option('--theme', 'light');
const width = Number(option('--width', 1280));
const workers = Number(option('--workers', 4));
const tags = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

function pagesIn(directory) {
  return fs.readdirSync(directory, {withFileTypes:true}).flatMap(entry => {
    const file = path.join(directory,entry.name);
    if (entry.isDirectory()) return pagesIn(file);
    if (!entry.name.endsWith('.html')) return [];
    const source = fs.readFileSync(file,'utf8');
    return /<html\b/i.test(source) && !/http-equiv=["']refresh/i.test(source) ? [path.relative(site,file)] : [];
  });
}

(async () => {
  const pathsFile = option('--paths', '');
  const pages = pathsFile ? JSON.parse(fs.readFileSync(pathsFile,'utf8')) : pagesIn(site);
  const browser = await chromium.launch({headless:true});
  const context = await browser.newContext({viewport:{width,height:900},colorScheme:theme,reducedMotion:'reduce'});
  await context.addInitScript(value => localStorage.setItem('theme',value),theme);
  // Analytics are not part of the UI and should not record test traffic.
  await context.route(/google-analytics\.com|googletagmanager\.com/, route => route.abort());
  let next = 0;
  let complete = 0;
  const results = [];
  await Promise.all(Array.from({length:workers},async () => {
    const page = await context.newPage();
    while (next < pages.length) {
      const pathname = pages[next++];
      const errors = [];
      const errorHandler = error => errors.push(error.message);
      page.on('pageerror',errorHandler);
      try {
        const url = new URL(pathname.split('/').map(encodeURIComponent).join('/'),base + '/');
        const response = await page.goto(url.href,{waitUntil:'load',timeout:30000});
        if (!response || response.status() >= 400) throw new Error('Page response ' + response?.status());
        await page.evaluate(async () => {
          if (document.fonts) await document.fonts.ready;
          await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        });
        await page.addScriptTag({content:axeSource});
        const audit = await page.evaluate(async tags => {
          const result = await axe.run({runOnly:{type:'tag',values:tags}});
          return {violations:result.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.map(n=>({target:n.target,html:n.html,summary:n.failureSummary}))})),
            overflow:document.documentElement.scrollWidth > innerWidth + 1};
        },tags);
        results.push({path:pathname,...audit,errors});
      } catch(error) { results.push({path:pathname,error:error.message,errors}); }
      page.removeListener('pageerror',errorHandler);
      complete++;
      if (complete % 50 === 0) {
        fs.writeFileSync(report,JSON.stringify({width,theme,pages:results.length,complete:false,results},null,2)+'\n');
        console.log(`${complete}/${pages.length} pages checked`);
      }
    }
    await page.close();
  }));
  await browser.close();
  const failures = results.filter(r=>r.error || r.errors.length || r.violations.length || r.overflow);
  fs.writeFileSync(report,JSON.stringify({width,theme,pages:results.length,failures:failures.length,results},null,2)+'\n');
  console.log(JSON.stringify({pages:results.length,failures:failures.length,report}));
  process.exitCode = failures.length ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode=1; });
