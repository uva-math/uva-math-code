(function () {
  'use strict';
  let scheduled = false;
  const helpId = 'code-scroll-help';
  const observed = new WeakSet();
  const sizes = typeof ResizeObserver === 'function' ? new ResizeObserver(schedule) : null;

  function update() {
    scheduled = false;
    document.querySelectorAll('main pre').forEach(element => {
      // Grid columns can settle after the window resize event. Observe the final boxes.
      if (sizes && !observed.has(element)) { sizes.observe(element); observed.add(element); }
      const scrolls = /auto|scroll/.test(getComputedStyle(element).overflowX) &&
        element.scrollWidth > element.clientWidth + 1;
      if (scrolls && !element.hasAttribute('tabindex')) {
        element.setAttribute('tabindex', '0');
        element.dataset.codeScroll = 'true';
        const descriptions = (element.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
        if (!descriptions.includes(helpId)) descriptions.push(helpId);
        element.setAttribute('aria-describedby', descriptions.join(' '));
      } else if (!scrolls && element.dataset.codeScroll) {
        element.removeAttribute('tabindex');
        delete element.dataset.codeScroll;
        const descriptions = (element.getAttribute('aria-describedby') || '').split(/\s+/).filter(id => id && id !== helpId);
        if (descriptions.length) element.setAttribute('aria-describedby', descriptions.join(' '));
        else element.removeAttribute('aria-describedby');
      }
    });
  }

  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
  }

  function initialize() {
    const main = document.querySelector('main');
    if (!main) return;
    const help = document.createElement('p');
    help.id = helpId;
    help.className = 'visually-hidden';
    help.textContent = 'This code example extends beyond the visible area. Use the left and right arrow keys to scroll.';
    main.append(help);
    new MutationObserver(schedule).observe(main, {childList: true, subtree: true});
    if (document.fonts) document.fonts.ready.then(schedule);
    schedule();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
  window.addEventListener('resize', schedule);
  window.addEventListener('load', schedule);
})();
