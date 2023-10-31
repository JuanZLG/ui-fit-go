document.addEventListener("DOMContentLoaded", function () {
    let changeStateElements = document.querySelectorAll("[data-url-state]");
    let showDetailsElements = document.querySelectorAll("[data-url-details]");

    function formatearPrecios(valor) {
        valor = Math.round(valor * 100) / 100;
        let precioFormateado = valor.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return '$ ' + precioFormateado;
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
                    console.log(venta)
                    $("#fechareg").text(venta.fechareg);
                    $("#cliente").text(venta.cliente);
                    $("#documento").text(venta.documento);
                    $("#totalVenta").text(formatearPrecios(venta.totalVenta));

                    if (venta.estado == 1) {
                        $(".estadoVentaCircle").addClass("activo").removeClass("inactivo");
                    } else {
                        $(".estadoVentaCircle").addClass("inactivo").removeClass("activo");
                    }
                    var detalles = venta.detalles;
                    let detallesVentaHTML = "";
                    for (let detalle of detalles) {
                        const precioUnitario = formatearPrecios(detalle.precio_uni);
                        const totalProducto = formatearPrecios(detalle.precio_tot);

                        detallesVentaHTML += `
                        <tr>
                            <td>${detalle.producto}</td>
                            <td>${precioUnitario}</td>
                            <td>${detalle.cantidad}</td>
                            <td>${totalProducto}</td> 
                        </tr>
                    `;
                    }
                    document.getElementById("modalDetallesVenta").innerHTML = detallesVentaHTML;


                    document.getElementById("verDetallesDialog").showModal();
                    $(".ventaDialog").addClass("fadeIn");
                    $(".modal-backdrop").show();
                    $(".modal-backdrop").addClass("fadeInBack");
                }
            });
        });

        $("#cerrarDetallesVenta").click(function () {
            $(".ventaDialog").addClass("fadeOut");
            $(".modal-backdrop").addClass("fadeOut");
            setTimeout(function () {
                document.getElementById("verDetallesDialog").close();
                $(".ventaDialog").removeClass("fadeOut");
                $(".modal-backdrop").hide();
                $(".modal-backdrop").removeClass("fadeOut");
            }, 300);
        });
    });
});


