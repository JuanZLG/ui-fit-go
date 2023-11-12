document.addEventListener("DOMContentLoaded", function () {
    let changeStateElements = document.querySelectorAll("[data-url-state]");
    let showDetailsElements = document.querySelectorAll("[data-url-details]");

    function formatearPrecios(valor) {
        valor = Math.round(valor * 100) / 100;
        let precioFormateado = valor.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return '$' + precioFormateado;
    }

    changeStateElements.forEach(function (element) {
        element.addEventListener("click", function () {
            let ventaId = element.getAttribute("data-venta-id");
            let nuevoEstado = element.getAttribute("data-nuevo-estado");
            let url = element.getAttribute("data-url-state");

            let mensaje;
            if (nuevoEstado === "0") {
                mensaje = "¿Esta seguro de desactivar esta venta? Esto marcará la venta como inactiva y devolverá al stock los productos relacionados. No podrá reactivarla nuevamente.";
            } else {
                mensaje = "¿Esta seguro de activar esta venta? Esto marcará la venta como activa y restará las cantidades al stock de los productos relacionados.";
            }

            Swal.fire({
                title: 'Estado',
                text: mensaje,
                showCancelButton: true,
                confirmButtonColor: '#419edd',
                cancelButtonColor: '#ba4d4d',
                confirmButtonText: 'Confirmar',
                cancelButtonText: 'Cancelar'
            }).then(function (result) {
                if (result.isConfirmed) {
                    $.ajax({
                        url: url,
                        data: {
                            venta_id: ventaId,
                            nuevo_estado: nuevoEstado
                        },
                        method: "GET",
                        success: function (response) {
                            location.reload();
                        },
                        error: function (error) {
                        }
                    });
                }
            });
        });
    });


    showDetailsElements.forEach(function (element) {
        element.addEventListener("click", function () {
            let venta_id = element.getAttribute("data-venta-id");
            let url = element.getAttribute("data-url-details");
            $.ajax({
                url: url,
                data: {
                    venta_id: venta_id
                },
                method: "GET",
                success: function (response) {
                    var venta = response.success;

                    Swal.fire({
                        html: `  
                            <div class="modal-container">
                                <h3 class="text-center">
                                    <div class="modal-state ${venta.estado == 1 ? 'activo' : 'inactivo'}"></div>
                                    <h2>Información de la Venta</h2>
                                </h3>
                                <div class="flex">
                                    <span>Documento: ${venta.documento} </span>
                                    <span>Fecha de venta: ${venta.fechareg}</span>
                                    <span>Cliente: ${venta.cliente}</span>
                                </div>
                                <table class="table modal-table">
                                    <h3 class="modal-subtitle text-start mt-3">Productos</h3>
                                    <thead class="text-center">
                                        <tr>
                                            <th>Producto</th>
                                            <th>Cantidad</th>
                                            <th>Precio Compra</th>
                                            <th>Precio Venta</th>
                                            <th>Descuentos</th>
                                            <th>Descuentos</th>
                                            <th>Total Producto</th>
                                        </tr>
                                    </thead>
                                    <tbody id="modalDetallesVenta">
                                        ${venta.detalles.map(detalle => `
                                            <tr>
                                                <td>${detalle.producto}</td>
                                                <td>${detalle.cantidad}</td>
                                                <td title="Precio de Compra">${formatearPrecios(detalle.precio_compra)}</td>
                                                <td title="Precio de venta">${formatearPrecios(detalle.precio_venta)}</td>
                                                <td>
                                                    <span title="Descuento">${detalle.descuento !== "0" ? detalle.descuento + '%' : 'No aplica'}</span>
                                                    <span title="Precio Descontado">${detalle.descuento !== "0" ? formatearPrecios(detalle.precio_descuento) : ''}</span>
                                                </td>
                                                <td>${detalle.ganancia}</td>
                                                <td>${detalle.precio_tot}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            <div class="modal-footer">
                                <span>Descuento de venta: 15%</span>
                                <span>Total con descuento: $76.50</span>
                                <span>Margen de ganancia: 44%</span>
                                <span class="font-weight-bold total-venta">TOTAL:<span>${formatearPrecios(venta.totalVenta)}</span></span>
                            <div>
                        </div>
                            `,
                        showCloseButton: true,
                        showConfirmButton: false,
                        customClass: {
                            closeButton: 'custom-close-button',
                            popup: 'custom-swal-popup'
                        }
                    })
                    let css = `
                            .custom-close-button { 
                                border: none !important; 
                                color: black !important; 
                            }
                            .custom-swal-popup {
                                max-width: 50% !important;
                                width: auto !important;
                            }
                            `,
                        head = document.head || document.getElementsByTagName('head')[0],
                        style = document.createElement('style');

                    head.appendChild(style);

                    style.type = 'text/css';
                    if (style.styleSheet) {
                        style.styleSheet.cssText = css;
                    } else {
                        style.appendChild(document.createTextNode(css));
                    }


                }
            });
        });

    });
});


