
// $(document).ready(function () {
//     $("#nombreCliente").on("input", function () {
//         let input = $(this).val();
//         let resultadoDocu = $("#cont-docu");

//         if (input.length == 8 || input.length == 10) {
//             $.ajax({
//                 url: "{% url 'buscar_documentos' %}?q=" + input,
//                 type: "GET",
//                 success: function (data) {
//                     let documento = data.documentos[0];
//                     let nomClienteDato = data.nombre_cliente;

//                     if (data.documentos.length > 0) {
//                         validarCliente(documento).then(function (existe) {
//                             if (existe && documento === input) {
//                                 resultadoDocu.html(
//                                     "<p id='nomClienteDato'>" +
//                                     nomClienteDato +
//                                     "</p><span>Doc:</span><p id='documentoDato'>" +
//                                     documento +
//                                     "</p>"
//                                 );
//                                 $("#nombreCliente").addClass("is-valid");
//                             } else {
//                                 resultadoDocu.empty();
//                             }
//                         });
//                     } else {
//                         resultadoDocu.hide();
//                     }
//                 },
//                 error: function () {
//                     $("#nombreCliente").addClass("is-invalid");
//                 },
//             });
//         } else {
//             resultadoDocu.empty().hide(); // Limpiar y ocultar cont-docu
//             $("#nombreCliente").removeClass("is-valid is-invalid"); // Remover clases de validación
//         }
//     });

//     function validarCliente(documentoDato) {
//         return new Promise(function (resolve, reject) {
//             $.ajax({
//                 url: "{% url 'validar_cliente' %}",
//                 type: "GET",
//                 data: {
//                     documentoDato: documentoDato,
//                 },
//                 success: function (data) {
//                     if (data.existe) {
//                         resolve(true);
//                     } else {
//                         resolve(false);
//                     }
//                 },
//                 error: function () {
//                     reject(new Error("Error al validar el cliente"));
//                 },
//             });
//         });
//     }

//     /********** PRODUCTO ***********/
//     $(".mess-sugges-prod").after('<div class="producto-suggestions"></div>');
//     $(document).on("input", ".producto", function () {
//         let input = $(this).val();
//         if (input.length >= 4) {
//             let currentRow = $(this).closest("tr");
//             $.ajax({
//                 url: "{% url 'buscar_productos' %}?q=" + input,
//                 type: "GET",
//                 success: function (data) {
//                     let suggestions = currentRow.find(".producto-suggestions");
//                     suggestions.empty();
//                     data.productos = data.productos.map((producto) =>
//                         producto.toUpperCase()
//                     );
//                     if (data.productos.length > 0) {
//                         let producSimilar1 = data.productos[0];
//                         let producSimilar2 = data.productos[1];
//                         let producSimilar3 = data.productos[2];
//                         suggestions.html(
//                             "<span class='resultado-sugerencia'>" + producSimilar1
//                         );
//                         if (data.productos.length > 1) {
//                             suggestions.append(
//                                 "<span class='resultado-sugerencia'>" +
//                                 producSimilar2 +
//                                 "</span>"
//                             );
//                         }
//                         if (data.productos.length > 2) {
//                             suggestions.append(
//                                 "<span class='resultado-sugerencia'>" +
//                                 producSimilar3 +
//                                 "</span>"
//                             );
//                         }

//                         suggestions.addClass("sugerencia").show();
//                     } else {
//                         suggestions.hide();
//                         calcularTotalVenta()
//                     }
//                 },
//                 error: function () {
//                     currentRow.find(".producto-suggestions").empty().hide();
//                 },
//             });
//         } else {
//             $(this).closest("tr").find(".producto-suggestions").empty().hide();
//         }
//     });

//     $(document).on("click", function (event) {
//         if (
//             !$(event.target).closest(".producto").length &&
//             !$(event.target).closest(".producto-suggestions").length
//         ) {
//             $(".producto-suggestions").empty().hide();
//         }
//     });

//     $(document).on(
//         "click",
//         ".producto-suggestions span.resultado-sugerencia",
//         function () {
//             let currentRow = $(this).closest("tr");
//             let nombreProducto = $(this).text();
//             nombreProducto =
//                 nombreProducto.charAt(0).toUpperCase() +
//                 nombreProducto.slice(1).toLowerCase();
//             currentRow.find(".producto").val(nombreProducto);

//             validarProducto(currentRow, nombreProducto);
//         }
//     );

