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


    let html = '';
    for (let idProducto in carrito) {
        let producto = carrito[idProducto];

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

    $('.list-item').on('click', '.remove-order', function () {
        let idProducto = $(this).parent().attr('data-id');

        delete carrito[idProducto];
        localStorage.setItem('carrito', JSON.stringify(carrito));
        $(this).parent().next().remove();
        $(this).parent().remove();
        actualizarCantidadProductos();
    });



    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {

            let imgSrc = document.getElementById('img-producto').src;
            let nombreProducto = document.getElementById('producto').textContent.trim();
            let precio = document.getElementById('precio').textContent.trim();
            let sabor = document.querySelector('select[name="sabor"]').value;
            let presentacion = document.querySelector('select[name="presentacion"]').value;
            let cantidad = document.querySelector('input[name="cantidad"]').value;

            let idProducto = this.dataset.id;

            let producto = {
                imgSrc: imgSrc,
                nombreProducto: nombreProducto,
                precio: precio,
                sabor: sabor,
                presentacion: presentacion,
                cantidad: cantidad
            };

            carrito[idProducto] = producto;

            localStorage.setItem('carrito', JSON.stringify(carrito));

            actualizarCantidadProductos();

            alert('Datos guardados exitosamente!');
        });
    });


});
