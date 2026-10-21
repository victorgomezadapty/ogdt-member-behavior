// Language switch: both languages live in the page (data-l="en" / data-l="es");
// CSS hides the inactive one from <html lang>. Charts listen for "ogdt:lang".
(function () {
  function initial() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'es' || q === 'en') return q;
    try { var s = localStorage.getItem('ogdt-lang'); if (s === 'es' || s === 'en') return s; } catch (e) {}
    return (navigator.language || '').toLowerCase().indexOf('es') === 0 ? 'es' : 'en';
  }
  function apply(lang) {
    document.documentElement.lang = lang;
    try { localStorage.setItem('ogdt-lang', lang); } catch (e) {}
    var t = document.querySelector('meta[name="title-' + lang + '"]');
    if (t) document.title = t.content;
    document.querySelectorAll('[data-set-lang]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.setLang === lang));
    });
    document.dispatchEvent(new CustomEvent('ogdt:lang', { detail: lang }));
  }
  document.documentElement.lang = initial();
  document.documentElement.classList.add('js');
  document.addEventListener('DOMContentLoaded', function () {
    apply(document.documentElement.lang);
    document.addEventListener('click', function (e) {
      var b = e.target.closest('[data-set-lang]');
      if (b) apply(b.dataset.setLang);
    });
  });
})();
