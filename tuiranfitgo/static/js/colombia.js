/* TuiranFit · Departamentos y municipios de Colombia (datos locales, sin servicios externos).
   Fuente: Divipola del Ministerio de Salud (datos.gov.co), empaquetada en static/data/colombia.json.
   Antes se consultaba un conjunto de datos de datos.gov.co que ya no existe, por eso los
   selectores quedaban vacíos.

   Uso:  TFColombia.vincular(selectDepartamento, selectMunicipio, 'Antioquia', 'Medellín');          */
(function () {
    'use strict';

    var cache = null;

    function cargar() {
        if (!cache) {
            cache = fetch(window.TF_COLOMBIA_URL, { credentials: 'same-origin' })
                .then(function (r) { if (!r.ok) throw new Error('No se pudo cargar la lista de municipios'); return r.json(); })
                .then(function (j) { return j.departamentos; })
                .catch(function (e) { cache = null; throw e; });
        }
        return cache;
    }

    // "BOGOTÁ, D.C." y "Bogotá D.C." deben considerarse el mismo valor
    function norm(s) {
        return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/gi, '').toLowerCase();
    }

    function resolver(el) { return typeof el === 'string' ? document.querySelector(el) : (el && el.jquery ? el[0] : el); }

    function opcion(texto, valor) {
        var o = document.createElement('option');
        o.value = valor; o.textContent = texto;
        return o;
    }

    function llenar(select, nombres, valor, placeholder) {
        select.innerHTML = '';
        select.appendChild(opcion(placeholder, ''));
        nombres.forEach(function (n) { select.appendChild(opcion(n, n)); });

        var objetivo = norm(valor), elegido = '';
        if (objetivo) {
            for (var i = 0; i < nombres.length; i++) { if (norm(nombres[i]) === objetivo) { elegido = nombres[i]; break; } }
            if (!elegido && valor) {                      // valor guardado que no está en la lista: se conserva
                select.appendChild(opcion(valor, valor)); elegido = valor;
            }
        }
        select.value = elegido;
        select.dispatchEvent(new Event('change', { bubbles: true }));
        return elegido;
    }


    /* ---------- Selector con buscador (reemplaza visualmente al <select>) ----------
       El <select> original se conserva oculto: sigue guardando el valor, dispara "change"
       y recibe las clases de validación, así el resto del código no cambia. */
    var contador = 0;

    function buscable(select) {
        select = resolver(select);
        if (!select || select._tfCombo) return;
        select._tfCombo = true;

        var id = 'tfc' + (++contador);
        var combo = document.createElement('div');
        combo.className = 'tf-combo';
        combo.innerHTML =
            '<button type="button" class="tf-combo__btn" aria-haspopup="listbox" aria-expanded="false">' +
            '<span class="tf-combo__text"></span><i class="tf-combo__caret" aria-hidden="true"></i></button>';
        // El panel vive en <body>: no cuenta como campo del formulario ni lo recortan tarjetas/modales
        var panel = document.createElement('div');
        panel.className = 'tf-combo__panel'; panel.hidden = true;
        panel.innerHTML =
            '<div class="tf-combo__bar"><input type="text" class="tf-combo__search" placeholder="Buscar…" autocomplete="off" spellcheck="false" aria-controls="' + id + '"></div>' +
            '<ul class="tf-combo__list" id="' + id + '" role="listbox"></ul>';
        document.body.appendChild(panel);
        select.insertAdjacentElement('afterend', combo);   // hermano: .siblings('.error-message') sigue funcionando
        select.classList.add('tf-combo__native');
        select.tabIndex = -1;

        var btn = combo.querySelector('.tf-combo__btn'), texto = combo.querySelector('.tf-combo__text');
        var buscador = panel.querySelector('.tf-combo__search'), lista = panel.querySelector('.tf-combo__list');
        var filtrados = [], activo = 0;

        function opciones() {
            return Array.prototype.map.call(select.options, function (o) { return { value: o.value, text: o.textContent }; })
                .filter(function (o) { return o.value !== ''; });
        }
        function placeholder() { var o = select.options[0]; return o && o.value === '' ? o.textContent : 'Selecciona…'; }

        function pintarBoton() {
            var o = select.selectedOptions && select.selectedOptions[0];
            var tiene = o && o.value !== '';
            texto.textContent = tiene ? o.textContent : placeholder();
            combo.classList.toggle('is-empty', !tiene);
            combo.classList.toggle('is-invalid', select.classList.contains('is-invalid'));
            combo.classList.toggle('is-disabled', select.disabled);
            btn.disabled = select.disabled;
        }

        function pintarLista() {
            var q = norm(buscador.value);
            filtrados = opciones().filter(function (o) { return !q || norm(o.text).indexOf(q) !== -1; });
            lista.innerHTML = '';
            if (!filtrados.length) {
                var vacio = document.createElement('li'); vacio.className = 'tf-combo__empty'; vacio.textContent = 'Sin resultados';
                lista.appendChild(vacio); return;
            }
            var actual = select.value;
            activo = Math.max(0, filtrados.findIndex(function (o) { return o.value === actual; }));
            if (q) activo = 0;
            filtrados.forEach(function (o, i) {
                var li = document.createElement('li');
                li.className = 'tf-combo__item' + (o.value === actual ? ' is-selected' : '') + (i === activo ? ' is-active' : '');
                li.setAttribute('role', 'option'); li.textContent = o.text; li.dataset.i = i;
                lista.appendChild(li);
            });
            marcar(true);
        }

        function marcar(centrar) {
            Array.prototype.forEach.call(lista.children, function (li, i) { li.classList.toggle('is-active', i === activo); });
            var el = lista.children[activo];
            if (el && el.scrollIntoView) el.scrollIntoView({ block: centrar ? 'center' : 'nearest' });
        }

        function posicionar() {
            var r = btn.getBoundingClientRect();
            if (r.bottom < 0 || r.top > window.innerHeight) { cerrar(false); return; }       // el botón salió de la pantalla
            var alto = Math.min(panel.offsetHeight || 330, 330);
            var abajo = window.innerHeight - r.bottom, arriba = r.top;
            var haciaArriba = abajo < alto + 12 && arriba > abajo;
            panel.style.width = r.width + 'px'; panel.style.left = r.left + 'px';
            panel.style.top = haciaArriba ? 'auto' : (r.bottom + 4) + 'px';
            panel.style.bottom = haciaArriba ? (window.innerHeight - r.top + 4) + 'px' : 'auto';
            panel.classList.toggle('is-up', haciaArriba);
            lista.style.maxHeight = Math.max(140, Math.min(260, (haciaArriba ? arriba : abajo) - 90)) + 'px';
        }

        function abrir() {
            if (select.disabled) return;
            document.querySelectorAll('.tf-combo.is-open').forEach(function (c) { if (c !== combo) c.classList.remove('is-open'); });
            buscador.value = ''; panel.hidden = false;
            posicionar();
            combo.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true');
            pintarLista(); posicionar();
            // en móvil evita saltos: el foco se da después de pintar
            setTimeout(function () { buscador.focus(); }, 10);
        }
        function cerrar(devolverFoco) {
            panel.hidden = true; combo.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false');
            if (devolverFoco) btn.focus();
        }
        function elegir(i) {
            var o = filtrados[i]; if (!o) return;
            select.value = o.value;
            select.classList.remove('is-invalid');
            select.dispatchEvent(new Event('change', { bubbles: true }));
            select.dispatchEvent(new Event('input', { bubbles: true }));
            pintarBoton(); cerrar(true);
        }

        btn.addEventListener('click', function () { combo.classList.contains('is-open') ? cerrar(false) : abrir(); });
        btn.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); abrir(); }
        });
        buscador.addEventListener('input', pintarLista);
        buscador.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowDown') { e.preventDefault(); activo = Math.min(activo + 1, filtrados.length - 1); marcar(); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); activo = Math.max(activo - 1, 0); marcar(); }
            else if (e.key === 'Enter') { e.preventDefault(); elegir(activo); }
            else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); cerrar(true); }
            else if (e.key === 'Tab') { cerrar(false); }
        });
        lista.addEventListener('mousemove', function (e) {
            var li = e.target.closest('.tf-combo__item');
            if (li && Number(li.dataset.i) !== activo) { activo = Number(li.dataset.i); marcar(); }
        });
        lista.addEventListener('mousedown', function (e) { e.preventDefault(); });       // no pierde el foco antes del clic
        lista.addEventListener('click', function (e) {
            var li = e.target.closest('.tf-combo__item'); if (li) elegir(Number(li.dataset.i));
        });
        document.addEventListener('mousedown', function (e) { if (!combo.contains(e.target) && !panel.contains(e.target)) cerrar(false); });
        window.addEventListener('resize', function () { if (combo.classList.contains('is-open')) posicionar(); });
        window.addEventListener('scroll', function (e) {
            if (combo.classList.contains('is-open') && !panel.contains(e.target)) posicionar();
        }, true);

        // El código existente cambia el <select> directamente: el botón se mantiene al día
        new MutationObserver(function () { pintarBoton(); if (combo.classList.contains('is-open')) pintarLista(); })
            .observe(select, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'disabled'] });
        select.addEventListener('change', pintarBoton);
        select.addEventListener('focus', function () { btn.focus(); });          // <label for="..."> enfoca el botón
        pintarBoton();
    }

    var TFColombia = {
        buscable: buscable,
        departamentos: function (select, valor) {
            select = resolver(select); buscable(select);
            return cargar().then(function (deptos) {
                return llenar(select, deptos.map(function (d) { return d.nombre; }), valor, 'Seleccionar');
            });
        },
        municipios: function (select, departamento, valor) {
            select = resolver(select); buscable(select);
            return cargar().then(function (deptos) {
                var d = deptos.filter(function (x) { return norm(x.nombre) === norm(departamento); })[0];
                return llenar(select, d ? d.municipios : [], valor, 'Seleccionar');
            });
        },
        /** Llena el departamento y mantiene el municipio sincronizado cuando cambia. */
        vincular: function (selDepto, selMuni, valorDepto, valorMuni) {
            selDepto = resolver(selDepto); selMuni = resolver(selMuni);
            buscable(selDepto); buscable(selMuni);
            var primera = true;
            selDepto.addEventListener('change', function () {
                var muni = primera ? valorMuni : '';
                TFColombia.municipios(selMuni, selDepto.value, muni);
                primera = false;
            });
            return TFColombia.departamentos(selDepto, valorDepto);
        }
    };

    window.TFColombia = TFColombia;
})();
