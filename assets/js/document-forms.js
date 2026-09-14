(function () {
  'use strict';
  function clearPrintValues() {
    document.querySelectorAll('.document-print-value').forEach(element => element.remove());
    document.querySelectorAll('.document-print-source').forEach(element => element.classList.remove('document-print-source'));
  }
  function preparePrintValues() {
    clearPrintValues();
    document.querySelectorAll('main [role="form"] input:not([type="checkbox"]):not([type="radio"]), main [role="form"] textarea, main [role="form"] select').forEach(control => {
      const value = document.createElement('span');
      value.className = 'document-print-value';
      value.textContent = control.tagName === 'SELECT'
        ? Array.from(control.selectedOptions).map(option => option.textContent).join(', ')
        : control.value;
      control.after(value);
      control.classList.add('document-print-source');
    });
  }
  window.addEventListener('beforeprint', preparePrintValues);
  window.addEventListener('afterprint', clearPrintValues);
})();
