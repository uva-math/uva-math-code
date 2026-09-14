(function () {
  'use strict';
  if (window.uvaSeminarCalendarLoaded) return;
  window.uvaSeminarCalendarLoaded = true;
  const apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
  const zone = 'America/New_York';
  const calendarDay = new Intl.DateTimeFormat('en-US', { timeZone: zone, year: 'numeric', month: 'numeric', day: 'numeric' });

  function safeURL(value) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
      const url = new URL(value, window.location.href);
      return ['https:', 'http:', 'mailto:'].includes(url.protocol) ? url.href : null;
    } catch (_) { return null; }
  }

  // Calendar descriptions are rich text supplied by organizers. Preserve their
  // semantics without importing scripts, presentation styles, or unnamed links.
  function descriptionFragment(html) {
    const source = document.createElement('template');
    source.innerHTML = html;
    const output = document.createDocumentFragment();
    const allowed = new Set(['P', 'DIV', 'BR', 'UL', 'OL', 'LI', 'STRONG', 'EM', 'B', 'I', 'A', 'SUB', 'SUP', 'BLOCKQUOTE']);
    function copy(node, parent) {
      if (node.nodeType === Node.TEXT_NODE) { parent.appendChild(document.createTextNode(node.textContent)); return; }
      if (node.nodeType !== Node.ELEMENT_NODE || ['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT'].includes(node.tagName)) return;
      if (node.tagName === 'IMG') {
        if (node.alt) parent.appendChild(document.createTextNode(node.alt));
        return;
      }
      if (!allowed.has(node.tagName)) { node.childNodes.forEach(child => copy(child, parent)); return; }
      const element = document.createElement(node.tagName.toLowerCase());
      if (node.tagName === 'A') {
        const href = safeURL(node.getAttribute('href'));
        if (href && node.textContent.trim()) element.href = href;
      }
      node.childNodes.forEach(child => copy(child, element));
      parent.appendChild(element);
    }
    source.content.childNodes.forEach(node => copy(node, output));
    return output;
  }

  function renderMath(element) {
    if (typeof window.renderMathInElement !== 'function') return;
    window.renderMathInElement(element, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false }
      ],
      output: 'htmlAndMathml',
      throwOnError: false,
      strict: 'ignore',
      trust: false
    });
  }

  function appendText(parent, tag, text) {
    const element = document.createElement(tag);
    element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function calendarWording(container) {
    const mode = container.dataset.mode;
    const noun = container.dataset.noun || (mode === 'visitors' ? 'visit' : mode === 'awm' ? 'activity' : 'talk');
    const capitalized = noun.charAt(0).toUpperCase() + noun.slice(1);
    return {
      noun,
      plural: noun === 'activity' ? 'activities' : noun + 's',
      title: noun === 'talk' ? 'Seminar talk' : capitalized,
      details: noun === 'talk' ? 'Talk abstract and details' : capitalized + ' details',
      calendar: noun === 'talk' ? 'Seminar calendar' : capitalized + ' calendar'
    };
  }

  function renderEvent(event, calendar, headingLevel, wording) {
    const article = document.createElement('article');
    article.className = 'seminar-event';
    const title = event.summary || wording.title;
    const heading = document.createElement(headingLevel === '2' ? 'h2' : 'h3');
    const href = event.htmlLink && safeURL(event.htmlLink);
    if (href) {
      const link = appendText(heading, 'a', title);
      link.href = href;
    } else heading.textContent = title;
    article.appendChild(heading);

    const dateValue = event.start.dateTime || event.start.date;
    const allDay = !event.start.dateTime;
    const date = new Date(allDay ? dateValue + 'T12:00:00Z' : dateValue);
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: zone };
    if (!allDay) Object.assign(options, { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
    const dateLine = document.createElement('p');
    const time = appendText(dateLine, 'time', new Intl.DateTimeFormat('en-US', options).format(date));
    time.dateTime = dateValue;
    if (event.end && (event.end.dateTime || event.end.date)) {
      const endValue = event.end.dateTime || event.end.date;
      const endDate = new Date(allDay ? endValue + 'T12:00:00Z' : endValue);
      // Google Calendar all-day event end dates are exclusive.
      if (allDay) endDate.setUTCDate(endDate.getUTCDate() - 1);
      if (endDate > date) {
        dateLine.appendChild(document.createTextNode(' – '));
        const endOptions = allDay || calendarDay.format(date) !== calendarDay.format(endDate)
          ? options : { hour: 'numeric', minute: '2-digit', timeZone: zone, timeZoneName: 'short' };
        const endTime = appendText(dateLine, 'time', new Intl.DateTimeFormat('en-US', endOptions).format(endDate));
        endTime.dateTime = allDay ? endDate.toISOString().slice(0, 10) : endValue;
      }
    }
    article.appendChild(dateLine);
    if (calendar.name) {
      const seminar = document.createElement('p');
      if (calendar.url) appendText(seminar, 'a', calendar.name).href = calendar.url;
      else seminar.textContent = calendar.name;
      article.appendChild(seminar);
    }
    if (event.location) appendText(article, 'p', 'Location: ' + event.location);
    if (event.description) {
      const details = document.createElement('details');
      const label = wording.details;
      const summary = appendText(details, 'summary', label);
      summary.setAttribute('aria-label', label + ': ' + title);
      const body = document.createElement('div');
      body.className = 'seminar-abstract';
      body.appendChild(descriptionFragment(event.description));
      details.appendChild(body);
      article.appendChild(details);
    }
    return article;
  }

  async function loadCalendar(container) {
    const wording = calendarWording(container);
    const status = container.querySelector('.seminar-status');
    const eventsElement = container.querySelector('.seminar-events');
    const calendars = JSON.parse(container.querySelector('.seminar-calendar-data').textContent);
    const current = container.dataset.current === 'true';
    const from = current ? new Date() : new Date(container.dataset.from);
    if (current) from.setDate(from.getDate() - Number(container.dataset.daysBack || 0));
    let to = container.dataset.to ? new Date(container.dataset.to) : null;
    if (current && container.dataset.mode === 'all') {
      to = new Date(); to.setDate(to.getDate() + 180);
    } else if (!current && !to) to = new Date();
    const maxEvents = Number(container.dataset.maxEvents) || 50;
    const perCalendar = Number(container.dataset.perCalendar) || maxEvents;
    const responses = await Promise.allSettled(calendars.map(async calendar => {
      const params = new URLSearchParams({
        key: apiKey, singleEvents: 'true', orderBy: 'startTime',
        timeZone: zone, timeMin: from.toISOString(), maxResults: String(perCalendar)
      });
      if (to) params.set('timeMax', to.toISOString());
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch('https://www.googleapis.com/calendar/v3/calendars/' + encodeURIComponent(calendar.id) + '/events?' + params, { signal: controller.signal });
        if (!response.ok) throw new Error('Calendar unavailable');
        const body = await response.json();
        return (body.items || []).filter(event => event.start && event.status !== 'cancelled').map(event => ({ event, calendar }));
      } finally { clearTimeout(timeout); }
    }));
    const events = responses.flatMap(result => result.status === 'fulfilled' ? result.value : []);
    events.sort((a, b) => new Date(a.event.start.dateTime || a.event.start.date) - new Date(b.event.start.dateTime || b.event.start.date));
    if (!current && container.dataset.mode === 'awm') events.reverse();
    const displayed = events.slice(0, maxEvents);
    displayed.forEach(item => eventsElement.appendChild(renderEvent(item.event, item.calendar, container.dataset.headingLevel, wording)));
    if (container.dataset.openDetails === 'true') {
      eventsElement.querySelectorAll('details').forEach(details => { details.open = true; });
    }
    renderMath(eventsElement);
    const failed = responses.filter(result => result.status === 'rejected').length;
    const { noun, plural } = wording;
    status.textContent = displayed.length ? displayed.length + ' ' + (displayed.length === 1 ? noun : plural) + ' listed.' : (failed ? 'The live schedule could not be loaded.' : 'No ' + plural + ' are scheduled in this period.');
    if (failed) {
      status.textContent += displayed.length ? ' Some calendars could not be loaded.' : '';
      const fallback = appendText(container, 'p', 'For the full schedule, use the calendar links below or contact the organizers. ');
      calendars.forEach((calendar, index) => {
        if (index) fallback.appendChild(document.createTextNode(' · '));
        const link = appendText(fallback, 'a', calendar.name || wording.calendar);
        link.href = 'https://calendar.google.com/calendar/embed?mode=AGENDA&ctz=America%2FNew_York&src=' + encodeURIComponent(calendar.id);
      });
    }
  }

  function initialize() {
    document.querySelectorAll('.seminar-calendar').forEach(container => {
      loadCalendar(container).catch(() => {
        container.querySelector('.seminar-status').textContent = 'The schedule could not be loaded. Please contact the organizers for ' + calendarWording(container).noun + ' details.';
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
})();
