#!/usr/bin/env node
'use strict';

// The website keeps native MathML. Only this temporary print DOM uses SVG
// equations because Chromium's PDF export does not preserve MathML semantics.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {parseArgs} = require('node:util');
const {chromium} = require('playwright');
const sre = require('speech-rule-engine');
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {MathML} = require('mathjax-full/js/input/mathml.js');
const {SVG} = require('mathjax-full/js/output/svg.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');

const {values: args} = parseArgs({options: {
  url: {type: 'string'}, output: {type: 'string'},
  'public-base': {type: 'string', default: 'https://math.virginia.edu'},
  python: {type: 'string', default: process.env.PDF_PYTHON ||
    (fs.existsSync(path.join(__dirname, '.venv/bin/python')) ? path.join(__dirname, '.venv/bin/python') : 'python3')},
  verapdf: {type: 'string', default: process.env.VERAPDF || 'verapdf'},
  landscape: {type: 'boolean', default: false},
  'keep-work': {type: 'boolean', default: false}
}});
if (!args.url || !args.output) {
  console.error('Usage: node export_pdf.cjs --url URL_OR_FILE_URL --output PATH [--landscape] [--python PYTHON]');
  process.exit(2);
}
const output = path.resolve(args.output);
const work = fs.mkdtempSync(path.join(os.tmpdir(), 'uva-pdf-'));
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const mathDocument = mathjax.document('', {
  InputJax: new MathML(), OutputJax: new SVG({fontCache: 'none'})
});
function run(command, argv) {
  const result = spawnSync(command, argv, {encoding: 'utf8', maxBuffer: 50 * 1024 * 1024});
  if (result.error) throw result.error;
  return result;
}
function ensureSuccess(result, description) {
  if (result.status !== 0) throw Error(`${description}: ${result.stderr || result.stdout}`);
}

