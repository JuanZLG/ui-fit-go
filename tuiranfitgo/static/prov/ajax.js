$(document).ready(function () {
    // Función para validar que todos los campos estén llenos
    function validarCamposLlenos() {
        let camposLlenos = true;
        const nombreValue = $('#nombre_proveedor').val();
        const telefonoValue = $('#telefono').val();
        const correoValue = $('#correo').val();

        if (!nombreValue) {
            mostrarError('#nombre_proveedor', 'Este campo es obligatorio.');
            camposLlenos = false;
        }
        if (!telefonoValue) {
            mostrarError('#telefono', 'Este campo es obligatorio.');
            camposLlenos = false;
        } else if (!/^\d{10}$/.test(telefonoValue)) {
            mostrarError('#telefono', 'Número inválido.');
            camposLlenos = false;
        }
        if (!correoValue) {
            mostrarError('#correo', 'Este campo es obligatorio.');
            camposLlenos = false;
        } else if (!validarFormatoCorreo(correoValue)) {
            mostrarError('#correo', 'El formato del correo electrónico no es válido.');
            camposLlenos = false;
        }
        return camposLlenos;
    }

    // Validación de campos al escribir
    $('#nombre_proveedor, #telefono, #correo').on('input', function () {
        const campo = $(this);
        const campoValue = campo.val();

        if (campoValue) {
            campo.removeClass('is-invalid');
            $(`#${campo.attr('id')}-error`).text('');
        }
    });

    function mostrarError(selector, mensaje) {
        $(selector).addClass('is-invalid');
        $(`${selector}-error`).text(mensaje).css('color', 'red');
    }

    function validarFormatoCorreo(correo) {
        const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        return emailRegex.test(correo);
    }

    $('#proveedor-form').submit(function (event) {
        event.preventDefault();
        // Validar que todos los campos estén llenos
        if (!validarCamposLlenos()) {
            return;
        }
        // Continuar con el envío del formulario si todos los campos están llenos
        $.ajax({
            type: 'POST',
            url: "{% url 'create' %}",
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    // Éxito: redirige o realiza acciones adicionales
                    alert('Proveedor creado con éxito.');
                    window.location.href = "{% url 'proveedores' %}";
                }
            }
        });
    });
});