//     $(document).on("click", ".producto-suggestions span", function () {
//         let currentRow = $(this).closest("tr");
//         let nombreProducto = $(this).text();
//         nombreProducto =
//             nombreProducto.charAt(0).toUpperCase() +
//             nombreProducto.slice(1).toLowerCase();
//         currentRow.find(".producto").val(nombreProducto);
//         currentRow.find(".producto-suggestions").empty().hide();
//         currentRow.find(".precioUnidad").removeClass("is-invalid");
//     });

//     /********** PRECIOS ***********/
//     $(document).on("input", ".producto", function () {
//         let currentRow = $(this).closest("tr");
//         let nombreProducto = $(this).val();
//         currentRow.find(".error-produ").text("");
//         if (nombreProducto.length >= 3) {
//             // Validar el producto antes de obtener el precio
//             validarProducto(currentRow, nombreProducto);
//         } else {
//             currentRow.find(".cantidad, .precioTotal, .precioUnidad").val("");
//             calcularTotalVenta();
//         }
//     });

//     function validarProducto(currentRow, nombreProducto) {
//         $.ajax({
//             url: "{% url 'validar_producto' %}",
//             type: "GET",
//             data: {
//                 nombre_producto: nombreProducto,
//             },
//             success: function (data) {
//                 if (data.existe) {
//                     obtenerPrecioProducto(currentRow, nombreProducto);
//                 } else {
//                     currentRow.find(".cantidad, .precioTotal, .precioUnidad").val("");
//                     calcularTotalVenta();
//                 }
//             },
//             error: function () {
//                 currentRow.find(".cantidad, .precioTotal").val("");
//                 calcularTotalVenta();
//             },
//         });
//     }

//     function obtenerPrecioProducto(currentRow, nombreProducto) {
//         $.ajax({
//             url: "{% url 'obtener_precio_producto' %}",
//             type: "GET",
//             data: {
//                 nombre_producto: nombreProducto,
//             },
//             success: function (data) {
//                 if ("precio" in data) {
//                     let precioUValue = parseInt(data.precio).toLocaleString();
//                     let precioTotalFormatted = "$ " + precioUValue;
//                     let precioU = currentRow.find(".precioUnidad").val(precioTotalFormatted);

//                 } else {
//                     currentRow.find(".precioUnidad").addClass("is-invalid");
//                 }
//             },
//             error: function () {
//                 currentRow.find(".cantidad, .precioTotal").val("");
//             },
//         });
//     }
//     $(document).ready(function () {
//         $(".precioTotal").val("");
//         $(".precioUnidad").val("");
//         $("#totalVenta").val("");
//     });

//     $(document).on("input", ".cantidad", function () {
//         calcularTotalProducto($(this));
//     });
//     function calcularTotalProducto(inputCantidad) {
//         let currentRow = inputCantidad.closest("tr");
//         let precioUnidad = currentRow.find(".precioUnidad").val().replace(/[^\d.-]/g, '');
//         let cantidad = parseInt(inputCantidad.val());

//         if (!isNaN(precioUnidad) && !isNaN(cantidad)) {
//             let total = precioUnidad * cantidad;
//             let totalProductoFormateado = total.toLocaleString();
//             currentRow.find(".precioTotal").val("$ " + totalProductoFormateado);
//             calcularTotalVenta();
//         } else {
//             currentRow.find(".precioTotal").val("");
//             calcularTotalVenta();
//         }
//     }

//     $(document).on("click", ".eliminar-producto", function () {
//         currentRow = $(this).closest("tr.producto-row").remove();
//         calcularTotalVenta();
//     });

//     $("#agregar-producto").on("click", function () {
//         let nuevaFila =
//             '<tr class="producto-row">' +
//             "<td>" +
//             '<input type="text" class="form-control producto" name="producto" id="producto" autocomplete="off" placeholder="Nombre del producto">' +
//             '<span class="error-message text-danger error-produ" ></span>' +
//             '<div class="p-2">' +
//             '<label class="text-secondary me-2 mess-sugges-prod">Sugerencias:</label>' +
//             "</div>" +
//             '<span class="error-message producto-error"></span>' +
//             "</td>" +
//             "<td>" +
//             '<div class="form-group">' +
//             '<input type="text" class="form-control precioUnidad" id="precioUnidad" name="precioUnidad" readonly>' +
//             '<span class="error-message" id="precioU-error"></span>' +
//             "</div>" +
//             "</td>" +
//             "<td>" +
//             '<div class="form-group">' +
//             '<input type="number" class="form-control cantidad" id="cantidad" name="cantidad" autocomplete="off" min="1" oninput="this.value = this.value.replace(/[^0-9]/g, \'\');" placeholder="Cantidad">' +
//             "</div>" +
//             "</td>" +
//             "<td>" +
//             '<div class="form-group">' +
//             '<input type="text" class="form-control precioTotal" id="precioTotal" name="precioTotal" readonly>' +
//             '<span class="error-message" id="total-error"></span>' +
//             "</div>" +
//             '<td class="eliminar-producto"><span class="icono-eliminar">X</span></td>' +
//             "</td>";
//         +"</tr>";
//         let filaAgregada = $(nuevaFila);
//         $("tbody").append(filaAgregada);

