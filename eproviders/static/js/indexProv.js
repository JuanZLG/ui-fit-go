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
                text: '¿Desea cambiar el estado de este registro?',
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
                    $("#nombreProveedor").text(proveedor.nombre_proveedor);
                    $("#telefonoProveedor").text(proveedor.telefono);
                    $("#correoProveedor").text(proveedor.correo);

                    if (proveedor.identificacion !== "") {
                        $("#tipo").text(proveedor.tipo);
                        $("#identificacion").text(proveedor.identificacion);
                        $("#identificacionRow").show();
                    } else {
                        $("#identificacionRow").hide();
                    }

                    if (proveedor.direccion !== "") {
                        $("#direccion").text(proveedor.direccion);
                        $("#direccionRow").show();
                    } else {
                        $("#direccionRow").hide();
                    }

                    if (proveedor.informacion !== "") {
                        $("#informacion").text(proveedor.informacion);
                        $("#informacionRow").show()
                    } else {
                        $("#informacionRow").hide();
                    }

                    if (proveedor.estado == 1) {
                        $(".estadoProveedorCircle").addClass("activo").removeClass("inactivo");
                    } else {
                        $(".estadoProveedorCircle").addClass("inactivo").removeClass("activo");
                    }

                    document.getElementById("verDetallesDialog").showModal();
                    $(".proveedorDialog").addClass("fadeIn");
                    $(".modal-backdrop").show();
                    $(".modal-backdrop").addClass("fadeInBack");
                },
            });


            $("#cerrarDetallesProveedor").click(function () {
                $(".proveedorDialog").addClass("fadeOut");
                $(".modal-backdrop").addClass("fadeOut");
                setTimeout(function () {
                    document.getElementById("verDetallesDialog").close();
                    $(".proveedorDialog").removeClass("fadeOut");
                    $(".modal-backdrop").hide();
                    $(".modal-backdrop").removeClass("fadeOut");
                }, 300);
            });
        });
    });


    // $("#nombre_proveedor, #telefono, #correo, #tipoIdentificacion, #identificacion, #direccion, #informacion").val("");
    // function mostrarError(selector, mensaje) {
    //     $(selector).addClass('is-invalid');
    //     $(`${selector}-error`).text(mensaje).css('color', 'red');
    // }

    // function validarFormatoCorreo(correo) {
    //     const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    //     return emailRegex.test(correo);
    // }
    // function validarCamposObligatorios() {
    //     let camposLlenos = true;
    //     const nombreValue = $('#nombre_proveedor').val();
    //     const telefonoValue = $('#telefono').val();
    //     const correoValue = $('#correo').val();
    //     const tipoIdentificacionValue = $('#tipoIdentificacion').val(); // Obtener valor del select
    //     const identificacionValue = $('#identificacion').val(); // Obtener valor del input identificacion

    //     if (!nombreValue) {
    //         mostrarError('#nombre_proveedor', 'Este campo es obligatorio.');
    //         camposLlenos = false;
    //     }
    //     if (!telefonoValue) {
    //         mostrarError('#telefono', 'Este campo es obligatorio.');
    //         camposLlenos = false;
    //     } else if (!/^\d{10}$/.test(telefonoValue)) {
    //         mostrarError('#telefono', 'Número inválido.');
    //         camposLlenos = false;
    //     }
    //     if (!correoValue) {
    //         mostrarError('#correo', 'Este campo es obligatorio.');
    //         camposLlenos = false;
    //     } else if (!validarFormatoCorreo(correoValue)) {
    //         mostrarError('#correo', 'El formato del correo electrónico no es válido.');
    //         camposLlenos = false;
    //     }

    //     if (tipoIdentificacionValue !== '' && identificacionValue === '') {
    //         mostrarError('#identificacion', 'Debe ingresar una identificación.');
    //         camposLlenos = false;
    //     } else if (tipoIdentificacionValue === '' && identificacionValue !== '') {
    //         mostrarError('#identificacion', 'Debe seleccionar el tipo de identificación.');
    //         camposLlenos = false;
    //     } else {
    //         $("#identificacion").removeClass("is-invalid")
    //         $("#identificacion-error").text("")
    //     }

    //     return camposLlenos;
    // }


    // $('#nombre_proveedor, #telefono, #correo, #identificacion').on('input', function () {
    //     const campo = $(this);
    //     const campoValue = campo.val();

    //     if (campoValue) {
    //         campo.removeClass('is-invalid');
    //         $(`#${campo.attr('id')}-error`).text('');
    //     }
    // });

    
    // function validarProveedor(proveedor, url) {
    //     return new Promise(function (resolve, reject) {
    //         $.ajax({
    //             url: url,
    //             type: "GET",
    //             data: {
    //                 proveedor: proveedor,
    //             },
    //             success: function (data) {
    //                 if (data.existe) {
    //                     resolve(true);
    //                 } else {
    //                     resolve(false);
    //                 }
    //             }
    //         });
    //     });
    // }

    // $('#proveedor-form').submit(function (event) {
    //     event.preventDefault();
    //     let urlCrear = document.getElementById("btnCrearProv").getAttribute("data-url-crear");
    //     let urlValidar = document.getElementById("btnCrearProv").getAttribute("data-url-validar");
    //     //     <div class="text-end mt-3">
    //     //     <button id="btnCrearProv" class="btn btn-success mx-auto" type="submit" data-url-crear="{% url 'crearProveedor' %}"  data-url-validar="{% url 'proveedor_unico' %}">Guardar</button>
    //     // </div>
    //     if (!validarCamposObligatorios()) {
    //         return;
    //     }
    //     prov = $("#nombre_proveedor").val()
    //     validarProveedor(prov, urlValidar).then(function (existe) {
    //         if (existe) {
    //             $("#nombre_proveedor").addClass("is-invalid");
    //             $("#nombre_proveedor-error").text("El proveedor " + prov + " ya existe").css("color", "red");
    //         } else {
    //             $("#nombre_proveedor").removeClass("is-invalid");
    //             $("#nombre_proveedor-error").text("");
    //             enviarDatosProveedor(urlCrear);
    //         }
    //     });
    // });

    // function enviarDatosProveedor(url) {
    //     $.ajax({
    //         type: 'POST',
    //         url: url,
    //         data: $('#proveedor-form').serialize(),
    //         success: function (response) {
    //             if (response.success) {
    //                 Swal.fire({
    //                     title: 'Éxito',
    //                     text: 'Proveedor creado con éxito',
    //                     icon: 'success',
    //                     showConfirmButton: false, 
    //                     timer: 2000,
    //                 });
    //                 setTimeout(function () {
    //                     window.location.href = "{% url 'proveedores' %}";
    //                 }, 2000);
    //             }
    //         }
    //     });            
    // }


});
