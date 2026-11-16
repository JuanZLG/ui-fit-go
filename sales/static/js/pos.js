/* TuiranFit · Venta rápida (POS)
   Reutiliza los endpoints existentes: buscar_productos, buscar_cliente y crear_venta.
   El servidor vuelve a validar stock, cantidades y cliente: aquí solo se agiliza la captura. */
(function () {
    'use strict';
    var raiz = document.getElementById('pos');
    if (!raiz) return;
    var D = raiz.dataset;
    var cop = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });
    var $ = function (id) { return document.getElementById(id); };

    var productos = [], categoria = 'Todas', texto = '';
    var carrito = {};                      // id -> { p, cantidad }
    var cliente = null;                    // { documento, nombre }
    var CLAVE = 'tf_pos_carrito';

    function norm(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
    function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }
    function aviso(icon, title) {
        if (window.Swal) Swal.fire({ toast: true, position: 'bottom-end', icon: icon, title: title, showConfirmButton: false, timer: 2200 });
    }

    /* ---------- Catálogo ---------- */
    function cargar() {
        return fetch(D.urlProductos + '?q=', { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (d) {
                productos = (d.resultados || []).filter(function (p) { return p.estado === 1 || p.estado === true; });
                // el carrito guardado se ajusta al stock actual
                Object.keys(carrito).forEach(function (id) {
                    var p = productos.filter(function (x) { return String(x.id_producto) === id; })[0];
                    if (!p || p.cantidad <= 0) { delete carrito[id]; return; }
                    carrito[id].p = p; carrito[id].cantidad = Math.min(carrito[id].cantidad, p.cantidad);
                });
                chips(); pintarGrid(); pintarCarrito();
            })
            .catch(function () { $('posGrid').innerHTML = '<div class="tf-empty" style="grid-column:1/-1"><i class="fas fa-triangle-exclamation"></i>No se pudo cargar el catálogo.</div>'; });
    }

    function chips() {
        var cats = ['Todas'];
        productos.forEach(function (p) { if (p.categoria && cats.indexOf(p.categoria) === -1) cats.push(p.categoria); });
        $('posChips').innerHTML = cats.map(function (c) {
            return '<button type="button" class="pos__chip' + (c === categoria ? ' is-active' : '') + '" data-cat="' + esc(c) + '">' + esc(c) + '</button>';
        }).join('');
    }

    function visibles() {
        var q = norm(texto);
        return productos.filter(function (p) {
            return (categoria === 'Todas' || p.categoria === categoria) &&
                (!q || norm(p.nombre_producto + ' ' + p.marca + ' ' + p.categoria).indexOf(q) !== -1);
        });
    }

    function pintarGrid() {
        var lista = visibles();
        $('posContador').textContent = lista.length + (lista.length === 1 ? ' producto' : ' productos');
        if (!lista.length) { $('posGrid').innerHTML = '<div class="tf-empty" style="grid-column:1/-1"><i class="fas fa-box-open"></i>Sin resultados</div>'; return; }
        $('posGrid').innerHTML = lista.map(function (p) {
            var enCarrito = carrito[p.id_producto] ? carrito[p.id_producto].cantidad : 0;
            var agotado = p.cantidad <= 0, disponible = p.cantidad - enCarrito;
            var img = p.presentacion ? D.media + p.presentacion : '';
            return '<button type="button" class="pos__prod' + (agotado ? ' is-agotado' : '') + (enCarrito ? ' is-en-carrito' : '') + '" data-id="' + p.id_producto + '"' + (agotado ? ' disabled' : '') + '>' +
                '<span class="pos__img" style="background-image:url(\'' + D.gorila + '\')">' + (img ? '<img src="' + esc(img) + '" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">' : '') + '</span>' +
                (enCarrito ? '<span class="pos__qty">' + enCarrito + '</span>' : '') +
                '<span class="pos__nombre">' + esc(p.nombre_producto) + '</span>' +
                '<span class="pos__pie"><b>' + cop.format(p.precio_venta) + '</b><i class="pos__stock' + (disponible <= 3 ? ' is-bajo' : '') + '">' + (agotado ? 'Agotado' : disponible + ' en stock') + '</i></span></button>';
        }).join('');
    }

    /* ---------- Carrito ---------- */
    function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(Object.keys(carrito).map(function (id) { return [id, carrito[id].cantidad]; }))); } catch (e) { } }
    function restaurar() {
        try { (JSON.parse(localStorage.getItem(CLAVE)) || []).forEach(function (par) { carrito[par[0]] = { p: null, cantidad: par[1] }; }); } catch (e) { }
    }

    function agregar(id) {
        var p = productos.filter(function (x) { return String(x.id_producto) === String(id); })[0];
        if (!p) return;
        var actual = carrito[id] ? carrito[id].cantidad : 0;
        if (actual + 1 > p.cantidad) { aviso('warning', 'No hay más stock de «' + p.nombre_producto + '»'); return; }
        carrito[id] = { p: p, cantidad: actual + 1 };
        cambiar();
    }
    function cambiarCantidad(id, delta) {
        var l = carrito[id]; if (!l) return;
        var n = l.cantidad + delta;
        if (n <= 0) { delete carrito[id]; }
        else if (n > l.p.cantidad) { aviso('warning', 'Solo hay ' + l.p.cantidad + ' unidades'); return; }
        else { l.cantidad = n; }
        cambiar();
    }
    function cambiar() { guardar(); pintarCarrito(); pintarGrid(); }

    function calculos() {
        var lineas = Object.keys(carrito).map(function (id) { return carrito[id]; }).filter(function (l) { return l.p; });
        var subtotal = 0, costo = 0;
        lineas.forEach(function (l) { subtotal += l.p.precio_venta * l.cantidad; costo += l.p.precio_compra * l.cantidad; });
        var d = Math.min(Math.max(parseFloat($('posDescuento').value) || 0, 0), 100);
        var valorDescuento = Math.round(subtotal * d / 100);
        var total = subtotal - valorDescuento;
        return { lineas: lineas, subtotal: subtotal, descuento: d, valorDescuento: valorDescuento, total: total, margen: total - costo };
    }

    function pintarCarrito() {
        var c = calculos();
        $('posLineas').innerHTML = c.lineas.length ? c.lineas.map(function (l) {
            return '<li class="pos__linea" data-id="' + l.p.id_producto + '"><div class="pos__linea-info"><span class="pos__linea-nombre">' + esc(l.p.nombre_producto) + '</span>' +
                '<span class="pos__linea-precio">' + cop.format(l.p.precio_venta) + ' c/u</span></div>' +
                '<div class="pos__paso"><button type="button" data-d="-1" aria-label="Quitar uno">−</button><b>' + l.cantidad + '</b><button type="button" data-d="1" aria-label="Agregar uno">+</button></div>' +
                '<strong class="pos__linea-total">' + cop.format(l.p.precio_venta * l.cantidad) + '</strong></li>';
        }).join('') : '<li class="tf-empty"><i class="fas fa-cart-shopping"></i>Aún no hay productos</li>';
        $('posSubtotal').textContent = cop.format(c.subtotal);
        $('posFilaDescuento').hidden = !c.valorDescuento;
        $('posValorDescuento').textContent = '−' + cop.format(c.valorDescuento);
        $('posMargen').textContent = cop.format(c.margen);
        $('posTotal').textContent = cop.format(c.total);
        var listo = c.lineas.length > 0 && !!cliente;
        $('posCobrar').disabled = !listo;
        $('posAyuda').textContent = !c.lineas.length ? 'Agrega productos para empezar.' : !cliente ? 'Elige un cliente para poder cobrar.' : 'Todo listo: pulsa Cobrar.';
    }

    /* ---------- Cliente ---------- */
    var tClientes = null;
    function buscarClientes() {
        var q = $('posCliente').value.trim(), ul = $('posClientes');
        clearTimeout(tClientes);
        if (q.length < 2) { ul.hidden = true; return; }
        tClientes = setTimeout(function () {
            fetch(D.urlClientes + '?nombreCliente=' + encodeURIComponent(q) + '&tipoPedido=' + encodeURIComponent('sin pedido'), { credentials: 'same-origin' })
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    var rs = d.resultados || [];
                    ul.innerHTML = rs.length ? rs.map(function (c) {
                        return '<li class="' + (c.estado ? '' : 'is-inactivo') + '" data-doc="' + esc(c.documento) + '" data-nombre="' + esc(c.nombre_cliente) + '" data-activo="' + (c.estado ? 1 : 0) + '"><span>' + esc(c.nombre_cliente) + '</span><small>' + esc(c.documento) + (c.estado ? '' : ' · inactivo') + '</small></li>';
                    }).join('') : '<li class="is-vacio">Sin resultados</li>';
                    ul.hidden = false;
                });
        }, 200);
    }
    function elegirCliente(doc, nombre) {
        cliente = { documento: doc, nombre: nombre };
        $('posCliente').value = ''; $('posClientes').hidden = true; $('posCliente').hidden = true;
        $('posClienteElegido').hidden = false; $('posClienteElegido').innerHTML = '<b>' + esc(nombre) + '</b><small>' + esc(doc) + '</small>';
        $('posQuitarCliente').hidden = false; pintarCarrito();
    }
    function quitarCliente() {
        cliente = null; $('posCliente').hidden = false; $('posClienteElegido').hidden = true; $('posQuitarCliente').hidden = true;
        $('posCliente').focus(); pintarCarrito();
    }

    /* ---------- Cobro ---------- */
    var cobrando = false;
    function cobrar() {
        var c = calculos();
        if (cobrando || !c.lineas.length || !cliente) return;
        cobrando = true; $('posCobrar').disabled = true; $('posCobrar').classList.add('is-cargando');
        var productosPayload = {};
        c.lineas.forEach(function (l) {
            var total = l.p.precio_venta * l.cantidad;
            productosPayload[l.p.id_producto] = {
                idPedido: 'no pedido', cantidad: l.cantidad, precioCompra: l.p.precio_compra, precioVenta: l.p.precio_venta,
                descuentoProducto: 'No aplica', margenGananciaProducto: (l.p.precio_venta - l.p.precio_compra) * l.cantidad,
                totalProducto: total, totalProductoDescuento: 'No aplica'
            };
        });
        fetch(D.urlVenta, {
            method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                documentoCliente: cliente.documento, totalVenta: c.total, margenGananciaVenta: c.margen,
                descuentoVenta: c.descuento ? String(c.descuento) : 'No aplica',
                totalVentaDescuento: c.valorDescuento ? String(c.valorDescuento) : 'No aplica', productos: productosPayload
            })
        }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
            .then(function (res) {
                if (!res.ok || !res.d.success) throw new Error((res.d && res.d.error) || 'No se pudo registrar la venta.');
                var url = D.urlFactura.replace(/0\/?$/, res.d.id_venta + '/');
                var total = cop.format(c.total);
                carrito = {}; guardar(); $('posDescuento').value = 0; quitarCliente();
                return cargar().then(function () {
                    Swal.fire({
                        icon: 'success', title: 'Venta registrada', html: '<div style="font:400 2.2rem var(--tf-display);letter-spacing:.03em">' + total + '</div>',
                        showCancelButton: true, confirmButtonText: 'Imprimir comprobante', cancelButtonText: 'Nueva venta', reverseButtons: true
                    }).then(function (r) { if (r.isConfirmed) window.open(url, '_blank', 'noopener'); $('posBuscar').focus(); });
                });
            })
            .catch(function (e) { Swal.fire({ icon: 'error', title: 'No se registró la venta', text: e.message, confirmButtonText: 'Entendido' }); })
            .then(function () { cobrando = false; $('posCobrar').classList.remove('is-cargando'); pintarCarrito(); });
    }

    /* ---------- Eventos ---------- */
    $('posBuscar').addEventListener('input', function () { texto = this.value; pintarGrid(); });
    $('posBuscar').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { var v = visibles().filter(function (p) { return p.cantidad > 0; }); if (v.length === 1) { agregar(v[0].id_producto); this.select(); } }
        if (e.key === 'Escape') { this.value = ''; texto = ''; pintarGrid(); }
    });
    $('posChips').addEventListener('click', function (e) { var b = e.target.closest('.pos__chip'); if (b) { categoria = b.dataset.cat; chips(); pintarGrid(); } });
    $('posGrid').addEventListener('click', function (e) { var b = e.target.closest('.pos__prod'); if (b && !b.disabled) agregar(b.dataset.id); });
    $('posLineas').addEventListener('click', function (e) {
        var b = e.target.closest('button[data-d]'), li = e.target.closest('.pos__linea');
        if (b && li) cambiarCantidad(li.dataset.id, parseInt(b.dataset.d, 10));
    });
    $('posVaciar').addEventListener('click', function () { carrito = {}; cambiar(); });
    $('posDescuento').addEventListener('input', pintarCarrito);
    $('posCliente').addEventListener('input', buscarClientes);
    $('posClientes').addEventListener('click', function (e) {
        var li = e.target.closest('li[data-doc]'); if (!li) return;
        if (li.dataset.activo !== '1') { aviso('warning', 'El cliente está inactivo'); return; }
        elegirCliente(li.dataset.doc, li.dataset.nombre);
    });
    $('posQuitarCliente').addEventListener('click', quitarCliente);
    $('posCobrar').addEventListener('click', cobrar);
    document.addEventListener('mousedown', function (e) { if (!e.target.closest('.pos__cliente')) $('posClientes').hidden = true; });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'F2') { e.preventDefault(); $('posBuscar').focus(); $('posBuscar').select(); }
        if (e.key === 'F9') { e.preventDefault(); cobrar(); }
    });

    restaurar();
    cargar().then(function () { $('posBuscar').focus(); });
})();
