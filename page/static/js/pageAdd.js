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

    /* LOCAL STORAGE --------------------------------------------  */

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
        } else {
            carrito = {};
        }

        let html = '';
        let total = 0;

        for (let idProducto in carrito) {
            let producto = carrito[idProducto];
            let subtotal = Number(producto.precio.replace('$', '').replace(/,/g, '')) * producto.cantidad;
            total += subtotal;

            html += `
                <li class="p-3 d-flex position-relative" data-id="${idProducto}">
                    <div style="width:95%;">
                        <div class="d-flex justify-content-start gap-3">
                            <img src="${producto.imgSrc}" id="img-producto" class="img-fluid" alt="Imagen" style="width:50px; height:50px;">
                            <span style="width: 110px; word-wrap: break-word;
                            overflow-wrap: break-word;">${producto.nombreProducto}</span>
                        </div>
                        <div class="d-flex gap-2 justify-content-end m-1">
                            <span><strong>${producto.precio} x ${producto.cantidad}</strong></span>
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


    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Evitar que el formulario se envíe

            let imgSrc = document.getElementById('img-producto').src;
            let nombreProducto = document.getElementById('producto').textContent.trim();
            let precio = document.getElementById('precio').textContent.trim();
            let sabor = document.querySelector('select[name="sabor"]').value;
            let presentacion = document.querySelector('select[name="presentacion"]').value;
            let cantidad = parseInt(document.querySelector('input[name="cantidad"]').value);

            let idProducto = this.dataset.id;

            let carrito = JSON.parse(localStorage.getItem('carrito')) || {};

            // Generar un ID único numérico para el producto
            let idPedido = generarIdUnico(nombreProducto, sabor, presentacion);

            // Verificar si el producto ya existe en el carrito
            if (carrito[idPedido] && carrito[idPedido].nombreProducto === nombreProducto && carrito[idPedido].sabor === sabor && carrito[idPedido].presentacion === presentacion) {
                carrito[idPedido].cantidad += cantidad;
            } else {
                carrito[idPedido] = {
                    idDelProducto: idProducto, 
                    imgSrc: imgSrc,
                    nombreProducto: nombreProducto,
                    precio: precio,
                    sabor: sabor,
                    presentacion: presentacion,
                    cantidad: cantidad
                };
            }

            localStorage.setItem('carrito', JSON.stringify(carrito));

            actualizarCantidadProductos(); // Asegúrate de que esta función esté definida

            alert('Datos guardados exitosamente!');
        });
    });

    // Función para generar un ID único numérico basado en el nombre, sabor y presentación del producto
    function generarIdUnico(nombre, sabor, presentacion) {
        let hash = 0;
        let identificador = nombre + sabor + presentacion;
        for (let i = 0; i < identificador.length; i++) {
            let char = identificador.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash |= 0; // Convertir a entero de 32 bits
        }
        return Math.abs(hash); // Asegurarse de que el ID sea positivo
    }


    // Función para generar un ID único numérico basado en el nombre, sabor y presentación del producto
    function generarIdUnico(nombre, sabor, presentacion) {
        let hash = 0;
        let identificador = nombre + sabor + presentacion;
        for (let i = 0; i < identificador.length; i++) {
            let char = identificador.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash |= 0; // Convertir a entero de 32 bits
        }
        return Math.abs(hash); // Asegurarse de que el ID sea positivo
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
