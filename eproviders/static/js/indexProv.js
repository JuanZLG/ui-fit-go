document.addEventListener("DOMContentLoaded", function () {
    let changeStateElements = document.querySelectorAll("[data-url-state]");
    let showDetailsElements = document.querySelectorAll("[data-url-details]");

    changeStateElements.forEach(function (element) {
        element.addEventListener("click", function () {
            let proveedorId = element.getAttribute("data-proveedor-id");
            let nuevoEstado = element.getAttribute("data-nuevo-estado");
            let url = element.getAttribute("data-url-state");

            Swal.fire({
                title: 'Estado',
                text: '¿Desea cambiar el estado de este proveedor?',
                showCancelButton: true,
                confirmButtonColor: '#419edd',
                cancelButtonColor: '#ba4d4d',
                confirmButtonText: 'Confirmar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    $.ajax({
                        url: url,
                        data: {
                            proveedor_id: proveedorId,
                            nuevo_estado: nuevoEstado
                        },
                        method: "GET",
                        success: function (response) {
                            location.reload();
                        }
                    });
                }
            });
        });
    });

    showDetailsElements.forEach(function (element) {
        element.addEventListener("click", function () {
            let proveedorId = element.getAttribute("data-prov-id");
            let url = element.getAttribute("data-url-details");
    
            $.ajax({
                url: url,
                data: {
                    proveedor_id: proveedorId
                },
                method: "GET",
                success: function (response) {
                    var proveedor = response.success;
                    let identificacionRow = proveedor.identificacion !== "" ? `<span><strong>Identificación:</strong>${proveedor.tipo} ${proveedor.identificacion}</span>` : "";
                    let direccionRow = proveedor.direccion !== "" ? `<strong>Dirección:</strong><span id="direccion">${proveedor.direccion}</span>` : "";
                    let informacionRow = proveedor.informacion !== "" ? `<strong>Información Adicional :</strong><p>${proveedor.informacion}</p>` : "";
                    let estadoProveedorCircle = proveedor.estado == 1 ? "activo" : "inactivo";
                    Swal.fire({
                        html: `
                        <div class="modal-container">
                            <div class="modal-state ${estadoProveedorCircle}"></div>
                            <h2>Información del Proveedor</h2>
                            <div class="modal-header flex">
                                ${identificacionRow ? `${identificacionRow}` : ""}
                                <span><strong>Proveedor:</strong>${proveedor.nombre_proveedor}</span></span>
                            </div>
                            <div class="modal-body flex">
                                <span><strong>Correo:</strong>${proveedor.correo}</span>
                                <span><strong>Teléfono:</strong>${proveedor.telefono} </span>
                            </div>
                            <div class="modal-footer">
                                ${direccionRow ? ` <span>${direccionRow}</span>` : ""}
                                ${informacionRow ? `<p class="modal-info">${informacionRow}</p>` : ""}
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
                },
            });
        });
    });
});