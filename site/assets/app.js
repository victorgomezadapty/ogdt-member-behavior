// Charts and the membership card. Data: window.OGDT_DATA (aggregates only).
(function () {
  'use strict';
  var D = window.OGDT_DATA;
  var NS = 'http://www.w3.org/2000/svg';
  var lang = function () { return document.documentElement.lang === 'es' ? 'es' : 'en'; };
  var T = {
    en: {
      visits: 'visits', months: 'member-months', ofMonths: 'of eligible months', windows: 'windows',
      noVisit: 'no recorded visit', monthOfRun: 'Month of consecutive eligible run', run: 'Month',
      zeroShare: 'months with no visit', meanVisits: 'mean visits', n: 'member-months',
      down: 'Fewer visits', same: 'Same', up: 'More visits', pairs: 'adjacent month pairs',
      club: 'Club', monthsWith: function (k) { return k === 1 ? '1 month with a visit' : k + ' months with a visit'; },
      stages: ['All source calendar rows', 'Inside documented club span', 'Source review flags accepted', 'Regular contract months'],
      members: 'members', rows: 'rows', period: 'Month', perMonth: 'mean visits / month', plus: '+',
      cols: { visits: 'Visits in month', months: 'Member-months', share: 'Share', month: 'Run month', zero: 'No-visit share', mean: 'Mean visits', windows: 'Windows', k: 'Months with a visit' }
    },
    es: {
      visits: 'visitas', months: 'meses-socio', ofMonths: 'de los meses elegibles', windows: 'ventanas',
      noVisit: 'ninguna visita registrada', monthOfRun: 'Mes de la racha elegible consecutiva', run: 'Mes',
      zeroShare: 'meses sin visita', meanVisits: 'media de visitas', n: 'meses-socio',
      down: 'Menos visitas', same: 'Igual', up: 'Más visitas', pairs: 'pares de meses contiguos',
      club: 'Club', monthsWith: function (k) { return k === 1 ? '1 mes con visita' : k + ' meses con visita'; },
      stages: ['Todas las filas del calendario', 'Dentro del periodo documentado', 'Banderas de origen aceptadas', 'Meses de contrato regular'],
      members: 'socios', rows: 'filas', period: 'Mes', perMonth: 'media de visitas / mes', plus: '+',
      cols: { visits: 'Visitas en el mes', months: 'Meses-socio', share: 'Proporción', month: 'Mes de racha', zero: 'Proporción sin visita', mean: 'Media de visitas', windows: 'Ventanas', k: 'Meses con visita' }
    }
  };
  var t = function () { return T[lang()]; };
  var locale = function () { return lang() === 'es' ? 'es-ES' : 'en-US'; };
  var fmt = function (n, d) { return Number(n).toLocaleString(locale(), { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0, useGrouping: 'always' }); };
  var pct = function (x, d) { return fmt(x * 100, d === undefined ? 1 : d) + ' %'; };
  var pctEn = function (x, d) { return lang() === 'es' ? pct(x, d) : fmt(x * 100, d === undefined ? 1 : d) + '%'; };

  function el(tag, attrs, parent) {
    var node = document.createElementNS(NS, tag);
    for (var k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function text(parent, x, y, str, cls, anchor) {
    var node = el('text', { x: x, y: y, class: 'lbl ' + (cls || ''), 'text-anchor': anchor || 'start' }, parent);
    node.textContent = str;
    return node;
  }
  // Bar with 4px rounded data-end, square at the baseline.
  function barPath(x, y, w, h, r) {
    r = Math.min(r, w / 2, h);
    return 'M' + x + ',' + (y + h) + 'V' + (y + r) + 'Q' + x + ',' + y + ' ' + (x + r) + ',' + y +
      'H' + (x + w - r) + 'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) + 'V' + (y + h) + 'Z';
  }
  function hbarPath(x, y, w, h, r) {
    r = Math.min(r, h / 2, w);
    return 'M' + x + ',' + y + 'H' + (x + w - r) + 'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) +
      'V' + (y + h - r) + 'Q' + (x + w) + ',' + (y + h) + ' ' + (x + w - r) + ',' + (y + h) + 'H' + x + 'Z';
  }
  function frame(id, height) {
    var host = document.getElementById(id);
    host.innerHTML = '';
    var width = Math.max(280, Math.round(host.clientWidth || 600));
    var svg = el('svg', { viewBox: '0 0 ' + width + ' ' + height, width: width, height: height }, host);
    return { svg: svg, w: width, h: height, host: host };
  }
  function ticks(max, count) {
    var raw = max / count, mag = Math.pow(10, Math.floor(Math.log10(raw))), step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; }).find(function (s) { return s >= raw; });
    var out = []; for (var v = 0; v <= max + 1e-9; v += step) out.push(+v.toFixed(6)); return out;
  }

  // Tooltip
  var tip = document.getElementById('tooltip');
  function showTip(evt, html) {
    tip.innerHTML = html; tip.hidden = false;
    var x = evt.clientX + 14, y = evt.clientY + 14, r = tip.getBoundingClientRect();
    if (x + r.width > innerWidth - 8) x = evt.clientX - r.width - 14;
    if (y + r.height > innerHeight - 8) y = evt.clientY - r.height - 14;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { tip.hidden = true; }

  // Membership card: 100 cells, empty share rounded from the real zero fraction.
  function card() {
    var host = document.getElementById('punches');
    var empty = Math.round(D.headline.zero_recorded_fraction * 100);
    // Seeded shuffle: the same irregular layout on every visit, without stripes.
    var order = [], seed = 20061, emptySet = {};
    for (var i = 0; i < 100; i++) order.push(i);
    for (var s = 99; s > 0; s--) {
      seed = (seed * 1103515245 + 12345) % 2147483648;
      var r = seed % (s + 1), tmp = order[s]; order[s] = order[r]; order[r] = tmp;
    }
    order.slice(0, empty).forEach(function (pos) { emptySet[pos] = true; });
    host.innerHTML = '';
    for (var j = 0; j < 100; j++) {
      var p = document.createElement('span');
      p.className = 'punch' + (emptySet[j] ? ' empty' : '');
      host.appendChild(p);
    }
    var cells = host.children;
    var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window)) { for (var k = 0; k < cells.length; k++) cells[k].classList.add('on'); return; }
    var io = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      io.disconnect();
      Array.prototype.forEach.call(cells, function (c, idx) { setTimeout(function () { c.classList.add('on'); }, 120 + idx * 14); });
    }, { threshold: .3 });
    io.observe(host);
  }

  function statNumbers() {
    document.querySelectorAll('[data-fmt]').forEach(function (n) { n.textContent = fmt(D.headline[n.dataset.fmt]); });
    document.querySelectorAll('.stat b.mono:not([data-fmt])').forEach(function (n) {
      n.innerHTML = fmt(D.headline.median_attendance_per_eligible_month) + ' <small>/ ' + fmt(D.headline.mean_attendance_per_eligible_month, 1) + '</small>';
    });
  }

  // 01 Histogram
  function hist() {
    var bins = D.histogram.bins, total = bins.reduce(function (s, b) { return s + b.months; }, 0);
    var f = frame('chart-hist', 300), m = { l: 58, r: 12, t: 30, b: 40 };
    var iw = f.w - m.l - m.r, ih = f.h - m.t - m.b, max = 28000, gap = 2;
    var bw = iw / bins.length;
    var y = function (v) { return m.t + ih - (v / max) * ih; };
    var g = el('g', { class: 'axis' }, f.svg);
    ticks(max, 4).forEach(function (v) {
      el('line', { x1: m.l, x2: f.w - m.r, y1: y(v), y2: y(v), class: 'gridline' }, g);
      text(g, m.l - 8, y(v) + 4, fmt(v), '', 'end');
    });
    bins.forEach(function (b, i) {
      var x = m.l + i * bw + gap / 2, h = ih * b.months / max;
      var isZero = b.visits === 0;
      el('path', { d: barPath(x, y(b.months), bw - gap, h, 4), fill: isZero ? 'var(--accent)' : 'var(--ink-2)', opacity: isZero ? 1 : .78 }, f.svg);
      var label = b.visits === D.histogram.cap ? b.visits + t().plus : String(b.visits);
      if (bw > 22 || i % 2 === 0 || b.visits === D.histogram.cap) text(f.svg, x + (bw - gap) / 2, f.h - m.b + 16, label, '', 'middle');
      var hit = el('rect', { x: m.l + i * bw, y: m.t, width: bw, height: ih, class: 'hit' }, f.svg);
      hit.addEventListener('pointermove', function (e) {
        showTip(e, '<b>' + label + '</b> ' + t().visits + '<br><b>' + fmt(b.months) + '</b> ' + t().months + ' · ' + pctEn(b.months / total));
      });
      hit.addEventListener('pointerleave', hideTip);
    });
    var z = bins[0];
    text(f.svg, m.l + bw + 6, y(z.months) + 10, fmt(z.months) + ' · ' + pctEn(z.months / total), 'strong big');
    text(f.svg, m.l + bw + 6, y(z.months) + 26, t().noVisit, '');
    text(f.svg, m.l + iw / 2, f.h - 4, t().cols.visits, '', 'middle');
    table('hist', [t().cols.visits, t().cols.months, t().cols.share], bins.map(function (b) {
      return [b.visits === D.histogram.cap ? b.visits + t().plus : b.visits, fmt(b.months), pctEn(b.months / total)];
    }));
  }

  // 02 Three-month windows, 100% stacked bar (ordinal ramp)
  function windows() {
    var rows = D.windows3, total = rows.reduce(function (s, r) { return s + r.windows; }, 0);
    var host = document.getElementById('chart-windows'), narrow = (host.clientWidth || 600) < 520;
    // Narrow screens: labels become a list under the bar so they cannot collide.
    var f = frame('chart-windows', narrow ? 60 + rows.length * 24 : 190), m = { l: 4, r: 4 }, iw = f.w - m.l - m.r, gap = 2, top = narrow ? 4 : 70, bh = 44;
    var x = m.l;
    rows.forEach(function (r, i) {
      var w = iw * r.windows / total - (i < rows.length - 1 ? gap : 0);
      var seg = el('rect', { x: x, y: top, width: Math.max(w, 1), height: bh, rx: i === 0 || i === rows.length - 1 ? 4 : 0, fill: 'var(--ord-' + r.positive_months + ')' }, f.svg);
      var share = r.windows / total, cx = x + w / 2, above = i % 2 === 0;
      var name = r.positive_months === 0 ? (lang() === 'es' ? 'ninguno' : 'none') : t().monthsWith(r.positive_months);
      if (narrow) {
        var ry = top + bh + 22 + i * 24;
        el('rect', { x: m.l, y: ry - 11, width: 12, height: 12, rx: 3, fill: 'var(--ord-' + r.positive_months + ')' }, f.svg);
        text(f.svg, m.l + 20, ry, name, '');
        text(f.svg, f.w - m.r, ry, pctEn(share), 'strong', 'end');
      } else {
        var ly = above ? top - 30 : top + bh + 22;
        el('line', { x1: cx, x2: cx, y1: above ? ly + 8 : top + bh, y2: above ? top : ly - 14, stroke: 'var(--line)' }, f.svg);
        text(f.svg, cx, ly, pctEn(share), r.positive_months === 0 ? 'strong big' : 'strong', 'middle');
        text(f.svg, cx, ly + 15, name, '', 'middle');
      }
      seg.addEventListener('pointermove', function (e) { showTip(e, '<b>' + t().monthsWith(r.positive_months) + '</b><br>' + fmt(r.windows) + ' ' + t().windows + ' · ' + pctEn(share)); });
      seg.addEventListener('pointerleave', hideTip);
      x += w + gap;
    });
    table('windows', [t().cols.k, t().cols.windows, t().cols.share], rows.map(function (r) { return [r.positive_months, fmt(r.windows), pctEn(r.windows / total)]; }));
  }

  // 03 Line chart with crosshair (single series: title names it, no legend)
  function line(id, rows, key, max, format, color) {
    var f = frame(id, 250), m = { l: 46, r: 16, t: 16, b: 42 };
    var iw = f.w - m.l - m.r, ih = f.h - m.t - m.b, n = rows.length;
    var x = function (i) { return m.l + (i / (n - 1)) * iw; };
    var y = function (v) { return m.t + ih - (v / max) * ih; };
    var g = el('g', { class: 'axis' }, f.svg);
    ticks(max, 4).forEach(function (v) {
      el('line', { x1: m.l, x2: f.w - m.r, y1: y(v), y2: y(v), class: 'gridline' }, g);
      text(g, m.l - 8, y(v) + 4, format(v, 0), '', 'end');
    });
    [1, 6, 12, 18, 24].forEach(function (mo) { text(g, x(mo - 1), f.h - m.b + 16, String(mo), '', 'middle'); });
    text(g, m.l + iw / 2, f.h - 4, t().monthOfRun, '', 'middle');
    el('line', { x1: x(11), x2: x(11), y1: m.t, y2: m.t + ih, stroke: 'var(--line)', 'stroke-dasharray': '3 3' }, f.svg);
    text(f.svg, x(11) + 4, m.t + ih - 6, lang() === 'es' ? '1 año' : '1 year', '');
    el('path', { d: rows.map(function (r, i) { return (i ? 'L' : 'M') + x(i) + ',' + y(r[key]); }).join(''), fill: 'none', stroke: color, 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, f.svg);
    [0, 10].forEach(function (i) {
      var cy = y(rows[i][key]);
      // Put the label on the side the line is not heading to, so it never sits on the stroke.
      var below = i === 0 && y(rows[1][key]) < cy;
      el('circle', { cx: x(i), cy: cy, r: 4, fill: color, stroke: 'var(--surface)', 'stroke-width': 2 }, f.svg);
      text(f.svg, x(i) + (i ? 0 : 8), below ? cy + 18 : cy - 10, format(rows[i][key], 1), 'strong', i ? 'middle' : 'start');
    });
    var cross = el('line', { y1: m.t, y2: m.t + ih, stroke: 'var(--muted)', 'stroke-width': 1, visibility: 'hidden' }, f.svg);
    var dot = el('circle', { r: 5, fill: color, stroke: 'var(--surface)', 'stroke-width': 2, visibility: 'hidden' }, f.svg);
    var hit = el('rect', { x: m.l, y: m.t, width: iw, height: ih, class: 'hit' }, f.svg);
    hit.addEventListener('pointermove', function (e) {
      var box = f.svg.getBoundingClientRect(), px = (e.clientX - box.left) * (f.w / box.width);
      var i = Math.max(0, Math.min(n - 1, Math.round(((px - m.l) / iw) * (n - 1)))), r = rows[i];
      cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i)); cross.setAttribute('visibility', 'visible');
      dot.setAttribute('cx', x(i)); dot.setAttribute('cy', y(r[key])); dot.setAttribute('visibility', 'visible');
      showTip(e, t().run + ' <b>' + r.month + '</b><br>' + t().zeroShare + ': <b>' + pctEn(r.zero) + '</b><br>' + t().meanVisits + ': <b>' + fmt(r.mean, 2) + '</b><br>n = ' + fmt(r.n));
    });
    hit.addEventListener('pointerleave', function () { hideTip(); cross.setAttribute('visibility', 'hidden'); dot.setAttribute('visibility', 'hidden'); });
  }
  function streak() {
    line('chart-zero', D.streak, 'zero', .4, function (v, d) { return pctEn(v, d); }, 'var(--accent)');
    line('chart-mean', D.streak, 'mean', 6, function (v, d) { return fmt(v, d); }, 'var(--ink)');
    table('streak', [t().cols.month, t().cols.months, t().cols.zero, t().cols.mean], D.streak.map(function (r) { return [r.month, fmt(r.n), pctEn(r.zero), fmt(r.mean, 2)]; }));
  }

  // 04 Month-to-month change: diverging single bar
  function change() {
    var c = D.changes, total = c.down + c.same + c.up;
    var f = frame('chart-change', 150), m = { l: 4, r: 4 }, iw = f.w - m.l - m.r, top = 54, bh = 40, gap = 2, x = m.l;
    [['down', c.down], ['same', c.same], ['up', c.up]].forEach(function (p, i) {
      var w = iw * p[1] / total - (i < 2 ? gap : 0), share = p[1] / total;
      var seg = el('rect', { x: x, y: top, width: w, height: bh, rx: i !== 1 ? 4 : 0, fill: 'var(--' + p[0] + ')' }, f.svg);
      text(f.svg, i === 0 ? x : (i === 2 ? x + w : x + w / 2), top - 24, pctEn(share), 'strong big', i === 0 ? 'start' : i === 2 ? 'end' : 'middle');
      text(f.svg, i === 0 ? x : (i === 2 ? x + w : x + w / 2), top - 9, t()[p[0]], '', i === 0 ? 'start' : i === 2 ? 'end' : 'middle');
      text(f.svg, i === 0 ? x : (i === 2 ? x + w : x + w / 2), top + bh + 20, fmt(p[1]), '', i === 0 ? 'start' : i === 2 ? 'end' : 'middle');
      seg.addEventListener('pointermove', function (e) { showTip(e, '<b>' + t()[p[0]] + '</b><br>' + fmt(p[1]) + ' / ' + fmt(total) + ' ' + t().pairs); });
      seg.addEventListener('pointerleave', hideTip);
      x += w + gap;
    });
  }

  // 05 Clubs over time: one axis, direct labels + legend, crosshair across clubs
  function clubs() {
    var ids = Object.keys(D.clubs).sort(), colors = ['var(--series-1)', 'var(--series-2)', 'var(--series-3)'];
    var periods = Array.from(new Set([].concat.apply([], ids.map(function (k) { return D.clubs[k].map(function (r) { return r.period; }); })))).sort();
    var f = frame('chart-clubs', 300), m = { l: 40, r: 70, t: 14, b: 34 };
    var iw = f.w - m.l - m.r, ih = f.h - m.t - m.b, min = 3, max = 7;
    var x = function (p) { return m.l + (periods.indexOf(p) / (periods.length - 1)) * iw; };
    var y = function (v) { return m.t + ih - ((v - min) / (max - min)) * ih; };
    var g = el('g', { class: 'axis' }, f.svg);
    [3, 4, 5, 6, 7].forEach(function (v) { el('line', { x1: m.l, x2: m.l + iw, y1: y(v), y2: y(v), class: 'gridline' }, g); text(g, m.l - 8, y(v) + 4, String(v), '', 'end'); });
    periods.forEach(function (p) { if (p.slice(5) === '01') text(g, x(p), f.h - m.b + 16, p.slice(0, 4), '', 'middle'); });
    var legend = document.getElementById('legend-clubs');
    legend.innerHTML = ids.map(function (k, i) { return '<span><i style="background:' + colors[i] + '"></i>' + t().club + ' ' + k + '</span>'; }).join('');
    var ends = [];
    ids.forEach(function (k, i) {
      var rows = D.clubs[k];
      el('path', { d: rows.map(function (r, j) { return (j ? 'L' : 'M') + x(r.period) + ',' + y(r.mean); }).join(''), fill: 'none', stroke: colors[i], 'stroke-width': 2, 'stroke-linejoin': 'round' }, f.svg);
      var last = rows[rows.length - 1];
      ends.push({ k: k, x: x(last.period), y: y(last.mean), color: colors[i] });
    });
    // Direct labels at line ends, nudged apart so they never collide.
    ends.sort(function (a, b) { return a.y - b.y; });
    for (var e = 1; e < ends.length; e++) if (ends[e].y - ends[e - 1].y < 14) ends[e].y = ends[e - 1].y + 14;
    ends.forEach(function (d) {
      el('circle', { cx: d.x, cy: d.y, r: 3.5, fill: d.color, stroke: 'var(--surface)', 'stroke-width': 2 }, f.svg);
      text(f.svg, d.x + 8, d.y + 4, t().club + ' ' + d.k, 'strong');
    });
    var cross = el('line', { y1: m.t, y2: m.t + ih, stroke: 'var(--muted)', visibility: 'hidden' }, f.svg);
    var hit = el('rect', { x: m.l, y: m.t, width: iw, height: ih, class: 'hit' }, f.svg);
    hit.addEventListener('pointermove', function (ev) {
      var box = f.svg.getBoundingClientRect(), px = (ev.clientX - box.left) * (f.w / box.width);
      var i = Math.max(0, Math.min(periods.length - 1, Math.round(((px - m.l) / iw) * (periods.length - 1)))), p = periods[i];
      cross.setAttribute('x1', x(p)); cross.setAttribute('x2', x(p)); cross.setAttribute('visibility', 'visible');
      var html = '<b>' + p + '</b>';
      ids.forEach(function (k) { var r = D.clubs[k].find(function (q) { return q.period === p; }); if (r) html += '<br>' + t().club + ' ' + k + ': <b>' + fmt(r.mean, 2) + '</b> (n=' + fmt(r.n) + ')'; });
      showTip(ev, html);
    });
    hit.addEventListener('pointerleave', function () { hideTip(); cross.setAttribute('visibility', 'hidden'); });
    var trows = [];
    periods.forEach(function (p) { trows.push([p].concat(ids.map(function (k) { var r = D.clubs[k].find(function (q) { return q.period === p; }); return r ? fmt(r.mean, 2) + ' (' + fmt(r.n) + ')' : '–'; }))); });
    table('clubs', [t().period].concat(ids.map(function (k) { return t().club + ' ' + k; })), trows);
  }

  // 06 Selection funnel
  function funnel() {
    var rows = D.funnel, max = rows[0].rows;
    // Labels sit above each bar, so they never depend on the bar's width.
    var step = 78, f = frame('chart-funnel', rows.length * step), iw = f.w;
    rows.forEach(function (r, i) {
      var y = i * step + 40, w = Math.max(6, iw * r.rows / max), last = i === rows.length - 1;
      text(f.svg, 0, y - 24, t().stages[i], 'strong');
      text(f.svg, 0, y - 8, fmt(r.rows) + ' ' + t().rows + ' · ' + fmt(r.members) + ' ' + t().members, '');
      el('path', { d: hbarPath(0, y, w, 20, 4), fill: last ? 'var(--accent)' : 'var(--ink-2)', opacity: last ? 1 : .55 + i * .1 }, f.svg);
    });
  }

  function table(name, head, rows) {
    var host = document.querySelector('[data-table="' + name + '"]');
    if (!host) return;
    host.innerHTML = '<div class="scroll"><table><thead><tr>' + head.map(function (h) { return '<th scope="col">' + h + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }

  function renderAll() { statNumbers(); hist(); windows(); streak(); change(); clubs(); funnel(); }
  document.addEventListener('DOMContentLoaded', function () {
    card();
    renderAll();
    document.addEventListener('ogdt:lang', renderAll);
    var last = innerWidth, timer;
    addEventListener('resize', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { if (innerWidth !== last) { last = innerWidth; renderAll(); } }, 150);
    });
    if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', renderAll);
  });
})();