//         inicializarSugerenciasEnFila(filaAgregada);
//     });

//     function inicializarSugerenciasEnFila(fila) {
//         fila
//             .find(".mess-sugges-prod")
//             .after('<div class="producto-suggestions"></div>');
//     }

//     function calcularTotalVenta() {
//         let totalVenta = 0; // Inicializa como número

//         $(".producto-row").each(function () {
//             let precioTotal = parseInt($(this).find(".precioTotal").val().replace(/[^\d.-]/g, ''));

//             if (!isNaN(precioTotal)) {
//                 totalVenta += precioTotal;
//             }
//         });

//         let totalVentaFormateado = "$ " + totalVenta.toLocaleString();
//         $("#totalVenta").val(totalVentaFormateado);
//     }



//     function validarCamposLlenos() {
//         let camposLlenos = true;
//         const documentoValue = $("#documentoDato").text();
//         const totalVentaValue = parseFloat($("#totalVenta").val().replace(/[^\d.-]/g, ''));

//         const nombreClienteValue = $("#nombreCliente").val();
//         const productos = [];

//         if (!nombreClienteValue) {
//             mostrarError("#nombreCliente");
//             $("#error-docu").text(
//                 "El campo del documento no puede estar vacío. Por favor, ingréselo correctamente."
//             );
//             camposLlenos = false;
//         } else if (!documentoValue) {
//             mostrarError("#nombreCliente");
//             $("#error-docu").text(
//                 "El documento debe estar correctamente escrito. Por favor, verifique y vuelva a intentar."
//             );
//             camposLlenos = false;
//         }

//         $(".producto-row").each(function (index) {
//             const row = $(this);
//             const productoInput = row.find(".producto");
//             const cantidadInput = row.find(".cantidad");
//             const precioUnidad = row.find(".precioUnidad").val();
//             const precioUnidadInput = row.find(".precioUnidad");
//             const precioTotalInput = row.find(".precioTotal");


//             const productoValue = productoInput.val();
//             const precioUnidadValue = parseInt(precioUnidadInput.val().replace(/[^\d.-]/g, ''));
//             const precioTotalValue = parseInt(precioTotalInput.val().replace(/[^\d.-]/g, ''));

//             const cantidadValue = parseInt(cantidadInput.val());

//             if (!precioUnidadValue) {
//                 productoInput.addClass("is-invalid");
//                 row
//                     .find(".error-produ")
//                     .text(
//                         "Por favor, selecciona un producto válido para completar el registro."
//                     );
//                 camposLlenos = false;
//             }

//             if (!productoValue) {
//                 mostrarError(productoInput);
//                 camposLlenos = false;
//             }

//             if (!cantidadValue) {
//                 mostrarError(cantidadInput);
//                 camposLlenos = false;
//             } else {
//                 productos.push({
//                     nombre: productoValue,
//                     precioUnidad: precioUnidadValue,
//                     precioTotal: precioTotalValue,
//                     cantidad: cantidadValue
//                 });
//             }
//         });

//         return camposLlenos
//             ? { documento: documentoValue, totalVenta: totalVentaValue, productos: productos }
//             : null;
//     }

//     function mostrarError(selector) {
//         $(selector).addClass("is-invalid");

//         $("#nombreCliente, .producto, .cantidad").on("input", function () {
//             const campo = $(this);
//             $("#error-docu").text("");
//             if (campo.val()) {
//                 campo.removeClass("is-invalid");
//             }
//         });
//     }

//     $("#venta-form").submit(function (event) {
//         event.preventDefault();

//         const data = validarCamposLlenos();
//         if (!data) {
//             return;
//         }
//         $.ajax({
//             type: "POST",
//             url: "{% url 'crear_venta' %}",
//             data: JSON.stringify(data),
//             contentType: "application/json",
//             success: function (response) {
//                 if (response.success) {
//                     alert("Venta Creada con Éxito.");
//                     window.location.href = "{% url 'ventas' %}";
//                 }
//             },
//         });
//     });
// });