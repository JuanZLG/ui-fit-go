
$(document).ready(function () {

    function reciboPedido() {
        let carritoLocal = JSON.parse(localStorage.getItem('carrito'));
        let html = '';
        let total = 0;

        if (carritoLocal) {
            for (let idProducto in carritoLocal) {
                let producto = carritoLocal[idProducto];
                let subtotal = Number(producto.precio.replace('$', '').replace(/,/g, '')) * producto.cantidad;
                total += subtotal;

                html += `
                <li class="p-3 d-flex position-relative" data-id="${idProducto}">
                    <div style="width:80%; margin:auto;">
                        <div class="d-flex justify-content-start gap-3">
                            <div class="d-flex align-items-center">
                                <img src="${producto.imgSrc}" id="img-producto" class="img-fluid" alt="Imagen" style="width:50px; height:50px; object-fit:cover;">
                            </div>
                            <div class="w-100"><span style="width: 110px; word-wrap: break-word;
                            overflow-wrap: break-word;"><strong>${producto.nombreProducto}x ${producto.sabor}</strong></span></div>
                        </div>
                        <div class="d-flex gap-2 justify-content-end m-1">
                            <span class="text-danger"><strong>${producto.precio} x ${producto.cantidad}</strong></span>
                        </div>
                    </div>
                </li>
                <hr class="m-0">
            `;
            }
        }

        document.getElementById('recibo-pedido').innerHTML = html;
        document.getElementById('total-recibo').textContent = "$" + total.toLocaleString();
    }

    reciboPedido();


    let carrito = JSON.parse(localStorage.getItem('carrito'));

    let htmlDesk = '';
    let htmlMobile = '';

    if (Object.keys(carrito).length === 0) {
        htmlDesk = '<p class="mt-2">No hay productos en el carrito, <a href="/Brutality/">agregar productos aquí.</a></p>';
        htmlMobile = htmlDesk;
    } else {
        for (let idProducto in carrito) {
            let producto = carrito[idProducto];
            let total = Number(producto.precio.replace('$', '').replace(/,/g, '')) * producto.cantidad;
            let precioUni = Number(producto.precio.replace('$', '').replace(/,/g, ''));

            htmlDesk += `
            <tr class="producto-row" data-id-producto="${idProducto}">
                <td class="p-2 ">
                    <div class="d-flex flex-wrap ">
                        <div class="cont-img d-flex align-items-center">
                            <img src="${producto.imgSrc}" id="img-producto" class="img-fluid"
                                alt="Imagen" style="width:70px; height:70px; object-fit: cover;">
                        </div>
                        <ul class="list-group">
                            <li class="list-group-item mt-2"><strong>${producto.nombreProducto}</strong></li>
                            <li class="list-group-item mt-2">
                                <span><strong class="mr-2">Sabor:</strong><span class="mx-2">${producto.sabor}</span></span>
                            </li>
                        </ul>
                    </div>
                </td>
                <td class="precio" style="vertical-align: middle !important;text-align:center;">$${precioUni.toLocaleString()}</td>
                <td style="vertical-align: middle !important;text-align:center;"> 
                    <span class="cantidad">
                        <div>
                            <div class="number-input">
                                <button type="button" class="decrement">-</button>
                                <input class="quantity" min="1" name="cantidad" value="${producto.cantidad}" type="number"
                                    autocomplete="off" step="1" id="cantidad-ingresada" max="100" required readonly
                                    oninput="this.value = this.value.replace(/[^0-9]/g, ''); if (this.value === '0') this.value = ''">
                                <button type="button" class="increment">+</button>
                            </div>
                        </div>
                    </span>
                </td>
                <td class="total_producto" style="vertical-align: middle !important;text-align:center;">$${total.toLocaleString()}</td>
                <td class="remove-order" style="cursor:pointer;vertical-align: middle !important;">
                    <span class="material-icons">delete</span>
                </td>
            </tr>
            `;

            htmlMobile += `
            <tr class="producto-row" data-id-producto="${idProducto}" style="vertical-align: middle !important;text-align:center;">
                <th>
                    <span>Producto</span>
                    <div class="remove-order" style="cursor:pointer;vertical-align: middle !important;">
                    <span class="material-icons">delete</span>
                    </div>
                </th>
                <th class="p-2">
                    <div class="d-flex align-items-center flex-wrap">
                        <div class="cont-img d-flex align-items-center ">
                            <img src="${producto.imgSrc}" id="img-producto" class="img-fluid"
                                alt="Imagen" style="width:70px; height:70px; object-fit: cover;">
                        </div>
                        <ul class="list-group">
                            <li class="list-group-item mt-2"><strong>${producto.nombreProducto}</strong></li>
                            <li class="list-group-item mt-2">
                                <span><strong class="mr-2">Sabor:</strong><span class="mx-2">${producto.sabor}</span></span>
                            </li>
                            <li class="list-group-item mt-2 precio" style="vertical-align: middle !important;text-align:center;"><strong>Precio Unitario: <strong>$${precioUni.toLocaleString()}</li>
                        </ul>
                    </div>
                </th>
            </tr>
            <tr style="vertical-align: middle !important;text-align:center;">
                <th class="price-column">Cantidad</th>
                <th class="cantidad mx-auto">
                    <div class="number-input">
                        <button type="button" class="decrement">-</button>
                        <input class="quantity" min="1" name="cantidad" value="${producto.cantidad}" type="number"
                        autocomplete="off" step="1" id="cantidad-ingresada" max="100" required readonly
                        oninput="this.value = this.value.replace(/[^0-9]/g, ''); if (this.value === '0') this.value = ''">
                        <button type="button" class="increment">+</button>
                    </div>
                </th>
            </tr>
            <tr style="vertical-align: middle !important;text-align:center; background-color:#ccc;">
                <th class="total-column">Total del Producto</th>
                <th class="total_producto text-danger" style="vertical-align: middle !important;text-align:center;">$${total.toLocaleString()}</th>
            </tr>
            <hr>
            `;
        }
    }

    // Asignar el HTML generado a las tablas correspondientes
    $('#producto-tbody-desk').html(htmlDesk);
    $('#producto-tbody-mobile').html(htmlMobile);





    $('.producto-row').each(function () {
        let row = $(this);
        let removeButton = row.find('.remove-order');

        removeButton.on('click', function () {
            let idProducto = row.data('id-producto');
            delete carrito[idProducto];
            localStorage.setItem('carrito', JSON.stringify(carrito));
            row.remove();
            location.reload();
        });
    });

    $('.list-item').on('click', '.remove-order', function () {
        location.reload();
    });

    function upListOrder() {
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
