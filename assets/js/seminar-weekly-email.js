(function () {
  'use strict';
  const apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
  const zone = 'America/New_York';
  const root = document.getElementById('weekly-email');
  if (!root) return;
  const calendars = JSON.parse(root.querySelector('.weekly-email-data').textContent);
  const status = root.querySelector('.weekly-email-status');
  const range = root.querySelector('.weekly-email-range');
  const subject = root.querySelector('.weekly-email-subject');
  const preview = root.querySelector('.weekly-email-preview');
  const notes = root.querySelector('.weekly-email-notes');
  const dayMs = 86400000;
  let offset = 0;
  let request = 0;

  function zoneParts(date) {
    const parts = {};
    new Intl.DateTimeFormat('en-US', { timeZone: zone, year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', hourCycle: 'h23', weekday: 'short' })
      .formatToParts(date).forEach(part => { parts[part.type] = part.value; });
    return parts;
  }

  // Midnight in Charlottesville is 04:00 or 05:00 UTC depending on daylight saving time.
  function zoneMidnight(utcDay) {
    for (const hour of [4, 5]) {
      const candidate = new Date(utcDay + hour * 3600000);
      if (Number(zoneParts(candidate).hour) === 0) return candidate;
    }
    return new Date(utcDay + 5 * 3600000);
  }

  // A week is Monday to Sunday; from Friday on, the default is the following week.
  function weekStart(weekOffset) {
    const now = zoneParts(new Date());
    const today = Date.UTC(Number(now.year), Number(now.month) - 1, Number(now.day));
    const weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(now.weekday);
    return today - weekday * dayMs + ((weekday >= 4 ? 1 : 0) + weekOffset) * 7 * dayMs;
  }

  function longDate(utcDay, withYear) {
    const options = { timeZone: 'UTC', month: 'long', day: 'numeric' };
    if (withYear) options.year = 'numeric';
    return new Intl.DateTimeFormat('en-US', options).format(new Date(utcDay));
  }

  function dayKey(date) {
    const parts = zoneParts(date);
    return Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day));
  }

  function plainText(html) {
    const source = document.createElement('template');
    source.innerHTML = html.replace(/<br\s*\/?>/gi, '\n').replace(/<\/(p|div|li)>/gi, '\n\n');
    const paragraphs = [];
    let open = false;
    // Organizers paste abstracts wrapped at about 70 characters. A line break after a
    // long line is that wrapping; after a short line it ends a paragraph.
    source.content.textContent.split('\n').forEach(raw => {
      const text = raw.replace(/\s+/g, ' ').trim();
      if (!text) { open = false; return; }
      if (open) paragraphs[paragraphs.length - 1] += ' ' + text;
      else paragraphs.push(text);
      open = text.length >= 55;
    });
    return paragraphs;
  }

  const texSymbols = {
    alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ϵ', varepsilon: 'ε', zeta: 'ζ', eta: 'η', theta: 'θ', vartheta: 'ϑ',
    iota: 'ι', kappa: 'κ', lambda: 'λ', mu: 'μ', nu: 'ν', xi: 'ξ', pi: 'π', rho: 'ρ', sigma: 'σ', tau: 'τ', upsilon: 'υ',
    phi: 'ϕ', varphi: 'φ', chi: 'χ', psi: 'ψ', omega: 'ω', Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ', Xi: 'Ξ', Pi: 'Π',
    Sigma: 'Σ', Upsilon: 'Υ', Phi: 'Φ', Psi: 'Ψ', Omega: 'Ω',
    ge: '≥', geq: '≥', le: '≤', leq: '≤', ne: '≠', neq: '≠', ll: '≪', gg: '≫', sim: '∼', simeq: '≃', cong: '≅', approx: '≈', equiv: '≡',
    in: '∈', notin: '∉', subset: '⊂', subseteq: '⊆', supset: '⊃', supseteq: '⊇', cup: '∪', cap: '∩', setminus: '∖', emptyset: '∅',
    to: '→', rightarrow: '→', leftarrow: '←', mapsto: '↦', Rightarrow: '⇒', Leftrightarrow: '⇔', iff: '⇔', hookrightarrow: '↪',
    times: '×', cdot: '·', otimes: '⊗', oplus: '⊕', circ: '∘', ast: '∗', star: '⋆', pm: '±', wedge: '∧', vee: '∨',
    infty: '∞', partial: '∂', nabla: '∇', ell: 'ℓ', hbar: 'ℏ', forall: '∀', exists: '∃', langle: '⟨', rangle: '⟩',
    ldots: '…', dots: '…', cdots: '…', mid: '∣', colon: ':', bmod: ' mod ', quad: ' ', qquad: ' ', left: '', right: '',
    log: 'log', exp: 'exp', sin: 'sin', cos: 'cos', dim: 'dim', ker: 'ker', det: 'det', max: 'max', min: 'min', sup: 'sup',
    inf: 'inf', lim: 'lim', deg: 'deg', gcd: 'gcd', Pr: 'Pr', hom: 'hom'
  };
  const texAlphabets = {
    mathbb: { upper: 0x1D538, special: { C: 'ℂ', H: 'ℍ', N: 'ℕ', P: 'ℙ', Q: 'ℚ', R: 'ℝ', Z: 'ℤ' } },
    mathfrak: { upper: 0x1D504, lower: 0x1D51E, special: { C: 'ℭ', H: 'ℌ', I: 'ℑ', R: 'ℜ', Z: 'ℨ' } },
    mathcal: { upper: 0x1D49C, special: { B: 'ℬ', E: 'ℰ', F: 'ℱ', H: 'ℋ', I: 'ℐ', L: 'ℒ', M: 'ℳ', R: 'ℛ' } }
  };
  const texAccents = { tilde: '\u0303', widetilde: '\u0303', hat: '\u0302', widehat: '\u0302', bar: '\u0304', overline: '\u0305', dot: '\u0307', vec: '\u20D7' };
  const texNegations = { '\\equiv': '≢', '\\in': '∉', '=': '≠', '\\subset': '⊄', '\\sim': '≁', '\\cong': '≇', '\\mid': '∤' };

  function texSymbol(match, name) {
    return Object.prototype.hasOwnProperty.call(texSymbols, name) ? texSymbols[name] : match;
  }

  function texCommands(source) {
    let text = source.replace(/\\(mathbb|mathfrak|mathcal)\s*\{([A-Za-z])\}/g, (match, font, letter) => {
      const alphabet = texAlphabets[font];
      if (alphabet.special[letter]) return alphabet.special[letter];
      const base = letter >= 'a' ? alphabet.lower : alphabet.upper;
      return base ? String.fromCodePoint(base + letter.charCodeAt(0) - (letter >= 'a' ? 97 : 65)) : match;
    });
    text = text.replace(/\\(?:mathrm|mathbf|mathit|mathsf|text|textrm|textit|operatorname)\s*\{([^{}\\]*)\}/g, '$1');
    text = text.replace(/\\pmod\s*\{([^{}\\]*)\}/g, ' (mod $1)');
    text = text.replace(/\\not\s*(\\[A-Za-z]+|=)/g, (match, relation) => texNegations[relation] || match);
    text = text.replace(/\\([A-Za-z]+)\s*(?:\{([A-Za-z])\}|([A-Za-z]))(?![A-Za-z])/g, (match, name, braced, bare) => texAccents[name] ? (braced || bare) + texAccents[name] : match);
    text = text.replace(/\\([A-Za-z]+)/g, texSymbol);
    return text.replace(/([\^_])\{([^{}]*)\}/g, (match, mark, body) => Array.from(body).length === 1 ? mark + body : match);
  }

  // Returns null when a formula keeps a command or grouping this table does not
  // cover; the caller then leaves that formula as TeX.
  function texFormula(source) {
    const text = texCommands(source.replace(/\\\{/g, '\u0001').replace(/\\\}/g, '\u0002').replace(/\\([%&_#])/g, '$1').replace(/\\[,;:!]/g, '').replace(/\\ /g, ' '));
    if (/\\/.test(text) || /[{}]/.test(text.replace(/[\^_]\{[^{}]*\}/g, ''))) return null;
    return text.replace(/\u0001/g, '{').replace(/\u0002/g, '}').replace(/\s+/g, ' ').trim();
  }

  // A dollar sign opens a formula only when a non-space follows it, so "$5 and $10" is left alone.
  function texToUnicode(text) {
    const formula = /\$\$([^$]+)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$(?!\s)([^$\n]+?)(?<!\s)\$(?!\d)/g;
    let output = '';
    let last = 0;
    let match;
    while ((match = formula.exec(text))) {
      output += texCommands(text.slice(last, match.index));
      const converted = texFormula(match[1] || match[2] || match[3] || match[4]);
      output += converted === null ? match[0] : converted;
      last = formula.lastIndex;
    }
    return output + texCommands(text.slice(last));
  }

  function nameLike(text) {
    const words = text.trim().split(/\s+/);
    return words.length >= 2 && words.length <= 5 && words.every(word => /^([A-ZÀ-Þ][^\d:]*|de|del|della|di|da|la|le|van|von|der|den)$/.test(word));
  }

  // Organizers put the speaker and the title on one line: "Name (Place) - Title", "Name: Title".
  function splitSummary(summary) {
    const text = (summary || '').replace(/\s+/g, ' ').trim();
    let match = text.match(/^(.+?)\s*(\([^()]*\))\s*[-–—:]\s*(.+)$/);
    if (match && nameLike(match[1])) return { speaker: match[1].trim() + ' ' + match[2], title: match[3] };
    match = text.match(/^(.+?)\s*(\([^()]*\))$/);
    if (match && nameLike(match[1])) return { speaker: match[1].trim() + ' ' + match[2], title: '' };
    match = text.match(/^(.+?)\s+[-–—]\s+(.+)$/) || text.match(/^([^:]+):\s+(.+)$/);
    if (match && nameLike(match[1])) return { speaker: match[1].trim(), title: match[2] };
    return { raw: text };
  }

  function line(parent, text, bold) {
    const paragraph = document.createElement('p');
    if (bold) {
      const strong = document.createElement('strong');
      strong.textContent = text;
      paragraph.appendChild(strong);
    } else paragraph.textContent = text;
    parent.appendChild(paragraph);
    return paragraph;
  }

  function renderEvent(parent, item) {
    const event = item.event;
    const time = event.start.dateTime
      ? new Intl.DateTimeFormat('en-US', { timeZone: zone, hour: 'numeric', minute: '2-digit' }).format(new Date(event.start.dateTime))
      : 'All day';
    line(parent, time + ' – ' + item.calendar.name, true);
    line(parent, '📍 ' + ((event.location || '').replace(/\s+/g, ' ').trim() || 'TBA'));
    const parts = splitSummary(event.summary);
    if (parts.raw !== undefined) line(parent, texToUnicode(parts.raw) || 'TBA');
    else {
      line(parent, 'Speaker: ' + parts.speaker);
      line(parent, 'Title: ' + (texToUnicode(parts.title) || 'TBA'));
    }
    const abstract = plainText(event.description || '').map(text => texToUnicode(text.replace(/^abstract\s*:\s*/i, ''))).filter(Boolean);
    if (abstract.length) abstract[0] = 'Abstract: ' + abstract[0];
    abstract.forEach(text => line(parent, text));
    line(parent, '\u00a0');
  }

  async function load() {
    const current = ++request;
    const monday = weekStart(offset);
    const friday = monday + 4 * dayMs;
    const from = zoneMidnight(monday);
    const to = zoneMidnight(monday + 7 * dayMs);
    range.textContent = 'Week of ' + longDate(monday) + ' – ' + longDate(friday, true);
    subject.value = 'Mathematics Seminars and Colloquia ' + longDate(monday) + ' – ' + longDate(friday, true);
    status.textContent = 'Loading calendars...';
    preview.textContent = '';
    notes.textContent = '';

    const responses = await Promise.allSettled(calendars.map(async calendar => {
      const params = new URLSearchParams({
        key: apiKey, singleEvents: 'true', orderBy: 'startTime', timeZone: zone,
        timeMin: from.toISOString(), timeMax: to.toISOString(), maxResults: '100'
      });
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch('https://www.googleapis.com/calendar/v3/calendars/' + encodeURIComponent(calendar.id) + '/events?' + params, { signal: controller.signal });
        if (!response.ok) throw new Error('Calendar unavailable');
        const body = await response.json();
        return (body.items || []).filter(event => event.start && event.status !== 'cancelled').map(event => ({ event, calendar }));
      } finally { clearTimeout(timeout); }
    }));
    if (current !== request) return;

    const startOf = item => item.event.start.dateTime ? new Date(item.event.start.dateTime) : new Date(item.event.start.date + 'T12:00:00Z');
    const dayOf = item => item.event.start.dateTime ? dayKey(new Date(item.event.start.dateTime)) : Date.parse(item.event.start.date + 'T00:00:00Z');
    const events = responses.flatMap(result => result.status === 'fulfilled' ? result.value : [])
      .filter(item => dayOf(item) >= monday && dayOf(item) < monday + 7 * dayMs);
    events.sort((a, b) => dayOf(a) - dayOf(b) || !!a.event.start.dateTime - !!b.event.start.dateTime || startOf(a) - startOf(b));

    line(preview, 'Hello All,');
    line(preview, 'The seminar and colloquium list for the week ending ' + longDate(friday, true) + ' is below. If you have any additions or corrections, please email me and I will send out an updated version.');
    const pointer = line(preview, 'You can refer to the ');
    const link = document.createElement('a');
    link.href = root.dataset.calendarUrl;
    link.textContent = 'calendar';
    pointer.appendChild(link);
    pointer.appendChild(document.createTextNode(' for all upcoming talks.'));
    let lastDay = null;
    events.forEach(item => {
      if (dayOf(item) !== lastDay) {
        lastDay = dayOf(item);
        preview.appendChild(document.createElement('hr'));
        line(preview, '🗓 ' + new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', weekday: 'long', month: 'long', day: 'numeric' }).format(new Date(lastDay)), true);
      }
      renderEvent(preview, item);
    });
    if (!events.length) line(preview, 'No events are on the seminar calendars for this week.');

    const listed = new Set(events.map(item => item.calendar.id));
    const failed = calendars.filter((calendar, index) => responses[index].status === 'rejected').map(calendar => calendar.name);
    const empty = calendars.filter((calendar, index) => responses[index].status === 'fulfilled' && !listed.has(calendar.id) && !calendar.occasional).map(calendar => calendar.name);
    const noRoom = events.filter(item => !(item.event.location || '').trim()).map(item => item.calendar.name);
    const add = (label, names) => { if (names.length) line(notes, label + ': ' + Array.from(new Set(names)).join(', ') + '.'); };
    add('Calendars that did not load (their events are missing; reload the page)', failed);
    add('No room in the calendar entry', noRoom);
    add('No calendar entry this week', empty);
    status.textContent = events.length + (events.length === 1 ? ' event' : ' events') + ' from ' + (calendars.length - failed.length) + ' of ' + calendars.length + ' calendars.';
  }

  async function copy(button, text, html) {
    const report = message => { root.querySelector('.weekly-email-copied').textContent = message; };
    try {
      if (html && window.ClipboardItem) {
        await navigator.clipboard.write([new ClipboardItem({
          'text/html': new Blob([html], { type: 'text/html' }),
          'text/plain': new Blob([text], { type: 'text/plain' })
        })]);
      } else await navigator.clipboard.writeText(text);
      report(button.textContent.trim() + ': done.');
    } catch (_) {
      report('Copying failed. Select the text and copy it by hand.');
    }
  }

  function start() { load().catch(() => { status.textContent = 'The calendars could not be loaded. Reload the page.'; }); }
  root.querySelector('.weekly-email-previous').addEventListener('click', () => { offset -= 1; start(); });
  root.querySelector('.weekly-email-next').addEventListener('click', () => { offset += 1; start(); });
  root.querySelector('.weekly-email-copy-subject').addEventListener('click', event => copy(event.currentTarget, subject.value));
  root.querySelector('.weekly-email-copy-list').addEventListener('click', event => {
    const text = Array.from(preview.children).map(node => node.tagName === 'HR' ? '________________________________' : node.textContent).join('\n');
    const html = '<div style="font-family: Aptos, Calibri, Arial, sans-serif; font-size: 11pt; color: #000000;">' +
      preview.innerHTML.replace(/<p>/g, '<p style="margin: 0;">') + '</div>';
    copy(event.currentTarget, text, html);
  });
  start();
})();
