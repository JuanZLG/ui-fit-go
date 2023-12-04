
$(document).ready(function () {


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


    let carrito = JSON.parse(localStorage.getItem('carrito'));

    let html = '';
    for (let idProducto in carrito) {
        let producto = carrito[idProducto];
        let total = Number(producto.precio.replace('$', '').replace(/,/g, '')) * producto.cantidad;
        let precioUni = Number(producto.precio.replace('$', '').replace(/,/g, ''));

        html += `
<tr class="producto-row" data-id-producto="${idProducto}">
    <td class="p-2 ">
        <div class="d-flex">
            <div class="cont-img">
                <img src="${producto.imgSrc}" id="img-producto" class="img-fluid"
                    alt="Imagen" style="width:70px; height:70px;">
            </div>
            <ul class="product-details">
                <li><strong class="">${producto.nombreProducto}</strong></li>
                <li>
                    <span><strong class="mr-2">Sabor:</strong><span class="mx-2">${producto.sabor}</span></span>
                </li>
                <li><strong class="mr-2">Presentación:</strong><span class="mx-2">${producto.presentacion} Libras</span>
                </li>
            </ul>
        </div>
    </td>
    <td class="precio">$${precioUni.toLocaleString()}</td>
    <td> <span class="cantidad">
            <div>
                <div class="number-input">
                    <button type="button" class="decrement">-</button>
                    <input class="quantity" min="1" name="cantidad" value="${producto.cantidad}" type="number"
                        autocomplete="off" step="1" id="cantidad-ingresada" max="100" required readonly
                        oninput="this.value = this.value.replace(/[^0-9]/g, ''); if (this.value === '0') this.value = ''">
                    <button type="button" class="increment">+</button>
                </div>
            </div>
    </td>
    <td class="total_producto">$${total.toLocaleString()}</td>
    <td class="remove-order">
        <i class="fas fa-trash" style="color: #000;"></i>
        x
    </td>
</tr>
`;
    }
    $('#producto-tbody').html(html);

    $('.producto-row').each(function () {
        let row = $(this);
        let removeButton = row.find('.remove-order');

        removeButton.on('click', function () {
            let idProducto = row.data('id-producto');
            delete carrito[idProducto];
            localStorage.setItem('carrito', JSON.stringify(carrito));
            row.remove();
            upListOrder()
            actualizarCantidadProductos();
        });
    });

    $('.list-item').on('click', '.remove-order', function () {
        location.reload();
    });

    function upListOrder() {
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
    }

    
    $('.producto-row').each(function () {
        let row = $(this);
        let input = row.find('.quantity');
        let precioUni = Number(row.find('.precio').text().replace('$', '').replace(/,/g, ''));
        let totalProducto = row.find('.total_producto');
    
        input.on('input', function () {
            let cantidad = input.val();
            let idProducto = row.data('id-producto');
            carrito[idProducto].cantidad = cantidad;
            localStorage.setItem('carrito', JSON.stringify(carrito));
            let total = precioUni * cantidad;
            totalProducto.text('$' + total.toFixed(3).replace(/\d(?=(\d{3})+\.)/g, '$&,'));
            upListOrder()
        });
    });
    
    
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
});
