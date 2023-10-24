document.addEventListener("DOMContentLoaded", function () {

    $("#nombreCliente").on("input", function () {
        let nombreCliente = $(this).val();
        $("#resultado-cliente").show();
        $("#cont-docu").empty()
        $("#nombreCliente").removeClass("is-valid")

        let tablaClientes = $("#resultado-cliente");

        $("#error-docu").text("");

        if (nombreCliente.length >= 3) {
            let buscarClienteUrl = document.getElementById("nombreCliente").getAttribute("data-url-cliente");
            let url = buscarClienteUrl + "?q=" + nombreCliente;
            $.ajax({
                url: url,
                type: "GET",
                success: function (data) {
                    if (data.resultados.length > 0) {
                        tablaClientes.empty();

                        for (let i = 0; i < Math.min(4, data.resultados.length); i++) {
                            let documento = data.resultados[i].documento;
                            let nomClienteDato = data.resultados[i].nombre_cliente;
                            let estadoCliente = data.resultados[i].estado;

                            let estadoClass = estadoCliente === 1 ? "activo" : "inactivo";

                            let filaHtml = `
                        <div class="cliente-item ${estadoClass}"> 
                            <div class="cliente-info">
                                <div class="estadoClienteCircle ${estadoClass}"></div>
                                <span id="nombreDato">${nomClienteDato}</span>
                            </div>
                            <div class="identificacion">Identificación: <span id="documentoDato">${documento}</span></div>
                        </div>`;

                            tablaClientes.append(filaHtml);
                        }

                        setTimeout(function () {
                            tablaClientes.css("opacity", "1");
                        }, 100);
                    } else {
                        tablaClientes.empty();
                    }
                },
                error: function () {
                    $("#nombreCliente").addClass("is-invalid");
                },
            });
        } else {
            tablaClientes.css("opacity", "0");
            tablaClientes.empty();
            $("#nombreCliente").removeClass("is-valid is-invalid");
        }

        tablaClientes.on("click", ".cliente-item", function () {
            if (!$(this).hasClass("inactivo")) {
                let nombreApellido = $(this).find("#nombreDato").text();
                let documento = $(this).find("#documentoDato").text();
                $("#error-docu").text("")
                let identificacionCompleta = `Identificación: <span id="documento">${documento}</span>`;
                $("#cont-docu").html(identificacionCompleta);

                $("#nombreCliente").val(nombreApellido).addClass("is-valid");
                $("#resultado-cliente").hide();
            }
        });
    });




    $(document).on("input", ".producto", function () {
        let producto = $(this).val();
        let currentRow = $(this).closest("tr");
        let suggestions = currentRow.find(".resultado-producto");
        urlValidar = $(this).data("url-validar");
        urlPrecio = $(this).data("url-precio");
        urlCantidad = $(this).data("url-cantidad");

        if (producto.length >= 3) {
            let buscarProductoUrl = $(this).data("url-producto");
            let url = buscarProductoUrl + "?q=" + producto;
            $.ajax({
                url: url,
                type: "GET",
                success: function (data) {
                    suggestions.empty();

                    if (data.productos.length > 0) {
                        data.productos.forEach(function (producto) {
                            let $sugerencia = $("<span class='resultado-sugerencia'></span>");
                            $sugerencia.text(producto.nombre_producto);
                            suggestions.append($sugerencia);

                            if (producto.estado === 0) {
                                $sugerencia.addClass("sugerencia-inhabilitado");
                            }
                        });

                        suggestions.addClass("sugerencia").show();
                    } else {
                        suggestions.hide();
                        calcularTotalVenta();
                    }

                    setTimeout(function () {
                        suggestions.css("opacity", "1");
                    }, 0);

                    validarProducto(currentRow, producto);
                },
                error: function () {
                    suggestions.empty().hide();
                },
            });
        } else {
            suggestions.empty().hide();
        }
    });

    function validarProducto(currentRow, nombreProducto) {
        $.ajax({
            url: urlValidar,
            type: "GET",
            data: {
                nombre_producto: nombreProducto,
            },
            success: function (data) {
                if (data.existe) {
                    obtenerPrecioProducto(currentRow, nombreProducto);
                } else {
                    currentRow.find(".cantidad, .precioTotal, .precioUnidad").val("");
                    calcularTotalVenta();
                }
            },
            error: function () {
                currentRow.find(".cantidad, .precioTotal").val("");
                calcularTotalVenta();
            },
        });
    }

    $(document).on("click", function (event) {
        if (!$(event.target).closest(".producto").length && !$(event.target).closest(".resultado-producto").length) {
            $(".resultado-producto").empty().hide();
        }
    });

    $(document).on("click", ".resultado-producto span.resultado-sugerencia", function () {
        let currentRow = $(this).closest("tr");
        let nombreProducto = $(this).text();
        nombreProducto = nombreProducto.charAt(0).toUpperCase() + nombreProducto.slice(1).toLowerCase();
        currentRow.find(".producto").val(nombreProducto);
        validarProducto(currentRow, nombreProducto);
    });

    $(document).on("click", ".resultado-sugerencia", function () {
        let currentRow = $(this).closest("tr");
        let nombreProducto = $(this).text();
        nombreProducto = nombreProducto.charAt(0).toUpperCase() + nombreProducto.slice(1).toLowerCase();
        currentRow.find(".producto").val(nombreProducto);
        currentRow.find(".resultado-producto").empty().hide();
        currentRow.find(".precioUnidad").removeClass("is-invalid");
    });





    $(document).on("input", ".producto", function () {
        let currentRow = $(this).closest("tr");
        let nombreProducto = $(this).val();
        currentRow.find(".producto-error").text("");
        currentRow.find(".producto").removeClass("is-invalid");
        currentRow.find(".cantidad").removeClass("is-invalid");
        currentRow.find(".error-cantidad").text("");
        if (nombreProducto.length >= 2) {
            validarProducto(currentRow, nombreProducto);
        } else {
            currentRow.find(".cantidad, .precioTotal, .precioUnidad").val("");
            calcularTotalVenta();
        }
    });



    function formatearPrecios(valor) {
        valor = Math.round(valor * 100) / 100;
        let precioFormateado = valor.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return '$ ' + precioFormateado;
    }

    function obtenerPrecioProducto(currentRow, nombreProducto) {
        $.ajax({
            url: urlPrecio,
            type: "GET",
            data: {
                nombre_producto: nombreProducto,
            },
            success: function (data) {
                if ("precio" in data) {
                    let precioUValue = parseFloat(data.precio)
                    let precioTotalFormatted = formatearPrecios(precioUValue);
                    let precioU = currentRow.find(".precioUnidad").val(precioTotalFormatted);
                }
                else {
                    currentRow.find(".precioUnidad").addClass("is-invalid");
                }
            },
            error: function () {
                currentRow.find(".cantidad, .precioTotal").val("");
            },
        });
    }
    $(document).ready(function () {
        $(".precioTotal").val("");
        $(".precioUnidad").val("");
        $("#totalVenta").val("");
    });

    $(document).on("input", ".cantidad", function () {
        calcularTotalProducto($(this));
    });
    function calcularTotalProducto(inputCantidad) {
        let currentRow = inputCantidad.closest("tr");
        let precioUnidad = parseFloat(currentRow.find(".precioUnidad").val().replace(/[$,.]/g, ''));

        let cantidad = parseInt(inputCantidad.val());

        if (!isNaN(precioUnidad) && !isNaN(cantidad)) {
            let total = precioUnidad * cantidad;
            let formateoTotal = formatearPrecios(total)
            currentRow.find(".precioTotal").val(formateoTotal);
            calcularTotalVenta();
        } else {
            currentRow.find(".precioTotal").val("");
            calcularTotalVenta();
        }
    }

    $(document).on("click", ".eliminar-producto", function () {
        currentRow = $(this).closest("tr.producto-row").remove();
        calcularTotalVenta();
    });
});