(async () => {
  await sre.setupEngine({locale: 'en', domain: 'mathspeak', style: 'default'});
  await sre.engineReady();
  const browser = await chromium.launch({headless: true});
  let metadata;
  try {
    const page = await browser.newPage({viewport: args.landscape ? {width: 1056, height: 816} : {width: 720, height: 1056}, reducedMotion: 'reduce'});
    await page.route('**/*', route => {
      const host = new URL(route.request().url()).hostname;
      if (/(^|\.)(google-analytics\.com|googletagmanager\.com|analytics\.google\.com|doubleclick\.net)$/.test(host)) return route.abort();
      return route.continue();
    });
    const response = await page.goto(args.url, {waitUntil: 'load', timeout: 60000});
    if (new URL(args.url).protocol !== 'file:' && (!response || response.status() !== 200)) {
      throw Error(`Document request failed: HTTP ${response?.status()}`);
    }
    if (await page.locator('main').count() !== 1) throw Error('Expected exactly one main content element');
    await page.evaluate(async () => {
      document.documentElement.dataset.theme = 'light';
      await document.fonts.ready;
      for (const details of document.querySelectorAll('main details')) details.open = true;
      const main = document.querySelector('main');
      // Chromium otherwise omits blank table cells and some endnote list items
      // from its structure tree. A dash records the absence of a table value.
      for (const cell of main.querySelectorAll('td,th')) {
        if (!cell.textContent.trim() && !cell.querySelector('img,math,input,svg')) cell.textContent = '—';
      }
      for (const item of main.querySelectorAll('li')) item.setAttribute('role', 'listitem');
      // Keep document tables of contents; remove only the surrounding website.
      document.body.querySelectorAll('style, link[rel="stylesheet"]').forEach(style => document.head.append(style));
      document.body.replaceChildren(main);
      main.querySelectorAll('[data-code-scroll], [data-math-scroll]').forEach(el => {
        el.removeAttribute('tabindex'); el.removeAttribute('aria-describedby');
      });
      main.querySelectorAll('#code-scroll-help, #math-scroll-help, .skip-link, .breadcrumb, .pagination').forEach(el => el.remove());
      for (const nav of main.querySelectorAll('nav')) {
        const label = `${nav.id} ${nav.getAttribute('aria-label') || ''}`;
        if (nav.getAttribute('role') !== 'doc-toc' && !/\b(?:toc|contents)\b/i.test(label)) nav.remove();
      }
      // Preserve native list/link semantics in PDF. Chromium maps these DPUB
      // roles to NonStruct; the website keeps their richer HTML semantics.
      main.querySelectorAll('[role="doc-endnotes"],[role="doc-endnote"],[role="doc-noteref"],[role="doc-backlink"]')
        .forEach(element => element.removeAttribute('role'));
    });
    await page.emulateMedia({media: 'print'});
    await page.addStyleTag({content: `
      @media print {
        html, body, main { color: #000 !important; background: #fff !important; color-scheme: light; }
        body { margin: 0 !important; }
        main { width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 !important; }
        main :is(h1,h2,h3,h4,h5,h6) { text-transform: none; break-after: avoid; }
        main :is(p,li) { orphans: 3; widows: 3; }
        main :is(img,svg) { max-width: 100%; }
        main a { color: #000 !important; text-decoration: underline; }
        main :is(pre,code) { white-space: pre-wrap !important; overflow-wrap: anywhere; }
        main :is(.math-block-scroll,.math-inline-scroll,.table-responsive) { overflow: visible !important; max-width: 100% !important; }
        main .math-block-scroll { width: 100% !important; }
        main .math-inline-scroll { display: inline !important; }
        main .prereq-table { min-width: 0 !important; width: 100% !important; font-size: 10pt; }
        main .prereq-table :is(td,th) { padding: 3pt !important; overflow-wrap: anywhere; }
        main button { display: none !important; }
        .pdf-math { break-inside: avoid; }
      }
    `});
    metadata = await page.evaluate(({publicBase}) => {
      const main = document.querySelector('main');
      const sourceOrigin = location.origin;
      const toPublic = value => {
        const url = new URL(value, location.href);
        // Local print documents use public links. Resolve any relative link
        // against the public site, never against a temporary filesystem path.
        if (location.protocol === 'file:' && url.protocol === 'file:') {
          if (value.startsWith('file:')) throw Error('Print document contains a filesystem link');
          return new URL(value, publicBase.replace(/\/$/, '') + '/').href;
        }
        if (['http:', 'https:'].includes(url.protocol) &&
            (url.origin === sourceOrigin || ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) {
          const base = new URL(publicBase); url.protocol = base.protocol; url.host = base.host; url.port = base.port;
        }
        return url.href;
      };
      for (const image of main.querySelectorAll('img')) image.src = image.src;
      const links = [...main.querySelectorAll('a[href]')].map(a => {
        a.href = toPublic(a.getAttribute('href'));
        return {url: a.href, text: (a.getAttribute('aria-label') || a.textContent || a.querySelector('img')?.alt || a.href).trim()};
      });
      const h1 = main.querySelector('h1');
      if (!h1?.textContent.trim()) throw Error('Document has no readable main heading');
      const title = document.title.trim() || h1.textContent.trim();
      return {title, sourceUrl: location.href, publicBase, links};
    }, {publicBase: args['public-base']});

    const formulas = await page.locator('main math').evaluateAll(nodes => nodes.map(node => {
      const copy = node.cloneNode(true);
      // SRE honors aria-label verbatim; derive speech from the actual MathML.
      copy.removeAttribute('aria-label'); copy.removeAttribute('role');
      return {mathml: copy.outerHTML, display: node.getAttribute('display') === 'block' || Boolean(node.closest('.katex-display'))};
    }));
    metadata.formulas = formulas.map(({mathml, display}, index) => {
      const speech = sre.toSpeech(mathml).replace(/\s+/g, ' ').trim();
      if (!speech) throw Error(`Formula ${index + 1} has no speech representation`);
      const container = mathDocument.convert(mathml, {display, em: 16, ex: 8, containerWidth: 720});
      const svg = adaptor.firstChild(container);
      const markup = adaptor.outerHTML(svg);
      if (markup.includes('data-mjx-error')) throw Error(`Formula ${index + 1} failed SVG conversion`);
      return {
        id: `UVA_FORMULA_${String(index + 1).padStart(5, '0')}`,
        speech, mathml, display,
        src: 'data:image/svg+xml;base64,' + Buffer.from(markup).toString('base64'),
        width: adaptor.getAttribute(svg, 'width'), height: adaptor.getAttribute(svg, 'height'),
        style: adaptor.getAttribute(svg, 'style') || ''
      };
    });
    await page.locator('main math').evaluateAll((nodes, formulas) => nodes.forEach((math, index) => {
      const data = formulas[index]; const image = document.createElement('img');
      image.src = data.src; image.alt = `${data.id} ${data.speech}`; image.className = 'pdf-math';
      image.style.cssText = `${data.style}; width:${data.width}; height:${data.height}; max-width:100%; object-fit:contain;`;
      if (data.display) { image.style.display = 'block'; image.style.margin = '0.5em auto'; }
      const target = math.closest('.katex-display') || math.closest('.katex') || math;
      target.replaceWith(image);
    }), metadata.formulas);
    await page.locator('main img').evaluateAll(images => Promise.all(images.map(image => image.decode())));
    metadata.figures = await page.locator('main img:not(.pdf-math)').evaluateAll(images => images
      .filter(image => image.getBoundingClientRect().width > 0 && getComputedStyle(image).visibility !== 'hidden' && image.getAttribute('aria-hidden') !== 'true')
      .map(image => ({alt: image.alt, width: image.naturalWidth, height: image.naturalHeight})));
    await page.pdf({path: path.join(work, 'raw.pdf'), format: 'Letter',
      margin: {top: '.5in', bottom: '.5in', left: '.5in', right: '.5in'},
      landscape: args.landscape, preferCSSPageSize: args.landscape,
      tagged: true, outline: true, printBackground: true});
    metadata.formulas.forEach(formula => delete formula.src);
  } finally {
    await browser.close();
  }
  const metadataPath = path.join(work, 'metadata.json');
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
  const postprocess = run(args.python, [path.join(__dirname, 'tag_pdf.py'),
    '--input', path.join(work, 'raw.pdf'), '--output', path.join(work, 'tagged.pdf'), '--metadata', metadataPath]);
  ensureSuccess(postprocess, 'PDF structure repair failed');
  const validation = run(args.verapdf, ['--flavour', 'ua1', '--format', 'json', path.join(work, 'tagged.pdf')]);
  fs.mkdirSync(path.dirname(output), {recursive: true});
  fs.writeFileSync(output + '.validation.json', validation.stdout);
  let report;
  try { report = JSON.parse(validation.stdout); } catch { throw Error(`veraPDF did not return valid JSON: ${validation.stderr}`); }
  const results = report.report?.jobs?.flatMap(job => job.validationResult || []) || [];
  if (validation.status !== 0 || results.length !== 1 || !results.every(result => result.compliant)) {
    throw Error(`PDF/UA validation failed; report: ${output}.validation.json`);
  }
  // Only a validated candidate can replace the requested destination.
  fs.copyFileSync(path.join(work, 'tagged.pdf'), output + '.pending');
  fs.renameSync(output + '.pending', output);
  const summary = {output, title: metadata.title, formulaCount: metadata.formulas.length,
    figureCount: metadata.figures.length, pdfua1: true, repairs: JSON.parse(postprocess.stdout),
    sourceUrl: metadata.sourceUrl};
  fs.writeFileSync(output + '.export.json', JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary));
  if (!args['keep-work']) fs.rmSync(work, {recursive: true});
})().catch(error => {
  console.error(error.message);
  console.error(`Diagnostic files retained at ${work}`);
  process.exitCode = 1;
});
