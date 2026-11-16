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
  const copyButtons = [root.querySelector('.weekly-email-copy-subject'), root.querySelector('.weekly-email-copy-list')];
  const copied = root.querySelector('.weekly-email-copied');
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
  function weekStart() {
    const now = zoneParts(new Date());
    const today = Date.UTC(Number(now.year), Number(now.month) - 1, Number(now.day));
    const weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(now.weekday);
    return today - weekday * dayMs + (weekday >= 4 ? 7 * dayMs : 0);
  }
  const firstMonday = weekStart();

  function longDate(utcDay, withYear) {
    const options = { timeZone: 'UTC', month: 'long', day: 'numeric' };
    if (withYear) options.year = 'numeric';
    return new Intl.DateTimeFormat('en-US', options).format(new Date(utcDay));
  }

  function dayKey(date) {
    const parts = zoneParts(date);
    return Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day));
  }

  const descriptionTag = /<\/?(?:p|div|br|span|a|b|i|u|em|strong|ul|ol|li|sub|sup|blockquote|h[1-6]|html-blob)(?:\s+[a-z-]+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'<>]+))*\s*\/?>/gi;

  // Most descriptions are plain text, where "p<q" is mathematics: only a
  // well-formed tag from the list above is read as markup.
  function plainText(description) {
    const tags = [];
    const html = description
      .replace(/<(script|style|title|textarea|noscript|iframe|object)\b[\s\S]*?<\/\1\s*>/gi, '')
      .replace(descriptionTag, tag => { tags.push(tag); return '\u0000'; })
      .replace(/</g, '&lt;')
      .replace(/\u0000/g, () => tags.shift());
    const source = document.createElement('template');
    source.innerHTML = html.replace(/<br\s*\/?>/gi, '\n').replace(/<li\b[^>]*>/gi, '\n- ').replace(/<\/(p|div|li|ul|ol|blockquote|h[1-6])>/gi, '\n\n');
    source.content.querySelectorAll('a[href]').forEach(anchor => {
      const href = anchor.getAttribute('href');
      if (/^(https?:|mailto:)/i.test(href) && !anchor.textContent.includes(href.replace(/^mailto:/i, ''))) anchor.append(' (' + href + ')');
    });
    const lines = source.content.textContent.split('\n').map(raw => raw.replace(/\s+/g, ' ').trim());
    // Some organizers paste abstracts hard-wrapped at about 70 characters. Only
    // then is a line break joined, and only where the text was wrapped: the
    // sentence runs on, or the next word would not have fitted on the line.
    const filled = lines.filter(Boolean);
    const inBand = filled.filter(text => text.length >= 55 && text.length <= 100);
    const wrapped = inBand.length >= 3 && inBand.length * 3 >= filled.length;
    const width = Math.max(0, ...inBand.map(text => text.length));
    const joined = [];
    let open = false;
    lines.forEach((text, index) => {
      if (!text) { open = false; return; }
      if (open && !/^(\[\d+\]|\d+[.)]\s|[-*•]\s|[A-Z][A-Za-z ]{0,20}:(\s|$))/.test(text)) joined[joined.length - 1] += ' ' + text;
      else joined.push(text);
      const next = (lines[index + 1] || '').split(' ')[0];
      open = wrapped && !/(\$\$|\\\])$/.test(text) && (text.length + 1 + next.length > width || !/[.!?:;]["')\]”’]*$/.test(text));
    });
    // Formulas are converted after the joining, so that one broken across
    // wrapped lines, or set on lines of its own, is seen whole.
    const paragraphs = texToUnicode(joined.join('\n')).split('\n').map(text => text.trim()).filter(Boolean);
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
    ldots: '…', dots: '…', cdots: '⋯', mid: '∣', colon: ':', bmod: 'mod', quad: ' ', qquad: ' ',
    left: '', right: '', big: '', Big: '', bigl: '', bigr: '', Bigl: '', Bigr: '',
    log: 'log', exp: 'exp', sin: 'sin', cos: 'cos', tan: 'tan', dim: 'dim', ker: 'ker', det: 'det', max: 'max', min: 'min',
    sup: 'sup', inf: 'inf', lim: 'lim', deg: 'deg', gcd: 'gcd', arg: 'arg', Pr: 'Pr', hom: 'hom'
  };
  const texSpaced = new Set(['ge', 'geq', 'le', 'leq', 'ne', 'neq', 'll', 'gg', 'sim', 'simeq', 'cong', 'approx', 'equiv', 'in', 'notin',
    'subset', 'subseteq', 'supset', 'supseteq', 'cup', 'cap', 'setminus', 'to', 'rightarrow', 'leftarrow', 'mapsto', 'Rightarrow',
    'Leftrightarrow', 'iff', 'hookrightarrow', 'times', 'cdot', 'otimes', 'oplus', 'mid', 'bmod']);
  const texOperators = new Set(['log', 'exp', 'sin', 'cos', 'tan', 'dim', 'ker', 'det', 'max', 'min', 'sup', 'inf', 'lim', 'deg', 'gcd', 'arg', 'Pr', 'hom']);
  const texAlphabets = {
    mathbb: { upper: 0x1D538, special: { C: 'ℂ', H: 'ℍ', N: 'ℕ', P: 'ℙ', Q: 'ℚ', R: 'ℝ', Z: 'ℤ' } },
    mathfrak: { upper: 0x1D504, lower: 0x1D51E, special: { C: 'ℭ', H: 'ℌ', I: 'ℑ', R: 'ℜ', Z: 'ℨ' } },
    mathcal: { upper: 0x1D49C, special: { B: 'ℬ', E: 'ℰ', F: 'ℱ', H: 'ℋ', I: 'ℐ', L: 'ℒ', M: 'ℳ', R: 'ℛ' } }
  };
  const texAccents = { tilde: '\u0303', widetilde: '\u0303', hat: '\u0302', widehat: '\u0302', bar: '\u0304', overline: '\u0305', dot: '\u0307', vec: '\u20D7' };
  const texNegations = {
    '=': '≠', '\\equiv': '≢', '\\in': '∉', '\\subset': '⊄', '\\subseteq': '⊈', '\\sim': '≁', '\\simeq': '≄', '\\cong': '≇', '\\approx': '≉',
    '\\mid': '∤', '\\le': '≰', '\\leq': '≰', '\\ge': '≱', '\\geq': '≱', '\\exists': '∄'
  };
  const texToken = /\\(mathbb|mathfrak|mathcal)\s*\{([A-Za-z])\}|\\(?:mathrm|mathbf|mathit|mathsf|text|textrm|textit|operatorname)\s*\{([^{}\\]*)\}|\\pmod\s*\{([^{}\\]*)\}|\\not\s*(\\[A-Za-z]+|=)|\\(?:left|right)\s*\.|\\(tilde|widetilde|hat|widehat|bar|overline|dot|vec)(?![A-Za-z])\s*(?:\{([A-Za-z])\}|([A-Za-z])(?![A-Za-z]))|\\([A-Za-z]+)|\\([,;:! ])/g;

  // Every command is resolved in one pass over the source, so the output of one
  // command can never join the next letter into a different command name. A
  // command this table does not cover is returned as it is, backslash included.
  function texCommands(source) {
    const text = source.replace(texToken, (match, font, letter, words, modulus, negated, accent, braced, bare, name, spacing, offset) => {
      const before = source[offset - 1] || '';
      const after = source[offset + match.length] || '';
      let output = '';
      if (font) {
        const alphabet = texAlphabets[font];
        const base = letter >= 'a' ? alphabet.lower : alphabet.upper;
        if (alphabet.special[letter]) output = alphabet.special[letter];
        else if (base) output = String.fromCodePoint(base + letter.charCodeAt(0) - (letter >= 'a' ? 97 : 65));
        else return match;
      } else if (words !== undefined) output = (/[A-Za-z0-9]/.test(before) ? ' ' : '') + words;
      else if (modulus !== undefined) output = ' (mod ' + modulus + ')';
      else if (negated) {
        if (!texNegations[negated]) return match;
        output = ' ' + texNegations[negated] + ' ';
      } else if (accent) output = (braced || bare) + texAccents[accent];
      else if (spacing) output = spacing === '!' ? '' : ' ';
      else if (name !== undefined) {
        if (!Object.prototype.hasOwnProperty.call(texSymbols, name)) return match;
        if (texSpaced.has(name)) output = ' ' + texSymbols[name] + ' ';
        else if (texOperators.has(name)) output = (/[A-Za-z0-9}]/.test(before) ? ' ' : '') + name + (/[A-Za-z0-9\\]/.test(after) ? ' ' : '');
        else output = texSymbols[name];
      }
      return /[\^_]/.test(before) && /[A-Za-z\\]/.test(after) ? '{' + output.trim() + '}' : output;
    });
    return text.replace(/([\^_])\{([^{}]*)\}(?![\p{L}\p{N}])/gu, (match, mark, group) => Array.from(group).length === 1 ? mark + group : match);
  }

  // Superscripts and subscripts travel through the text as private-use marks
  // (start of a superscript, start of a subscript, end) and become <sup> and
  // <sub> elements when a line is drawn.
  const scriptMarks = /[\uE000-\uE002]/g;

  function texScripts(text) {
    let previous;
    do {
      previous = text;
      text = text.replace(/([\^_])(?:\{([^{}]*)\}|([^\s{}^_\uE000-\uE002]\p{M}*))/gu, (match, mark, group, single) =>
        (mark === '^' ? '\uE000' : '\uE001') + (group !== undefined ? group : single) + '\uE002');
    } while (text !== previous);
    return text;
  }

  // Returns null when a formula keeps a command or grouping the table does not
  // cover; the caller then leaves that formula as TeX.
  function texFormula(source) {
    const text = texCommands(source.replace(/\\\{/g, '\u0001').replace(/\\\}/g, '\u0002').replace(/\\([%&#$])/g, '$1'));
    if (/\\/.test(text) || /[{}]/.test(text.replace(/[\^_]\{[^{}]*\}/g, ''))) return null;
    return texScripts(text.replace(/\s+/g, ' ').replace(/([(\[]) /g, '$1').replace(/ ([)\],.;])/g, '$1').trim()).replace(/\u0001/g, '{').replace(/\u0002/g, '}');
  }

  const textAccents = { "'": '\u0301', '"': '\u0308', '`': '\u0300', '^': '\u0302', '~': '\u0303', H: '\u030B', v: '\u030C', c: '\u0327', u: '\u0306' };

  // Text outside formulas. Accents in names ("G\'alvez", "Erd\H{o}s") and TeX
  // dashes ("Sato--Tate") are always converted. Commands typed without dollar
  // signs ("n \geq 6") are converted sentence by sentence, and only where every
  // command in the sentence is covered and the line holds no stray dollar sign.
  function texProse(chunk) {
    return chunk.split('\n').map(source => {
      const line = source
        .replace(/\{\\(['"`^~])\{?([A-Za-z])\}?\}|\\(['"`^~])\{([A-Za-z])\}|\\(['"`^~])([A-Za-z])/g, (match, a, x, b, y, c, z) => (x || y || z) + textAccents[a || b || c])
        .replace(/\{\\([Hvcu])\{([A-Za-z])\}\}|\\([Hvcu])\{([A-Za-z])\}/g, (match, a, x, b, y) => (x || y) + textAccents[a || b])
        .normalize('NFC')
        .replace(/([\p{L}\p{N}])---(?=[\p{L}\p{N}])/gu, '$1—')
        .replace(/([\p{L}\p{N}])--(?=[\p{L}\p{N}])/gu, '$1–');
      if (line.includes('$')) return line;
      // Without a command in sight, only a short word such as "GL_1" or "L^2" is read as an index.
      if (!line.includes('\\')) return line.replace(/(^|[\s(\["“])([A-Za-z]{1,3}[\^_](?:\{[^{}\s]+\}|[A-Za-z0-9]))(?![A-Za-z0-9_^{])/g, (match, lead, word) => lead + texScripts(word));
      return (line.match(/[^.!?]+(?:[.!?]+["')\]”’]*\s*|$)|[.!?]+\s*/g) || [line]).map(sentence => {
        const converted = texCommands(sentence);
        if (converted.includes('\\')) return sentence;
        return converted.replace(/ {2,}/g, ' ').replace(/ ([,.;])/g, '$1').replace(/\S+/g, word => /:\/\/|@|www\./.test(word) ? word : texScripts(word));
      }).join('');
    }).join('\n');
  }

  const texDelimited = /\$\$([^$]+)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\\begin\{([a-z]+\*?)\}([\s\S]+?)\\end\{\4\}|\$([^$\n]+)\$/g;

  function texToUnicode(source) {
    const text = source.replace(scriptMarks, '');
    let output = '';
    let last = 0;
    let match;
    texDelimited.lastIndex = 0;
    while ((match = texDelimited.exec(text))) {
      const [whole, display, bracket, parenthesis, , environment, inline] = match;
      const body = display || bracket || parenthesis || environment || inline;
      const mathematical = /[\\^_=<>+]/.test(body);
      // "$5 and $10", "$HOME/$USER", "\[1\]" and "\(joint with A. B.\)" are prose, not formulas.
      if (inline !== undefined && !mathematical && (/^\s|\s$/.test(inline) || /^\d/.test(text[texDelimited.lastIndex] || '') || /^\d.*\s/.test(inline) || /^[A-Z_]{3,}\W*$/.test(inline))) {
        texDelimited.lastIndex = match.index + whole.length - 1;
        continue;
      }
      if (bracket !== undefined && /^[\d,\s-]+$/.test(bracket)) continue;
      if (parenthesis !== undefined && !mathematical && /\s\S+\s/.test(parenthesis.trim())) continue;
      const converted = texFormula(body);
      output += texProse(text.slice(last, match.index)) + (converted === null ? whole.replace(/\s+/g, ' ') : converted);
      last = texDelimited.lastIndex;
    }
    return output + texProse(text.slice(last));
  }

  const notNames = /^(seminar|colloquium|defense|talk|meeting|break|theory|lectures?|workshop|conference|panel|party|night|exam|session|club|program|introduction|organizational|learning|thesis|phd|problems?|special|joint|event|social|picnic|lunch|reception|minicourse|holiday|cancell?ed|postponed|tba|tbd|mathematics)$/i;

  function nameLike(text) {
    const words = text.trim().split(/\s+/);
    return words.length >= 2 && words.length <= 5 && words.every(word =>
      /^([A-ZÀ-Þ][^\d:]*|de|del|della|di|da|la|le|van|von|der|den)$/.test(word) && !notNames.test(word) && !/^[A-Z]{3,}$/.test(word));
  }

  function placeLike(parenthesis) {
    return !/^\((part|no|zoom|online|virtual|cancel|postponed|tba|tbd|joint|continued|\d)/i.test(parenthesis);
  }

  // Organizers put the speaker and the title on one line: "Name (Place) - Title", "Name: Title".
  // A line that does not clearly start with a person's name is printed as it is.
  function splitSummary(summary) {
    const text = (summary || '').replace(/\s+/g, ' ').trim();
    let match = text.match(/^(.+?)\s*(\([^()]*\))\s*[-–—:]\s*(.+)$/);
    if (match && nameLike(match[1]) && placeLike(match[2])) return { speaker: match[1].trim() + ' ' + match[2], title: match[3] };
    match = text.match(/^(.+?)\s*(\([^()]*\))$/);
    if (match && nameLike(match[1]) && placeLike(match[2])) return { speaker: match[1].trim() + ' ' + match[2], title: '' };
    match = text.match(/^(.+?)\s+[-–—]\s+(.+)$/) || text.match(/^([^:]+):\s+(.+)$/);
    if (match && nameLike(match[1])) return { speaker: match[1].trim(), title: match[2] };
    return { raw: text };
  }

  function appendMarked(parent, text) {
    const open = [parent];
    text.split(/([\uE000-\uE002])/).forEach(piece => {
      if (piece === '\uE000' || piece === '\uE001') {
        const element = document.createElement(piece === '\uE000' ? 'sup' : 'sub');
        open[open.length - 1].appendChild(element);
        open.push(element);
      } else if (piece === '\uE002') {
        if (open.length > 1) open.pop();
      } else if (piece) open[open.length - 1].appendChild(document.createTextNode(piece));
    });
  }

  function line(parent, text, bold) {
    const paragraph = document.createElement('p');
    appendMarked(bold ? paragraph.appendChild(document.createElement('strong')) : paragraph, text);
    parent.appendChild(paragraph);
    return paragraph;
  }

  // The plain-text copy writes a superscript as ^ and a subscript as _, and a link with its address.
  function plain(node) {
    if (node.nodeType === Node.TEXT_NODE) return node.textContent;
    const inner = Array.from(node.childNodes).map(plain).join('');
    if (node.tagName === 'SUP' || node.tagName === 'SUB') return (node.tagName === 'SUP' ? '^' : '_') + (Array.from(inner).length === 1 ? inner : '{' + inner + '}');
    return node.tagName === 'A' ? inner + ' (' + node.href + ')' : inner;
  }

  function renderEvent(parent, item) {
    const event = item.event;
    let time = 'All day';
    if (event.start.dateTime) time = new Intl.DateTimeFormat('en-US', { timeZone: zone, hour: 'numeric', minute: '2-digit' }).format(new Date(event.start.dateTime));
    else if (event.end && event.end.date) {
      const first = Date.parse(event.start.date + 'T00:00:00Z');
      // Google Calendar all-day event end dates are exclusive.
      const last = Date.parse(event.end.date + 'T00:00:00Z') - dayMs;
      if (last > first) time = longDate(first) + ' to ' + longDate(last);
    }
    const room = '📍 ' + ((event.location || '').replace(/\s+/g, ' ').trim() || 'TBA');
    const summary = texToUnicode((event.summary || '').replace(/\s+/g, ' ').trim());
    const parts = splitSummary(summary);
    // The one-off calendar has no seminar name of its own: the entry names the event.
    if (item.calendar.oneOff) {
      line(parent, time + ' – ' + (summary || 'TBA'), true);
      line(parent, room);
    } else {
      line(parent, time + ' – ' + item.calendar.name, true);
      line(parent, room);
      if (parts.raw !== undefined) line(parent, parts.raw || 'TBA');
      else {
        line(parent, 'Speaker: ' + parts.speaker);
        line(parent, 'Title: ' + (parts.title || 'TBA'));
      }
    }
    const paragraphs = plainText(event.description || '');
    const labelFrom = Math.max(paragraphs.findIndex(text => /^abstract\s*:/i.test(text)), 0);
    let labelled = false;
    paragraphs.forEach((text, index) => {
      const body = text.replace(/^abstract\s*:\s*/i, '');
      if (!body) return;
      line(parent, (!labelled && index >= labelFrom ? 'Abstract: ' : '') + body);
      labelled = labelled || index >= labelFrom;
    });
    line(parent, '\u00a0');
  }

  async function load() {
    const current = ++request;
    const monday = firstMonday + offset * 7 * dayMs;
    const friday = monday + 4 * dayMs;
    const from = zoneMidnight(monday);
    const to = zoneMidnight(monday + 7 * dayMs);
    range.textContent = 'Week of ' + longDate(monday) + ' – ' + longDate(friday, true);
    subject.value = '';
    status.textContent = 'Loading calendars...';
    preview.textContent = '';
    notes.textContent = '';
    copied.textContent = '';
    copyButtons.forEach(button => { button.disabled = true; });

    const responses = await Promise.allSettled(calendars.map(async calendar => {
      const items = [];
      let pageToken = '';
      do {
        const params = new URLSearchParams({
          key: apiKey, singleEvents: 'true', orderBy: 'startTime', timeZone: zone,
          timeMin: from.toISOString(), timeMax: to.toISOString(), maxResults: '250'
        });
        if (pageToken) params.set('pageToken', pageToken);
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        try {
          const response = await fetch('https://www.googleapis.com/calendar/v3/calendars/' + encodeURIComponent(calendar.id) + '/events?' + params, { signal: controller.signal });
          if (!response.ok) throw new Error('Calendar unavailable');
          const body = await response.json();
          items.push(...(body.items || []));
          pageToken = body.nextPageToken || '';
        } finally { clearTimeout(timeout); }
      } while (pageToken);
      return items.filter(event => event.start && event.status !== 'cancelled').map(event => ({ event, calendar }));
    }));
    if (current !== request) return;

    const timed = item => !!item.event.start.dateTime;
    const startOf = item => timed(item) ? new Date(item.event.start.dateTime) : new Date(item.event.start.date + 'T12:00:00Z');
    // An all-day event that began before Monday and is still running is listed under Monday.
    const dayOf = item => timed(item) ? dayKey(new Date(item.event.start.dateTime)) : Math.max(Date.parse(item.event.start.date + 'T00:00:00Z'), monday);
    const lastDayOf = item => !timed(item) && item.event.end && item.event.end.date ? Date.parse(item.event.end.date + 'T00:00:00Z') - dayMs : dayOf(item);
    const events = responses.flatMap(result => result.status === 'fulfilled' ? result.value : [])
      .filter(item => dayOf(item) < monday + 7 * dayMs && (timed(item) ? dayOf(item) >= monday : lastDayOf(item) >= monday));
    events.sort((a, b) => dayOf(a) - dayOf(b) || timed(a) - timed(b) || startOf(a) - startOf(b));
    const failed = calendars.filter((calendar, index) => responses[index].status === 'rejected').map(calendar => calendar.name);

    // The email says Monday to Friday unless something is listed on the weekend.
    const lastListed = events.length ? Math.max(friday, dayOf(events[events.length - 1])) : friday;
    range.textContent = 'Week of ' + longDate(monday) + ' – ' + longDate(lastListed, true);
    subject.value = 'Mathematics Seminars and Colloquia ' + longDate(monday) + ' – ' + longDate(lastListed, true);

    if (failed.length) line(preview, 'NOT LOADED, EVENTS MISSING: ' + failed.join(', ') + '. Reload the page.', true);
    line(preview, 'Hello All,');
    line(preview, 'The seminar and colloquium list for the week ending ' + longDate(lastListed, true) + ' is below. If you have any additions or corrections, please email me and I will send out an updated version.');
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
    if (!events.length && !failed.length) line(preview, 'No events are on the seminar calendars for this week.');

    const listed = new Set(events.map(item => item.calendar.id));
    const empty = calendars.filter((calendar, index) => responses[index].status === 'fulfilled' && !listed.has(calendar.id) && !calendar.occasional).map(calendar => calendar.name);
    const noRoom = events.filter(item => !(item.event.location || '').trim()).map(item => item.calendar.name);
    const add = (label, names) => names.length ? line(notes, label + ': ' + Array.from(new Set(names)).join(', ') + '.') : null;
    const warning = add('These calendars did not load, so their events are missing from the list below. Reload the page', failed);
    if (warning) {
      warning.className = 'alert alert-danger';
      warning.setAttribute('role', 'alert');
    }
    add('No room in the calendar entry', noRoom);
    add('No calendar entry this week', empty);
    status.textContent = events.length + (events.length === 1 ? ' event' : ' events') + ' from ' + (calendars.length - failed.length) + ' of ' + calendars.length + ' calendars.';
    copyButtons.forEach(button => { button.disabled = false; });
  }

  async function copy(button, text, html) {
    const report = message => { copied.textContent = message; };
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
  copyButtons[0].addEventListener('click', event => copy(event.currentTarget, subject.value));
  copyButtons[1].addEventListener('click', event => {
    const text = Array.from(preview.children).map(node => node.tagName === 'HR' ? '________________________________' : plain(node)).join('\n');
    const html = '<div style="font-family: Aptos, Calibri, Arial, sans-serif; font-size: 11pt; color: #000000;">' +
      preview.innerHTML.replace(/<p>/g, '<p style="margin: 0;">') + '</div>';
    copy(event.currentTarget, text, html);
  });
  start();
})();
