document.addEventListener("DOMContentLoaded", function () {
    let changeStateElements = document.querySelectorAll("[data-url-state]");
    let showDetailsElements = document.querySelectorAll("[data-url-details]");

    function formatearPrecios(valor) {
        valor = parseFloat(valor);
        if (!isNaN(valor)) {
            valor = Math.round(valor * 100) / 100;
            let precioFormateado = valor.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            return '$' + precioFormateado;
        } 
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
                            $('.table-responsive').addClass('animate__animated animate__fadeOut').css('animation-duration', '100');
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
                                <div class="modal-state ${venta.estado == 1 ? 'activo' : 'inactivo'}"></div>
                                <h2>Información de la Venta</h2>
                                <div class="flex">
                                    <span><strong class="me-2">Documento:</strong>${venta.documento} </span>
                                    <span><strong class="me-2">Fecha de venta:</strong>${venta.fechareg}</span>
                                    <span><strong class="me-2">Cliente:</strong>${venta.cliente}</span>
                                </div>
                                <table class="table modal-table">
                                    <h3 class="modal-subtitle text-start mt-3">Detalles</h3>
                                    <thead class="text-center">
                                        <tr>
                                            <th>Producto</th>
                                            <th>Cantidad</th>
                                            <th>Precio Compra</th>
                                            <th>Precio Venta</th>
                                            <th>Descuentos</th>
                                            <th>Ganancia</th>
                                            <th>Total Producto</th>
                                        </tr>
                                    </thead>
                                    <tbody id="modalDetallesVenta">
                                        ${venta.detalles.map(detalle => `
                                            <tr>
                                                <td style="text-align:start; width:50px;">${detalle.producto}</td>
                                                <td>${detalle.cantidad}</td>
                                                <td>${formatearPrecios(detalle.precio_compra)}</td>
                                                <td>${formatearPrecios(detalle.precio_venta)}</td>
                                                <td>
                                                    <span title="Descuento">${detalle.descuento !== "0" ? detalle.descuento + '%' : 'No aplica'}</span>
                                                    <span title="Precio Descontado">${detalle.descuento !== "0" ? formatearPrecios(detalle.precio_descuento) : ''}</span>
                                                </td>
                                                <td>${formatearPrecios(detalle.ganancia)}</td>
                                                <td>${formatearPrecios(detalle.precio_tot)}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            <div class="modal-footer">
                                <div>
                                    <span><strong class="me-2">Descuento de venta:</strong></span>
                                    <span>${venta.descuentoVenta !== "0" ? venta.descuentoVenta + '%' : 'No aplica'}</span>
                                </div>
                                <div>
                                    <span><strong class="me-2">Total descontado:</strong></span>
                                    <span>${venta.descuentoVenta !== "0" ? formatearPrecios(venta.totalVentaDescuento) : "$0"}</span>
                                </div>
                                <div>
                                    <span><strong class="me-2">Margen de ganancia:</strong></span>
                                    <span>${formatearPrecios(venta.margenGanancia)}</span>
                                </div>
                                <div class="font-weight-bold total-venta mt-2 p-2" style="border-top: 2px dotted #ccc">
                                    <span>TOTAL:</span>
                                    <span class="mx-2">${formatearPrecios(venta.totalVenta)}</span>
                                </div>
                            </div>
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


