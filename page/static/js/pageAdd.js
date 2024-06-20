$(document).ready(function () {

    function increment(button) {
        let input = $(button).parent().find('.quantity');
        input.val(parseInt(input.val()) + 1).trigger('input');
    }

    function decrement(button) {
        let input = $(button).parent().find('.quantity');
        if (input.val() > 1) {
            input.val(parseInt(input.val()) - 1).trigger('input');
        }
    }

    $('.increment').on('click', function () {
        increment(this);
    });

    $('.decrement').on('click', function () {
        decrement(this);
    });

    let carrito = localStorage.getItem('carrito') ? JSON.parse(localStorage.getItem('carrito')) : {};

    $('.item-order').parent().mouseenter(function () {
        $(this).find('.item-order').next().find('.list-order').addClass('show');
    });

    $('.item-order').parent().mouseleave(function () {
        $(this).find('.item-order').next().find('.list-order').removeClass('show');
    });

    function actualizarCantidadProductos() {
        let carrito = JSON.parse(localStorage.getItem('carrito'));
        let isMobile = window.innerWidth <= 768;
        let orderCant = document.querySelector(isMobile ? '.order-cant-mobile' : '.order-cant');
        actualizarCarrito()

        if (!carrito) {
            carrito = {};
            orderCant.classList.remove('show');
            return;
        }

        let cantidadTotal = Object.keys(carrito).length;

        if (cantidadTotal === 0) {
            orderCant.classList.remove('show');
            return;
        }

        orderCant.textContent = cantidadTotal;
        cantidadTotal = 0;
        orderCant.classList.add('show');
    }

    actualizarCantidadProductos();

    window.addEventListener('resize', function () {
        actualizarCantidadProductos();
    });


    function actualizarCarrito() {
        let carrito = localStorage.getItem('carrito');
        if (carrito) {
            carrito = JSON.parse(carrito);
            if (Object.keys(carrito).length === 0) {
                $("#enlace-ver-pedido").addClass("enlace-inactivo-pedido");
            } else {
                $("#enlace-ver-pedido").removeClass("enlace-inactivo-pedido");
            }
        } else {
            $("#enlace-ver-pedido").addClass("enlace-inactivo-pedido");
            carrito = {};
        }

        let html = '';
        let total = 0;

        for (let idProducto in carrito) {
            let producto = carrito[idProducto];
            let subtotal = Number(producto.precio.replace('$', '').replace(/,/g, '')) * producto.cantidad;
            total += subtotal;

            html += `
                <li class="p-3 d-flex position-relative" data-id="${idProducto}" style="font-size:14px">
                    <div style="width:95%;">
                        <div class="d-flex justify-content-start gap-3">
                            <img src="${producto.imgSrc}" id="img-producto" class="img-fluid" alt="Imagen" style="width:50px; height:50px;">
                            <span style="width: 110px; word-wrap: break-word;
                            overflow-wrap: break-word;">${producto.nombreProducto} x ${producto.sabor}</span>
                        </div>
                        <div class="d-flex gap-2 justify-content-end m-1">
                            <span ><strong>${producto.precio} x ${producto.cantidad}</strong></span>
                        </div>
                    </div>
                    <span class="remove-order position-absolute top-0 end-0" style="width:5%; font-size: 14px"><i class="fas fa-trash"></i></span>
                </li>
                <hr class="m-0">
            `;
        }

        $('.list-item').html(html);
        document.getElementById('total-order').textContent = "$" + total.toLocaleString();
    }

    actualizarCarrito();

    $('.list-item').on('click', '.remove-order', function () {
        let idUnico = $(this).parent().attr('data-id');

        let carrito = JSON.parse(localStorage.getItem('carrito')) || {};
        delete carrito[idUnico];
        localStorage.setItem('carrito', JSON.stringify(carrito));

        $(this).parent().remove();
        actualizarCantidadProductos();
    });

    function productoAlCarrito() {
        var avisos = document.querySelectorAll('.show-avis-carrito');
        avisos.forEach(function (aviso) {
            aviso.style.cssText = 'width:100%; background-color: #28a746a8; color: #222; text-align: center; padding: 2px 10px; box-shadow: 0 2px 4px rgba(0,0,0,.2); position:absolute; top:0;';
            aviso.innerHTML = '¡Producto agregado al carrito con éxito! <a href="/Brutality/ver_pedido/" style="color: #000; text-decoration: underline; padding-left: 10px;">Ver aquí</a>';
            aviso.style.display = 'block';
        });

        setTimeout(function () {
            avisos.forEach(function (aviso) {
                aviso.style.display = 'none';
            });
        }, 4000);
    }

    document.querySelectorAll('.product-form-mobile').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            let imgSrc = form.querySelector('#img-producto').src;
            let nombreProducto = form.querySelector('#producto').textContent.trim();
            let precio = form.querySelector('#precio').textContent.trim();
            let sabor = form.querySelector('select[name="sabor"]').value;
            let cantidad = parseInt(form.querySelector('input[name="cantidad"]').value);
            let idProducto = form.dataset.id;

            let carrito = JSON.parse(localStorage.getItem('carrito')) || {};

            let idPedido = generarIdUnico(nombreProducto, sabor);

            if (carrito[idPedido] && carrito[idPedido].nombreProducto === nombreProducto && carrito[idPedido].sabor === sabor) {
                carrito[idPedido].cantidad = parseInt(carrito[idPedido].cantidad);
                carrito[idPedido].cantidad += cantidad;
            } else {
                carrito[idPedido] = {
                    idDelProducto: idProducto,
                    imgSrc: imgSrc,
                    nombreProducto: nombreProducto,
                    precio: precio,
                    sabor: sabor,
                    cantidad: cantidad
                };
            }

            localStorage.setItem('carrito', JSON.stringify(carrito));

            actualizarCantidadProductos();
            productoAlCarrito();
        });
    });

    document.querySelectorAll('.product-form-desk').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            let imgSrc = form.querySelector('#img-producto').src;
            let nombreProducto = form.querySelector('#producto').textContent.trim();
            let precio = form.querySelector('#precio').textContent.trim();
            let sabor = form.querySelector('select[name="sabor"]').value;
            let cantidad = parseInt(form.querySelector('input[name="cantidad"]').value);
            let idProducto = form.dataset.id;
            let carrito = JSON.parse(localStorage.getItem('carrito')) || {};
            let idPedido = generarIdUnico(nombreProducto, sabor);

            if (carrito[idPedido] && carrito[idPedido].nombreProducto === nombreProducto && carrito[idPedido].sabor === sabor) {
                carrito[idPedido].cantidad = parseInt(carrito[idPedido].cantidad);
                carrito[idPedido].cantidad += cantidad;
            } else {
                carrito[idPedido] = {
                    idDelProducto: idProducto,
                    imgSrc: imgSrc,
                    nombreProducto: nombreProducto,
                    precio: precio,
                    sabor: sabor,
                    cantidad: cantidad
                };
            }

            localStorage.setItem('carrito', JSON.stringify(carrito));

            actualizarCantidadProductos();
            productoAlCarrito();
        });
    });


    function generarIdUnico(nombre, sabor) {
        let hash = 0;
        let identificador = nombre + sabor;
        for (let i = 0; i < identificador.length; i++) {
            let char = identificador.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash |= 0;
        }
        return Math.abs(hash);
    }


    obtenerDepartamentos();

    function obtenerDepartamentos() {
        $.ajax({
            url: "https://www.datos.gov.co/resource/xdk5-pm3f.json",
            type: "GET",
            data: {
                "$limit": 5000,
            }
        }).done(function (data) {
            const departamentos = [...new Set(data.map(item => item.departamento))];
            const departamentoSelect = $("#departamento");
            departamentos.forEach(function (depto) {
                departamentoSelect.append($("<option>", {
                    value: depto,
                    text: depto
                }));
            });

            departamentoSelect.change(obtenerMunicipios);
        });
    }

    function obtenerMunicipios() {
        const departamentoSeleccionado = $("#departamento").val();
        const municipioSelect = $("#municipio");

        $.ajax({
            url: "https://www.datos.gov.co/resource/xdk5-pm3f.json",
            type: "GET",
            data: {
                "$limit": 5000,
                "departamento": departamentoSeleccionado
            }
        }).done(function (data) {
            municipioSelect.empty();
            data.forEach(function (item) {
                municipioSelect.append($("<option>", {
                    value: item.municipio,
                    text: item.municipio
                }));
            });
        });
    }
});