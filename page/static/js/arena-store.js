/* TuiranFit · Tienda "ARENA": inclinación 3D de tarjetas, foco de luz, paralaje y fallback de imágenes */
(function () {
    'use strict';
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Si una imagen de producto no carga, se oculta y se ve el gorila de fondo
    document.addEventListener('error', function (e) {
        var t = e.target;
        if (t && t.tagName === 'IMG' && (t.closest('.product-image') || t.closest('.search-card-desk') || t.closest('.search-card'))) {
            t.style.visibility = 'hidden';
        }
    }, true);

    // Imágenes que ya fallaron antes de registrar el listener
    function revisarImagenes() {
        document.querySelectorAll('.product-image img, .search-card-desk img, .search-card img').forEach(function (img) {
            if (img.complete && img.naturalWidth === 0) img.style.visibility = 'hidden';
        });
    }
    document.addEventListener('DOMContentLoaded', revisarImagenes);
    window.addEventListener('load', revisarImagenes);

    if (reduce) return;

    // Inclinación 3D + foco de luz en cada tarjeta
    document.addEventListener('mousemove', function (e) {
        var card = e.target.closest && e.target.closest('.product-card');
        if (!card) return;
        var r = card.getBoundingClientRect();
        var x = e.clientX - r.left, y = e.clientY - r.top;
        card.style.setProperty('--mx', x + 'px');
        card.style.setProperty('--my', y + 'px');
        card.style.setProperty('--ry', (((x / r.width) - .5) * 9).toFixed(2) + 'deg');
        card.style.setProperty('--rx', ((.5 - (y / r.height)) * 9).toFixed(2) + 'deg');
    }, { passive: true });
    document.addEventListener('mouseout', function (e) {
        var card = e.target.closest && e.target.closest('.product-card');
        if (card && !card.contains(e.relatedTarget)) { card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); }
    });

    // Paralaje del hero
    var hero = document.querySelector('.store-hero');
    if (hero) {
        hero.addEventListener('mousemove', function (e) {
            var r = hero.getBoundingClientRect();
            hero.style.setProperty('--px', ((e.clientX - r.left) / r.width - .5).toFixed(3));
            hero.style.setProperty('--py', ((e.clientY - r.top) / r.height - .5).toFixed(3));
        }, { passive: true });
    }
})();
