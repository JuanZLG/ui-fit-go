/* =========================================================================
   TUIRANFIT · Capa de interacción "ARENA"
   - Barra de progreso al navegar
   - Foco de luz roja que sigue al cursor sobre tarjetas
   - Paralaje suave del hero
   - Paleta de comandos (Ctrl/⌘ + K  ó  "/")
   - TF.countUp(): cifras que cuentan hacia arriba
   Sin dependencias. Respeta prefers-reduced-motion.
   ========================================================================= */
(function () {
    'use strict';

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var TF = window.TF = window.TF || {};

    /* ---------- Cifras animadas ---------- */
    TF.countUp = function (el, target, format, duration) {
        if (typeof el === 'string') el = document.getElementById(el);
        if (!el) return;
        format = format || function (n) { return Math.round(n).toLocaleString('es-CO'); };
        target = Number(target) || 0;
        el.classList.remove('is-loading');
        if (reduce || target === 0) { el.textContent = format(target); return; }
        var t0 = null; duration = duration || 1100;
        function step(ts) {
            if (t0 === null) t0 = ts;
            var p = Math.min((ts - t0) / duration, 1);
            var eased = 1 - Math.pow(1 - p, 4);                    // easeOutQuart
            el.textContent = format(target * eased);
            if (p < 1) requestAnimationFrame(step); else el.textContent = format(target);
        }
        requestAnimationFrame(step);
    };

    /* ---------- Barra de progreso de navegación ---------- */
    var bar = document.createElement('div');
    bar.id = 'tfProgress';
    document.body.appendChild(bar);
    function progressStart() { bar.style.opacity = 1; bar.style.width = '72%'; }
    document.addEventListener('click', function (e) {
        var a = e.target.closest && e.target.closest('a[href]');
        if (!a || e.defaultPrevented || e.ctrlKey || e.metaKey || e.shiftKey || a.target === '_blank') return;
        var h = a.getAttribute('href');
        if (!h || h.charAt(0) === '#' || h.indexOf('javascript:') === 0 || a.hasAttribute('data-toggle') || a.hasAttribute('data-lightbox')) return;
        progressStart();
    });
    window.addEventListener('pageshow', function () { bar.style.width = '0'; bar.style.opacity = 0; });

    /* ---------- Foco de luz que sigue al cursor ---------- */
    if (!reduce) {
        document.addEventListener('mousemove', function (e) {
            var t = e.target.closest && e.target.closest('.card, .tf-panel, .tf-kpi, .tf-hero');
            if (!t) return;
            var r = t.getBoundingClientRect();
            t.style.setProperty('--mx', (e.clientX - r.left) + 'px');
            t.style.setProperty('--my', (e.clientY - r.top) + 'px');
        }, { passive: true });

        /* Paralaje del hero: las pinceladas se desplazan con el cursor */
        var hero = document.querySelector('.tf-hero');
        if (hero) {
            hero.addEventListener('mousemove', function (e) {
                var r = hero.getBoundingClientRect();
                hero.style.setProperty('--px', ((e.clientX - r.left) / r.width - .5).toFixed(3));
                hero.style.setProperty('--py', ((e.clientY - r.top) / r.height - .5).toFixed(3));
            }, { passive: true });
            hero.addEventListener('mouseleave', function () { hero.style.setProperty('--px', 0); hero.style.setProperty('--py', 0); });
        }
    }

    /* ---------- Paleta de comandos ---------- */
    function buildIndex() {
        var items = [], seen = {};
        var links = document.querySelectorAll('#accordionSidebar a[href]');
        Array.prototype.forEach.call(links, function (a) {
            var href = a.getAttribute('href');
            if (!href || href === '#' || seen[href]) return;
            seen[href] = true;
            var label = a.textContent.replace(/\s+/g, ' ').trim();
            var group = 'Ir a';
            var panel = a.closest('.collapse');
            if (panel && panel.previousElementSibling) group = panel.previousElementSibling.textContent.replace(/\s+/g, ' ').trim();
            items.push({ label: label, group: group, href: href });
        });
        items.push({ label: 'Tienda pública', group: 'Ir a', href: '/Brutality/' });
        items.push({ label: 'Cerrar sesión', group: 'Cuenta', run: function () { window.jQuery ? jQuery('#logoutModal').modal('show') : (location.href = '/logout/'); } });
        return items;
    }

    var overlay, input, list, items = [], filtered = [], active = 0;

    function render() {
        list.innerHTML = '';
        if (!filtered.length) {
            list.innerHTML = '<li class="tf-cmd__empty">Sin resultados</li>';
            return;
        }
        filtered.forEach(function (it, i) {
            var li = document.createElement('li');
            li.className = 'tf-cmd__item' + (i === active ? ' is-active' : '');
            li.setAttribute('role', 'option');
            li.innerHTML = '<span class="tf-cmd__idx">' + String(i + 1).padStart(2, '0') + '</span>' +
                '<span class="tf-cmd__label"></span><span class="tf-cmd__group"></span>';
            li.children[1].textContent = it.label;
            li.children[2].textContent = it.group;
            li.addEventListener('mousemove', function () { if (active !== i) { active = i; mark(); } });
            li.addEventListener('click', function () { go(it); });
            list.appendChild(li);
        });
    }
    function mark() {
        Array.prototype.forEach.call(list.children, function (li, i) { li.classList.toggle('is-active', i === active); });
        var el = list.children[active]; if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
    }
    function filter() {
        var q = input.value.trim().toLowerCase();
        filtered = !q ? items.slice() : items.filter(function (it) { return (it.label + ' ' + it.group).toLowerCase().indexOf(q) !== -1; });
        active = 0; render();
    }
    function go(it) {
        close();
        if (it.run) { it.run(); return; }
        progressStart(); location.href = it.href;
    }
    function open() {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'tf-cmd';
            overlay.innerHTML =
                '<div class="tf-cmd__box" role="dialog" aria-modal="true" aria-label="Paleta de comandos">' +
                '<div class="tf-cmd__bar"><span class="tf-cmd__slash">//</span>' +
                '<input class="tf-cmd__input" type="text" placeholder="Ir a… usuarios, ventas, productos" autocomplete="off" spellcheck="false">' +
                '<kbd>ESC</kbd></div><ul class="tf-cmd__list" role="listbox"></ul>' +
                '<div class="tf-cmd__foot"><span><kbd>↑</kbd><kbd>↓</kbd> navegar</span><span><kbd>↵</kbd> abrir</span><span><kbd>esc</kbd> cerrar</span></div></div>';
            document.body.appendChild(overlay);
            input = overlay.querySelector('input'); list = overlay.querySelector('ul');
            overlay.addEventListener('mousedown', function (e) { if (e.target === overlay) close(); });
            input.addEventListener('input', filter);
            input.addEventListener('keydown', function (e) {
                if (e.key === 'ArrowDown') { e.preventDefault(); active = Math.min(active + 1, filtered.length - 1); mark(); }
                else if (e.key === 'ArrowUp') { e.preventDefault(); active = Math.max(active - 1, 0); mark(); }
                else if (e.key === 'Enter') { e.preventDefault(); if (filtered[active]) go(filtered[active]); }
            });
        }
        items = buildIndex(); input.value = ''; filter();
        overlay.classList.add('is-open'); document.documentElement.classList.add('tf-cmd-open');
        setTimeout(function () { input.focus(); }, 30);
    }
    function close() {
        if (!overlay) return;
        overlay.classList.remove('is-open'); document.documentElement.classList.remove('tf-cmd-open');
    }
    TF.openPalette = open;

    document.addEventListener('keydown', function (e) {
        var isOpen = overlay && overlay.classList.contains('is-open');
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); isOpen ? close() : open(); return; }
        if (e.key === 'Escape' && isOpen) { close(); return; }
        var tag = (e.target.tagName || '').toLowerCase();
        if (e.key === '/' && !isOpen && tag !== 'input' && tag !== 'textarea' && tag !== 'select' && !e.target.isContentEditable) { e.preventDefault(); open(); }
    });
    document.addEventListener('click', function (e) {
        if (e.target.closest && e.target.closest('[data-tf-palette]')) { e.preventDefault(); open(); }
    });
})();