// $("#agregar-producto").on("click", function () {
//     let nuevaFila =
//         '<tr class="producto-row">' +
//         '    <td class="p-2 celda-producto">' +
//         '        <input type="text" class="form-control producto" name="producto" id="producto" autocomplete="off" placeholder="Nombre del producto" data-url-producto="{% url \'buscar_productos\' %}" data-url-validar="{% url \'validar_producto\' %}" data-url-precio="{% url \'obtener_precio_producto\' %}">' +
//         '        <span class="text-danger producto-error"></span>' +
//         '        <div class="p-2 resultado-producto"></div>' +
//         '    </td>' +
//         '    <td>' +
//         '        <div class="form-group">' +
//         '            <input type="text" class="form-control precioUnidad" id="precioUnidad" name="precioUnidad" readonly data-url-cantidad="{% url \'validar_cantidad\' %}">' +
//         '        </div>' +
//         '    </td>' +
//         '    <td>' +
//         '        <input type="number" class="form-control cantidad p-0 text-center" id="cantidad" name="cantidad" autocomplete="off" min="1" step="1" oninput="this.value = this.value.replace(/[^0-9]/g, \'\'); if (this.value === \'0\') this.value = \'\';" placeholder="Cantidad">' +
//         '        <span class="text-danger error-cantidad"></span>' +
//         '    </td>' +
//         '    <td>' +
//         '        <div class="form-group">' +
//         '            <input type="text" class="form-control precioTotal" id="precioTotal" name="precioTotal" readonly>' +
//         '        </div>' +
//         '    </td>' +
//         '<td class="eliminar-producto"><span class="icono-eliminar">X</span></td>' +
//         '</tr>';
//     let filaAgregada = $(nuevaFila);
//     $("tbody").append(filaAgregada);

//     inicializarSugerenciasEnFila(filaAgregada);
// });


