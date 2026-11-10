// Charts and the membership card. Data: window.OGDT_DATA (aggregates only).
(function () {
  'use strict';
  var D = window.OGDT_DATA;
  var NS = 'http://www.w3.org/2000/svg';
  var lang = function () { return document.documentElement.lang === 'es' ? 'es' : 'en'; };
  var T = {
    en: {
      month: 'Month', months: 'months', active: 'still active', ci: '95% interval', users: 'users', dropouts: 'dropouts',
      renew: function (g) { return g === '0' ? 'No renewal' : g === '1' ? '1 renewal' : g + ' renewals'; },
      band: function (g) { return g + ' / week'; }, cls: { 'No classes': 'No classes', 'Attended classes': 'Attended classes' },
      days: 'days', dropGroup: 'Dropouts', actGroup: 'Active users', thisWeek: 'Visits this week', nextWeek: 'Next week', pairs: 'week pairs',
      share: 'share', median: 'Median months', s12: 'Active at 12 months', rawShare: 'Dropout share', group: 'Group', est: 'Estimate',
      metrics: { r_week_to_week: 'Week to next week, r', p_any_next_given_any: 'Visit next week if visited (share)', p_any_next_given_none: 'Visit next week if not (share)',
        r_weeks5_8_to_1_4: 'Weeks 5 to 8 to weeks 1 to 4, r', auc_any_weeks1_4: 'Any visit in weeks 1 to 4, AUC', r_control_past4_to_study: 'Control: before to study, r', r_control_past4_to_after: 'Control: before to after, r' }
    },
    es: {
      month: 'Mes', months: 'meses', active: 'aún activa', ci: 'intervalo del 95 %', users: 'usuarios', dropouts: 'bajas',
      renew: function (g) { return g === '0' ? 'Sin renovación' : g === '1' ? '1 renovación' : g + ' renovaciones'; },
      band: function (g) { return g.replace('.', ',') + ' / semana'; }, cls: { 'No classes': 'Sin clases', 'Attended classes': 'Con clases' },
      days: 'días', dropGroup: 'Bajas', actGroup: 'Activos', thisWeek: 'Visitas esta semana', nextWeek: 'Semana siguiente', pairs: 'pares de semanas',
      share: 'proporción', median: 'Meses (mediana)', s12: 'Activa a 12 meses', rawShare: 'Proporción de bajas', group: 'Grupo', est: 'Estimación',
      metrics: { r_week_to_week: 'Semana a la siguiente, r', p_any_next_given_any: 'Vuelve si vino (proporción)', p_any_next_given_none: 'Vuelve si no vino (proporción)',
        r_weeks5_8_to_1_4: 'Semanas 5 a 8 a semanas 1 a 4, r', auc_any_weeks1_4: 'Alguna visita en semanas 1 a 4, AUC', r_control_past4_to_study: 'Control: antes a estudio, r', r_control_past4_to_after: 'Control: antes a después, r' }
    }
  };
  var t = function () { return T[lang()]; };
  var locale = function () { return lang() === 'es' ? 'es-ES' : 'en-US'; };
  var fmt = function (n, d) { return Number(n).toLocaleString(locale(), { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0, useGrouping: 'always' }); };
  var pct = function (x, d) { var v = fmt(x * 100, d === undefined ? 1 : d); return lang() === 'es' ? v + ' %' : v + '%'; };
  var css = function (v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); };
  var SERIES = ['var(--accent)', 'var(--ink)', 'var(--ink-2)', 'var(--muted)'];
  var DASH = ['', '', '6 4', '2 4'];

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


  // Membership card: 100 cells, empty share = dropout share rounded.
  function card() {
    var host = document.getElementById('punches');
    var empty = Math.round(D.lisboa.dropout_share * 100);
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

  // Shared survival axes: months 0..48 on x, share 0..1 on y.
  function survAxes(id, h) {
    var f = frame(id, h), m = { l: 44, r: 14, t: 12, b: 34 }, iw = f.w - m.l - m.r, ih = h - m.t - m.b;
    var x = function (v) { return m.l + iw * v / 48; }, y = function (v) { return m.t + ih * (1 - v); };
    var g = el('g', { class: 'axis' }, f.svg);
    [0, .25, .5, .75, 1].forEach(function (v) {
      el('line', { x1: m.l, x2: m.l + iw, y1: y(v), y2: y(v), class: 'gridline' }, g);
      text(g, m.l - 8, y(v) + 4, pct(v, 0), '', 'end');
    });
    [0, 6, 12, 18, 24, 30, 36, 42, 48].forEach(function (v) { text(g, x(v), h - 12, fmt(v), '', 'middle'); });
    text(g, m.l + iw, h - 0, t().months, '', 'end');
    return { f: f, x: x, y: y, m: m, iw: iw, ih: ih };
  }
  function stepPath(ax, curve) {
    var d = 'M' + ax.x(0) + ',' + ax.y(curve[0]);
    for (var i = 1; i < curve.length; i++) d += 'H' + ax.x(i) + 'V' + ax.y(curve[i]);
    return d;
  }
  function hover(ax, series) {
    var hit = el('rect', { x: ax.m.l, y: ax.m.t, width: ax.iw, height: ax.ih, class: 'hit', fill: 'transparent' }, ax.f.svg);
    var guide = el('line', { y1: ax.m.t, y2: ax.m.t + ax.ih, stroke: 'var(--muted)', 'stroke-dasharray': '3 3', opacity: 0 }, ax.f.svg);
    hit.addEventListener('mousemove', function (e) {
      var r = ax.f.svg.getBoundingClientRect(), mx = (e.clientX - r.left) * ax.f.w / r.width;
      var mo = Math.max(0, Math.min(48, Math.round((mx - ax.m.l) / ax.iw * 48)));
      guide.setAttribute('x1', ax.x(mo)); guide.setAttribute('x2', ax.x(mo)); guide.setAttribute('opacity', 1);
      showTip(e, '<b>' + t().month + ' ' + mo + '</b><br>' + series.map(function (s) { return s.name + ': ' + pct(s.curve[mo]); }).join('<br>'));
    });
    hit.addEventListener('mouseleave', function () { hideTip(); guide.setAttribute('opacity', 0); });
  }
  function legend(id, items) {
    var host = document.getElementById(id); if (!host) return;
    host.innerHTML = items.map(function (s, i) { var st = DASH[i] ? 'background:none;border-top:3px ' + (DASH[i] === '6 4' ? 'dashed' : 'dotted') + ' ' + SERIES[i] + ';height:0' : 'background:' + SERIES[i];
      return '<span><i style="' + st + '"></i>' + s + '</span>'; }).join('');
  }

  function km() {
    var L = D.lisboa, ax = survAxes('chart-km', 300);
    var band = D.km_band, d = 'M' + ax.x(0) + ',' + ax.y(band[0][2]);
    for (var i = 1; i < band.length; i++) d += 'H' + ax.x(i) + 'V' + ax.y(band[i][2]);
    for (var j = band.length - 1; j >= 1; j--) d += 'V' + ax.y(band[j - 1][1]) + 'H' + ax.x(j - 1);
    el('path', { d: d + 'Z', fill: 'var(--accent-soft)', opacity: .9 }, ax.f.svg);
    el('path', { d: stepPath(ax, L.curve), fill: 'none', stroke: 'var(--accent)', 'stroke-width': 2.5 }, ax.f.svg);
    var med = L.median_months;
    el('line', { x1: ax.x(0), x2: ax.x(med), y1: ax.y(.5), y2: ax.y(.5), stroke: 'var(--ink-2)', 'stroke-dasharray': '4 4' }, ax.f.svg);
    el('line', { x1: ax.x(med), x2: ax.x(med), y1: ax.y(.5), y2: ax.y(0), stroke: 'var(--ink-2)', 'stroke-dasharray': '4 4' }, ax.f.svg);
    text(ax.f.svg, ax.x(med) + 6, ax.y(.5) - 8, (lang() === 'es' ? 'mediana ' : 'median ') + fmt(med, 1) + ' ' + t().months, 'strong');
    hover(ax, [{ name: t().active, curve: L.curve }]);
    table('km', [t().month, t().active, t().ci], L.survival_at.map(function (p) { return [fmt(p.months), pct(p.survival), pct(p.lo) + ' · ' + pct(p.hi)]; }));
  }

  function curves(id, legendId, groups, label, h) {
    var ax = survAxes(id, h || 280);
    groups.forEach(function (g, i) { el('path', { d: stepPath(ax, g.curve), fill: 'none', stroke: SERIES[i], 'stroke-width': 2.3, 'stroke-dasharray': DASH[i] }, ax.f.svg); });
    legend(legendId, groups.map(function (g) { return label(g.group) + ' (' + fmt(g.users) + ')'; }));
    hover(ax, groups.map(function (g) { return { name: label(g.group), curve: g.curve }; }));
  }
  function groupRows(groups, label) {
    return groups.map(function (g) { return [label(g.group), fmt(g.users), fmt(g.dropouts), pct(g.dropout_share), g.median_months === null ? '' : fmt(g.median_months, 1), pct(g.s12.survival) + ' (' + pct(g.s12.lo) + ' · ' + pct(g.s12.hi) + ')']; });
  }
  var groupHead = function () { return [t().group, t().users, t().dropouts, t().rawShare, t().median, t().s12]; };

  function renewals() {
    curves('chart-renewals', 'legend-renewals', D.lisboa.by_renewals, t().renew, 300);
    table('renewals', groupHead(), groupRows(D.lisboa.by_renewals, t().renew));
  }
  function classes() { curves('chart-classes', 'legend-classes', D.lisboa.by_classes, function (g) { return t().cls[g]; }, 300); }

  function bars(id, items, opts) {
    var h = 250, f = frame(id, h), m = { l: 44, r: 10, t: 22, b: 34 }, iw = f.w - m.l - m.r, ih = h - m.t - m.b;
    var y = function (v) { return m.t + ih * (1 - v); }, bw = iw / items.length;
    var g = el('g', { class: 'axis' }, f.svg);
    [0, .25, .5, .75, 1].forEach(function (v) { el('line', { x1: m.l, x2: m.l + iw, y1: y(v), y2: y(v), class: 'gridline' }, g); text(g, m.l - 8, y(v) + 4, pct(v, 0), '', 'end'); });
    items.forEach(function (it, i) {
      var x0 = m.l + i * bw + bw * .2, w = bw * .6;
      el('path', { d: barPath(x0, y(it.v), w, y(0) - y(it.v), 4), fill: opts.color || 'var(--ink-2)' }, f.svg);
      if (it.lo !== undefined) {
        var cx = x0 + w / 2;
        el('line', { x1: cx, x2: cx, y1: y(it.lo), y2: y(it.hi), stroke: 'var(--ink)', 'stroke-width': 1.5 }, f.svg);
        [it.lo, it.hi].forEach(function (v) { el('line', { x1: cx - 5, x2: cx + 5, y1: y(v), y2: y(v), stroke: 'var(--ink)', 'stroke-width': 1.5 }, f.svg); });
      }
      text(f.svg, x0 + w / 2, y(it.hi !== undefined ? it.hi : it.v) - 7, pct(it.v), 'strong', 'middle');
      text(f.svg, x0 + w / 2, h - 12, it.label, '', 'middle');
      var hit = el('rect', { x: m.l + i * bw, y: m.t, width: bw, height: ih, fill: 'transparent', class: 'hit' }, f.svg);
      hit.addEventListener('mousemove', function (e) { showTip(e, it.tip); });
      hit.addEventListener('mouseleave', hideTip);
    });
  }

  function frequency() {
    var G = D.lisboa.by_frequency;
    bars('chart-freq-raw', G.map(function (g) { return { label: t().band(g.group), v: g.dropout_share, tip: '<b>' + t().band(g.group) + '</b><br>' + fmt(g.dropouts) + ' / ' + fmt(g.users) + ' ' + t().users }; }), { color: 'var(--accent)' });
    bars('chart-freq-km', G.map(function (g) { return { label: t().band(g.group), v: g.s12.survival, lo: g.s12.lo, hi: g.s12.hi, tip: '<b>' + t().band(g.group) + '</b><br>' + pct(g.s12.survival) + ' (' + pct(g.s12.lo) + ' · ' + pct(g.s12.hi) + ')' }; }), { color: 'var(--ink-2)' });
    table('freq', groupHead(), groupRows(G, t().band));
  }

  function recency() {
    var B = D.lisboa.recency.bands, nd = 0, na = 0;
    B.forEach(function (b) { nd += b.dropouts; na += b.active; });
    var h = 260, f = frame('chart-recency', h), m = { l: 44, r: 10, t: 22, b: 34 }, iw = f.w - m.l - m.r, ih = h - m.t - m.b;
    var max = .7, y = function (v) { return m.t + ih * (1 - v / max); }, bw = iw / B.length;
    var g = el('g', { class: 'axis' }, f.svg);
    [0, .2, .4, .6].forEach(function (v) { el('line', { x1: m.l, x2: m.l + iw, y1: y(v), y2: y(v), class: 'gridline' }, g); text(g, m.l - 8, y(v) + 4, pct(v, 0), '', 'end'); });
    B.forEach(function (b, i) {
      [[b.dropouts / nd, 'var(--accent)', t().dropGroup, b.dropouts], [b.active / na, 'var(--ink)', t().actGroup, b.active]].forEach(function (s, k) {
        var w = bw * .32, x0 = m.l + i * bw + bw * .16 + k * w;
        el('path', { d: barPath(x0, y(s[0]), w - 2, y(0) - y(s[0]), 3), fill: s[1] }, f.svg);
        text(f.svg, x0 + w / 2, y(s[0]) - 6, pct(s[0], 0), '', 'middle');
      });
      text(f.svg, m.l + i * bw + bw / 2, h - 12, b.band + ' ' + t().days, '', 'middle');
      var hit = el('rect', { x: m.l + i * bw, y: m.t, width: bw, height: ih, fill: 'transparent', class: 'hit' }, f.svg);
      hit.addEventListener('mousemove', function (e) { showTip(e, '<b>' + b.band + ' ' + t().days + '</b><br>' + t().dropGroup + ': ' + fmt(b.dropouts) + ' (' + pct(b.dropouts / nd) + ')<br>' + t().actGroup + ': ' + fmt(b.active) + ' (' + pct(b.active / na) + ')'); });
      hit.addEventListener('mouseleave', hideTip);
    });
    legend('legend-recency', [t().dropGroup + ' (' + fmt(nd) + ')', t().actGroup + ' (' + fmt(na) + ')']);
    document.querySelectorAll('#legend-recency i')[1].style.background = 'var(--ink)';
    table('recency', [t().days, t().dropGroup, t().actGroup], B.map(function (b) { return [b.band, fmt(b.dropouts) + ' (' + pct(b.dropouts / nd) + ')', fmt(b.active) + ' (' + pct(b.active / na) + ')']; }));
  }

  function transition() {
    var tr = D.carrera.transition, n = tr.rows.length;
    var size = Math.min(document.getElementById('chart-transition').clientWidth || 420, 460);
    var f = frame('chart-transition', size), m = { l: 60, t: 46, r: 8, b: 8 };
    var cw = (f.w - m.l - m.r) / n, ch = (size - m.t - m.b) / n;
    text(f.svg, m.l + (f.w - m.l - m.r) / 2, 14, t().nextWeek, 'strong', 'middle');
    var rot = text(f.svg, 14, m.t + (size - m.t - m.b) / 2, t().thisWeek, 'strong', 'middle');
    rot.setAttribute('transform', 'rotate(-90 14 ' + (m.t + (size - m.t - m.b) / 2) + ')');
    tr.rows.forEach(function (r, i) {
      var tot = tr.counts[i].reduce(function (a, b) { return a + b; }, 0);
      text(f.svg, m.l - 10, m.t + i * ch + ch / 2 + 4, r, '', 'end');
      tr.cols.forEach(function (c, j) {
        if (i === 0) text(f.svg, m.l + j * cw + cw / 2, m.t - 8, c, '', 'middle');
        var s = tr.counts[i][j] / tot;
        var cell = el('rect', { x: m.l + j * cw + 1, y: m.t + i * ch + 1, width: cw - 2, height: ch - 2, rx: 4, fill: 'var(--accent)', 'fill-opacity': .08 + s * 1.3 }, f.svg);
        text(f.svg, m.l + j * cw + cw / 2, m.t + i * ch + ch / 2 + 4, pct(s, 0), s > .4 ? 'strong lbl-inv' : '', 'middle');
        cell.addEventListener('mousemove', function (e) { showTip(e, '<b>' + r + ' → ' + c + '</b><br>' + fmt(tr.counts[i][j]) + ' / ' + fmt(tot) + ' ' + t().pairs + ' (' + pct(s) + ')'); });
        cell.addEventListener('mouseleave', hideTip);
      });
    });
    table('transition', [t().thisWeek].concat(tr.cols.map(function (c) { return t().nextWeek + ' ' + c; })), tr.rows.map(function (r, i) { return [r].concat(tr.counts[i].map(function (v) { return fmt(v); })); }));
  }

  function persist() {
    var C = D.carrera, keys = ['r_week_to_week', 'r_weeks5_8_to_1_4', 'auc_any_weeks1_4', 'r_control_past4_to_study', 'r_control_past4_to_after'];
    var step = 46, h = keys.length * step + 30, f = frame('chart-persist', h), lab = Math.min(260, f.w * .45), m = { l: lab, r: 30, t: 10 }, iw = f.w - m.l - m.r;
    var x = function (v) { return m.l + iw * v; };
    var g = el('g', { class: 'axis' }, f.svg);
    [0, .25, .5, .75, 1].forEach(function (v) { el('line', { x1: x(v), x2: x(v), y1: m.t, y2: h - 22, class: 'gridline' }, g); text(g, x(v), h - 6, fmt(v, 2), '', 'middle'); });
    keys.forEach(function (k, i) {
      var y = m.t + i * step + step / 2, ci = C.ci[k];
      text(f.svg, 0, y + 4, t().metrics[k], '');
      el('line', { x1: x(ci[0]), x2: x(ci[1]), y1: y, y2: y, stroke: 'var(--ink)', 'stroke-width': 6, 'stroke-linecap': 'round', opacity: .25 }, f.svg);
      var dot = el('circle', { cx: x(C[k]), cy: y, r: 6, fill: 'var(--accent)' }, f.svg);
      text(f.svg, x(C[k]), y - 12, fmt(C[k], 2), 'strong', 'middle');
      dot.addEventListener('mousemove', function (e) { showTip(e, '<b>' + t().metrics[k] + '</b><br>' + fmt(C[k], 3) + ' (' + fmt(ci[0], 3) + ' · ' + fmt(ci[1], 3) + ')'); });
      dot.addEventListener('mouseleave', hideTip);
    });
    var all = ['r_week_to_week', 'p_any_next_given_any', 'p_any_next_given_none', 'r_weeks5_8_to_1_4', 'auc_any_weeks1_4', 'r_control_past4_to_study', 'r_control_past4_to_after'];
    table('persist', [t().group, t().est, t().ci], all.map(function (k) { return [t().metrics[k], fmt(C[k], 3), fmt(C.ci[k][0], 3) + ' · ' + fmt(C.ci[k][1], 3)]; }));
  }

  function table(name, head, rows) {
    var host = document.querySelector('[data-table="' + name + '"]');
    if (!host) return;
    host.innerHTML = '<div class="scroll"><table><thead><tr>' + head.map(function (h) { return '<th scope="col">' + h + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }

  function renderAll() { km(); renewals(); frequency(); classes(); recency(); transition(); persist(); }
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
