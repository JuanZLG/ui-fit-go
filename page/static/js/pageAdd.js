$(document).ready(function () {
    let carrito = localStorage.getItem('carrito') ? JSON.parse(localStorage.getItem('carrito')) : {};

    $('.item-order').parent().mouseenter(function () {
        $(this).find('.item-order').next().find('.list-order').addClass('show');
    });

    $('.item-order').parent().mouseleave(function () {
        $(this).find('.item-order').next().find('.list-order').removeClass('show');
    });

    function actualizarCantidadProductos() {
        let carrito = JSON.parse(localStorage.getItem('carrito'));
        let orderCant = document.querySelector('.order-cant');

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

    
    let html = '';
    for (let idProducto in carrito) {
        let producto = carrito[idProducto];

        html += `
            <li class="p-3 d-flex position-relative" data-id="${idProducto}">
                <div style="width:95%;">
                    <div class="d-flex justify-content-start gap-3">
                        <img src="${producto.imgSrc}" id="img-producto" class="img-fluid" alt="Imagen" style="width:50px; height:50px;">
                        <span style="width: 110px">${producto.nombreProducto}</span>
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

});