// function inicializarSugerenciasEnFila(fila) {
//     fila
//         .find(".resultado-producto");
// }

function calcularTotalVenta() {
    let totalVenta = 0;

    $(".producto-row").each(function () {
        let precioTotal = parseFloat($(this).find(".precioTotal").val().replace(/[$,.]/g, ''));
        if (!isNaN(precioTotal)) {
            totalVenta += precioTotal;
        }
    });

    let formateoTotalVenta = formatearPrecios(totalVenta)
    $("#totalVenta").val(formateoTotalVenta);
}


function validarCantidad() {
    const cantidad = parseInt($(this).val());
    const nombreProducto = $(this).closest("tr.producto-row").find(".producto").val();

    return new Promise(function (resolve, reject) {
        $.ajax({
            url: urlCantidad,
            type: "GET",
            data: {
                cantidad: cantidad,
                nombre: nombreProducto,
            },
            success: function (data) {
                if (data.suficiente) {
                    resolve(true);
                } else {
                    resolve(false);
                }
            },
            error: function () {
                reject(new Error("Error al validar la cantidad"));
            },
        });
    });
}

function validarCamposLlenos() {
    let camposLlenos = true;
    const documentoValue = $("#documento").text();
    const totalVentaValue = parseFloat($("#totalVenta").val().replace(/[$,.]/g, '')).toFixed(2);
    const nombreClienteValue = $("#nombreCliente").val();
    const productos = [];
    const productoNombres = {};

    if (!nombreClienteValue) {
        $("#error-docu").text(
            "Este campo es obligatorio."
        );
        camposLlenos = false;
    } else if (!documentoValue) {
        $("#error-docu").text(
            "Por favor, asegúrese de seleccionar un cliente antes de continuar."
        );
        camposLlenos = false;
    }

    $(".producto-row").each(function (index) {
        const row = $(this);
        const productoInput = row.find(".producto");
        const cantidadInput = row.find(".cantidad");
        const precioUnidad = row.find(".precioUnidad").val();
        const precioUnidadInput = row.find(".precioUnidad");
        const precioTotalInput = row.find(".precioTotal");

        const productoValue = productoInput.val().toLowerCase();
        const precioUnidadValue = parseFloat(precioUnidadInput.val().replace(/[$,.]/g, '')).toFixed(2);
        const precioTotalValue = parseFloat(precioTotalInput.val().replace(/[$,.]/g, '')).toFixed(2);
        const cantidadValue = parseInt(cantidadInput.val());

        if (isNaN(precioUnidadValue)) {
            row.find(".producto-error").text("El campo producto debe estar correctamente escrito.");
            camposLlenos = false;
        }
        if (!productoValue) {
            row.find(".producto-error ").text("Este campo es obligatorio.");
            camposLlenos = false;
        }

        if (!cantidadValue) {
            mostrarError(cantidadInput);
            camposLlenos = false;
        }
        if ($(".error-cantidad").text() !== "") {
            camposLlenos = false;
        }

        if (productoValue && productoNombres[productoValue]) {
            row
                .find(".producto-error")
                .text("Este producto ya ha sido seleccionado anteriormente.");
            camposLlenos = false;
        } else if (productoValue) {
            productoInput.removeClass("is-invalid");
            productos.push({
                nombre: productoValue,
                precioUnidad: precioUnidadValue,
                precioTotal: precioTotalValue,
                cantidad: cantidadValue
            });
            productoNombres[productoValue] = true;
        }
    });
    return camposLlenos
        ? { documento: documentoValue, totalVenta: totalVentaValue, productos: productos }
        : null;
}



function mostrarError(selector) {
    $(selector).addClass("is-invalid");
    $("#nombreCliente, .producto, .cantidad").on("input", function () {
        const campo = $(this);
        if (campo.val()) {
            campo.removeClass("is-invalid");
        }
    });
}



$('#venta-form').submit(function (event) {
    event.preventDefault();
    const data = validarCamposLlenos();
    if (!data) {
        return;
    } else {
        enviarDatosVentas(data);
    }
});

$(document).on('input', '.cantidad', function () {
    const $this = $(this);
    const fila = $this.closest("tr.producto-row");
    validarCantidad.call(this).then(function (suficiente) {
        if (suficiente) {
            $this.removeClass("is-invalid");
            fila.find(".error-cantidad").text("");
        } else {
            $this.addClass("is-invalid");
            fila.find(".error-cantidad").text("Supera el stock mínimo.").css("color", "red");
        }
    });
});



function enviarDatosVentas(data) {
    let url = document.querySelector(".btn-crear").getAttribute("data-url-crear");
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (response) {
            if (response.success) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'Venta creada con éxito',
                    icon: 'success',
                    showConfirmButton: false,
                    timer: 2000,
                });
                setTimeout(function () {
                    // window.location.href = "{% url 'ventas' %}";
                    alert(2)
                }, 2000);
            }
        },
    });
}
