
$(document).ready(function () {
            function cambiarContraseña() {
                Swal.close();
                Swal.fire({
                    title: '<span style="font-family:Arial; font-size:25px; color: #fff">Cambiar contraseña</span>',
                    html: `
                        <svg viewBox="25 25 50 50" id="loading">
                            <circle r="20" cy="50" cx="50"></circle>
                        </svg>
                        <div class="forget-container" style="text-align:left;">
                            <p style="font-size: 14px; color: #f2f2f2; text-align: start;"></p>
                            <div class="recover-container-inputs" id="input-container">
                                <label for="new-password">
                                    Nueva contraseña *
                                    <input type="password" id="new-password" placeholder="Nueva contraseña">
                                </label>
                                <label for="confirm-password">
                                    Confirmar nueva contraseña *
                                    <input type="password" id="confirm-password" placeholder="Confirmar nueva contraseña">
                                </label>
                            </div>
                            <span id="recover-error" style="font-size: 14px; color:#C00000;"></span>
                            <div class="forget-butons">
                                <button id="submit-recover" class="submit-recover" style=" width: auto; padding: 0 10px">Aceptar</button>
                                <button id="close-recover">Cancelar</button>
                            </div>
                        </div>
                `,
                    showConfirmButton: false,
                    showCancelButton: false,
                    customClass: {
                        popup: 'sweet-forget'
                    }
                });
                $("#close-recover").click(function () {
                    Swal.close();
                });

                $(".recover-container-inputs input").on("input", function () {
                    $("#recover-error").text("");
                });

                $("#submit-recover").click(function () {
                    let newPassword = $("#new-password").val();
                    let confirmPassword = $("#confirm-password").val();

                    if (newPassword !== confirmPassword) {
                        $("#recover-error").text("Las contraseñas no coinciden.");
                        return;
                    } else if (newPassword == "" || confirmPassword == "") {
                        $("#recover-error").text("Ambos campos son requeridos.");
                        return;
                    } else {
                        const regex = /^(?=.*[A-Z])(?=.*\d).{8,}$/;
                            if (!regex.test(newPassword)) {
                                $("#recover-error").text("La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.");
                                return;
                            }
                    }
                    $("#loading").show();
                    setTimeout(function () {
                        $("#loading").hide();
                        $.ajax({
                            url: "{% url 'restablecer_contrasena' %}",
                            type: 'POST',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            data: {
                                newPassword: newPassword
                            },
                            success: function (response) {
                                Swal.close();
                                Swal.fire({
                                    icon: 'success',
                                    title: '¡Cuenta recuperada!',
                                    text: 'Ahora puedes ingresar con tu nueva contraseña.',
                                    confirmButtonColor: '#808080', 
                                    confirmButtonText: 'Aceptar',
                                    customClass: {
                                        confirmButton: 'white-text' ,
                                        title: "white-text",
                                        text: "white-text",
                                    }
                                });
                            }
                        })
                    }, 2000);
                    $("#close-recover").click(function () {
                        Swal.close();
                    });
                });


            }


            function validarCodigo() {
                Swal.close();
                Swal.fire({
                    title: '<span style="font-family:Arial; font-size:25px; color: #fff">Código de Verificación</span>',
                    html: `
                        <svg viewBox="25 25 50 50" id="loading">
                            <circle r="20" cy="50" cx="50"></circle>
                        </svg>
                        <div class="forget-container" style="text-align:left;">
                            <p style="font-size: 14px; color: #f2f2f2; text-align: start;">Ingresa el código enviado al correo para restablecer tu contraseña.</p>
                            <div class="codig-container-inputs" id="input-container">
                                <input type="number" maxlength="1">
                                <input type="number" maxlength="1">
                                <input type="number" maxlength="1">
                                <input type="number" maxlength="1">
                                <input type="number" maxlength="1">
                            </div>
                            <span id="codig-error" style="display: inline-block; font-size: 14px; color:#C00000;"></span>
                            <div class="forget-butons">
                                <button id="submit-codig" class="btn-codig" style=" width: auto; padding: 0 10px">Verificar código</button>
                                <button id="close-codig">Cancelar</button>
                            </div>
                        </div>
                        `,
                    showConfirmButton: false,
                    showCancelButton: false,
                    customClass: {
                        popup: 'sweet-forget'
                    }
                });
                $("#loading").hide();

                $("#close-codig").click(function () {
                    Swal.close();
                });

                document.querySelectorAll('#input-container input').forEach((input, index, inputArray) => {
                    input.addEventListener('input', () => {
                        $("#codig-error").text("");
                        if (input.value.length > 1) {
                            input.value = input.value[0];
                        }
                        if (input.value.length === 1 && index < inputArray.length - 1) {
                            inputArray[index + 1].focus();
                        }

                        if (Array.from(inputArray).every(input => input.value.length === 1)) {
                            document.querySelector('.btn-codig').classList.add('is-active');
                        } else {
                            document.querySelector('.btn-codig').classList.remove('is-active');
                        }
                    });

                    input.addEventListener('keydown', (event) => {
                        if (event.key === 'Backspace' && index > 0 && input.value.length === 0) {
                            inputArray[index - 1].focus();
                        }
                    });

                    input.addEventListener('keypress', (event) => {
                        if (!/\d/.test(event.key)) {
                            event.preventDefault();
                        }
                    });
                });

                $("#submit-codig").click(function () {
                    let codigo = "";
                    $("#input-container input").each(function () {
                        codigo += $(this).val();
                    });

                    $("#loading").show();
                    setTimeout(function () {
                        $("#loading").hide();
                    $.ajax({
                        url: "{% url 'verificar_codigo' %}",
                        type: 'GET',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        data: {
                            codigo: codigo
                        },
                        success: function (response) {
                            if (response.success) {
                                $("#loading").hide();
                                cambiarContraseña();
                            }
                            else {
                                $("#codig-error").text("Código incorrecto.");
                            }
                        }
                    })
                }, 2000);

                });
            }

            $("#forget-pass").click(function () {
                Swal.fire({
                    title: '<span style="font-family:Arial; font-size:25px; color: #fff">Recuperar contraseña</span>',
                    html: `
                    <svg viewBox="25 25 50 50" id="loading">
                        <circle r="20" cy="50" cx="50"></circle>
                    </svg>
                    <div class="forget-container" style="position: relative; text-align: start;">
                        <p style="display: inline-block; font-size: 14px; color: #f2f2f2;">Ingresa tu correo electrónico, te enviaremos un código para restablecer tu contraseña.</p>
                        <input type="email" id="forget-correo" name="correo" placeholder="Correo Electrónico">
                        <span id="forget-error" style="font-size: 14px; color:#C00000;"></span>
                        <div class="forget-butons">
                            <button id="submit-btn">Enviar</button>
                            <button id="close-btn">Cerrar</button>
                        </div>
                    </div>
                `,
                    showConfirmButton: false,
                    showCancelButton: false,
                    customClass: {
                        popup: 'sweet-forget'
                    }
                });
                $("#loading").hide();

                $("#forget-correo").on("input", function () {
                    $("#forget-error").text("");
                });

                $("#close-btn").click(function () {
                    Swal.close();
                });

                $(document).ajaxStart(function () {
                    $("#loading").show();
                });

                $(document).ajaxStop(function () {
                    $("#loading").hide();
                });
                $("#submit-btn").click(function () {
                    let correo = $("#forget-correo").val();
                    let regex = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/;
                    if (correo == "") {
                        $("#forget-error").text("Campo requerido");
                    } else if (!regex.test(correo)) {
                        $("#forget-error").text("Introduce un correo electrónico válido");
                    } else {
                        $("#forget-error").text("");
                        $("#submit-btn").addClass("inhabilitado")
                        $("#forget-correo").addClass("inhabilitado")
                        let loadingTimeout = setTimeout(function () {
                            $("#loading").show();
                        }, 1000);
                        $.ajax({
                            url: "{% url 'verificar_correo' %}",
                            type: 'GET',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            data: {
                                correo: correo
                            },
                            success: function (response) {
                                clearTimeout(loadingTimeout);
                                if (response.existe) {
                                    $("#loading").hide();
                                    validarCodigo()
                                }
                                else {
                                    $("#submit-btn").removeClass("inhabilitado")
                                    $("#forget-correo").removeClass("inhabilitado")
                                    $("#forget-error").text("No existen registros asociados con el correo electrónico ingresado");
                                }
                            }
                        })
                    }
                });
            });
        });


        document.getElementById('login-button').addEventListener('click', function () {
            document.getElementById('user-error').textContent = '';
            document.getElementById('correo-error').textContent = '';
            document.getElementById('contra-error').textContent = '';
            document.getElementById('status-error').textContent = '';
            document.getElementById('cvalid-error').textContent = '';

            var correo = document.querySelector('[name="correo"]').value;
            var contra = document.querySelector('[name="contra"]').value;
            var formData = {
                correo: correo,
                contra: contra
            };

            if (!correo && !contra) {
                displayError('correo', 'El correo es obligatorio');
                displayError('contra', 'La contraseña es obligatoria');
            } else if (!correo) {
                displayError('correo', 'El correo es obligatorio');
            } else if (!contra) {
                displayError('contra', 'La contraseña es obligatoria');
            } else {

                fetch("{% url 'login_view' %}", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(formData)
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.token) {
                            console.log("Token Cargado");
                            setCookie('jwt_token', data.token, 30);
                            window.location.href = 'admin/home/';
                        } else if (data.error === 'Usuario no Registrado') {
                            displayError('user', 'No existe un usuario registrado con este correo');
                        } else if (data.error === 'Usuario inactivo') {
                            displayError('status', 'El usuario asociado a este correo esta inactivo')
                        } else if (data.error === 'contrasena incorrecta') {
                            displayError('cvalid', 'La contraseña es incorrecta')
                        } else {
                            displayError('correo', 'Error: ' + data.error);
                        }
                    })
                    .catch(error => {
                        displayError('correo', 'Error: ' + error);
                    });
            }
        });

        function displayError(field, message) {
            var errorElement = document.getElementById(field + '-error');
            errorElement.textContent = message;
        }

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function setCookie(name, value, daysToExpire) {
            var date = new Date();
            date.setTime(date.getTime() + (daysToExpire * 24 * 60 * 60 * 1000));
            var expires = "expires=" + date.toUTCString();
            document.cookie = name + "=" + value + "; " + expires;
        }
   

        var imgn = document.getElementById('logus');

        imgn.oncontextmenu = function (e) {
            e.preventDefault();
        };
    </script>

    <script>
        var video = document.getElementById("video-fondo");
        video.playbackRate = 0.75;
    </script>