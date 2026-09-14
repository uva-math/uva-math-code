(function () {
  'use strict';
  let scheduled = false;
  const observed = new WeakSet();
  const resizeObserver = window.ResizeObserver ? new ResizeObserver(schedule) : null;
  function update() {
    scheduled = false;
    document.querySelectorAll('main math[display="block"]').forEach(element => {
      if (element.closest('.katex-mathml, .math-block-scroll')) return;
      const wrapper = document.createElement('span');
      wrapper.className = 'math-block-scroll';
      element.before(wrapper);
      wrapper.append(element);
    });
    document.querySelectorAll('main math:not([display="block"]), main .katex:not(.katex-display .katex), main mjx-container:not([display="true"])').forEach(element => {
      if (element.closest('.katex-mathml, .math-inline-scroll')) return;
      const container = element.closest('p,li,dd,dt,td,th,main');
      if (!container || !container.clientWidth || Math.max(element.scrollWidth, element.getBoundingClientRect().width) <= container.clientWidth) return;
      const wrapper = document.createElement('span');
      wrapper.className = 'math-inline-scroll';
      element.before(wrapper);
      wrapper.append(element);
    });
    document.querySelectorAll('main .math-inline-scroll, main .math-block-scroll, main .katex-display, main mjx-container[display="true"]').forEach(element => {
      // KaTeX's hidden MathML copy is already contained by its display wrapper.
      if (element.closest('.katex-mathml')) return;
      if (resizeObserver && !observed.has(element)) {
        resizeObserver.observe(element);
        observed.add(element);
      }
      const overflows = element.scrollWidth > element.clientWidth || element.scrollHeight > element.clientHeight;
      if (overflows) {
        if (!element.hasAttribute('tabindex')) {
          element.setAttribute('tabindex', '0');
          element.dataset.mathScroll = 'true';
          const descriptions = (element.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
          if (!descriptions.includes('math-scroll-help')) descriptions.push('math-scroll-help');
          element.setAttribute('aria-describedby', descriptions.join(' '));
        }
      } else if (element.dataset.mathScroll) {
        element.removeAttribute('tabindex');
        delete element.dataset.mathScroll;
        const descriptions = (element.getAttribute('aria-describedby') || '').split(/\s+/).filter(id => id && id !== 'math-scroll-help');
        if (descriptions.length) element.setAttribute('aria-describedby', descriptions.join(' '));
        else element.removeAttribute('aria-describedby');
      }
    });
  }
  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
  }
  document.addEventListener('DOMContentLoaded', () => {
    const main = document.querySelector('main');
    if (!main) return;
    const help = document.createElement('p');
    help.id = 'math-scroll-help';
    help.className = 'visually-hidden';
    help.textContent = 'This equation extends beyond the visible area. Use the left and right arrow keys to scroll.';
    main.append(help);
    new MutationObserver(schedule).observe(main, {childList:true, subtree:true});
    main.addEventListener('toggle', schedule, true);
    if (document.fonts) {
      document.fonts.ready.then(schedule);
      document.fonts.addEventListener('loadingdone', schedule);
    }
    schedule();
  });
  window.addEventListener('resize', schedule);
  window.addEventListener('load', schedule);
})();
