(function () {
  'use strict';
  const carousel = document.querySelector('.swiper-container');
  if (!carousel || typeof Swiper !== 'function') return;
  const pause = carousel.querySelector('.carousel-pause');
  const status = carousel.querySelector('.carousel-status');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const slides = Array.from(carousel.querySelectorAll('.swiper-slide'));
  let announce = false;
  const swiper = new Swiper(carousel, {
    spaceBetween: 30,
    centeredSlides: true,
    loop: false,
    autoHeight: true,
    speed: motion.matches ? 0 : 300,
    autoplay: motion.matches ? false : { delay: 6500, disableOnInteraction: true },
    pagination: {
      el: carousel.querySelector('.swiper-pagination'),
      clickable: true,
      renderBullet: function (index, className) {
        return '<button type="button" class="' + className + '" aria-label="Go to news slide ' + (index + 1) + '"></button>';
      }
    },
    // Native buttons supply keyboard interaction. Global arrow or wheel
    // listeners would interfere with reading and scrolling the page.
    keyboard: { enabled: false },
    mousewheel: { enabled: false },
    a11y: { enabled: false }
  });

  function syncSlides() {
    slides.forEach((slide, index) => {
      const active = index === swiper.activeIndex;
      slide.inert = !active;
      slide.setAttribute('aria-hidden', String(!active));
      slide.setAttribute('aria-label', (index + 1) + ' of ' + slides.length);
      // Also support browsers without the inert property.
      slide.querySelectorAll('a, button, input, select, textarea, summary, [tabindex]').forEach(element => {
        if (!active) {
          if (!element.hasAttribute('data-carousel-tabindex')) element.setAttribute('data-carousel-tabindex', element.getAttribute('tabindex') || '');
          element.setAttribute('tabindex', '-1');
        } else if (element.hasAttribute('data-carousel-tabindex')) {
          const original = element.getAttribute('data-carousel-tabindex');
          if (original) element.setAttribute('tabindex', original);
          else element.removeAttribute('tabindex');
          element.removeAttribute('data-carousel-tabindex');
        }
      });
    });
    carousel.querySelectorAll('.swiper-pagination-bullet').forEach((bullet, index) => {
      if (index === swiper.activeIndex) bullet.setAttribute('aria-current', 'true');
      else bullet.removeAttribute('aria-current');
    });
    if (announce) {
      const heading = slides[swiper.activeIndex]?.querySelector('h2');
      status.textContent = 'Slide ' + (swiper.activeIndex + 1) + ' of ' + slides.length + ': ' + (heading?.textContent || '');
    }
  }
  function syncRotation() {
    const running = swiper.autoplay.running;
    pause.setAttribute('aria-label', running ? 'Pause automatic slide rotation' : 'Start automatic slide rotation');
    pause.querySelector('i').className = running ? 'fas fa-pause' : 'fas fa-play';
    announce = !running;
  }
  function stopRotation() { swiper.autoplay.stop(); syncRotation(); }
  // Wrap manual navigation without duplicating slide content in the DOM.
  carousel.querySelector('.carousel-prev').addEventListener('click', () => {
    stopRotation();
    swiper.slideTo((swiper.activeIndex + slides.length - 1) % slides.length);
  });
  carousel.querySelector('.carousel-next').addEventListener('click', () => {
    stopRotation();
    swiper.slideTo((swiper.activeIndex + 1) % slides.length);
  });
  carousel.addEventListener('mouseenter', stopRotation);
  carousel.addEventListener('focusin', stopRotation);
  carousel.addEventListener('pointerdown', event => {
    if (!pause.contains(event.target)) stopRotation();
  });
  pause.addEventListener('click', () => {
    if (swiper.autoplay.running) stopRotation();
    else {
      // Starting rotation is always an explicit user action after focus/hover.
      swiper.params.autoplay = { delay: 6500, disableOnInteraction: true };
      swiper.autoplay.start();
      syncRotation();
    }
  });
  swiper.on('autoplayStop', syncRotation);
  swiper.on('autoplayStart', syncRotation);
  swiper.on('slideChange', syncSlides);
  if (motion.addEventListener) motion.addEventListener('change', event => {
    swiper.params.speed = event.matches ? 0 : 300;
    if (event.matches) stopRotation();
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopRotation(); });
  if (slides.length < 2) {
    stopRotation();
    carousel.querySelector('.carousel-controls-bar').hidden = true;
  }
  syncSlides();
  syncRotation();
})();
