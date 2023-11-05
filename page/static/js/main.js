document.addEventListener('DOMContentLoaded', function () {

    var pageDetailsUrl = "{% url 'pageDetails' %}";
    var searchProductsUrl = "{% url 'search_products' %}"
    var filterProductsUrl = "{% url 'filter_products' %}"

    function cargarDetalle(id_producto) {
        $.ajax({
            url: pageDetailsUrl,
            data: {
                'producto_id': id_producto
            },
            dataType: 'json',
            success: function (data) {
                Swal.fire({
                    html: `
  <div>
    <swiper-container class="mySwiper" keyboard="true" space-between="30" pagination="true"
        pagination-clickable="true" navigation="true" loop="true">
        <swiper-slide><a href="/media/landingproducts/products/${data.iProductImg_name}" data-lightbox="image-1"><img src="/media/landingproducts/products/${data.iProductImg_name}" class="img-fluid"
            alt="Imagen"></a></swiper-slide>
        <swiper-slide><a href="/media/landingproducts/nutritiondex/${data.iInfoImg_name}" data-lightbox="image-1"><img src="/media/landingproducts/nutritiondex/${data.iInfoImg_name}" class="img-fluid"
            alt="Imagen"></a></swiper-slide>
    </swiper-container>
        <div class="col-lg-12 mb-4 mt-4" style="text-align:left;">
            <h2 class="my-3"> ${data.nombre_producto} <strong>${data.precio}</strong></h2>
            <div class="mb-3" style="max-height: 100px; height: auto;overflow-y: scroll;"> ${data.descripcion}</div>
            <hr >
            <ul class="list-group list-group-flush mt-4">
                <li><strong>Sabores:</strong> ${data.sabor}</li>
                <hr >
                <li><strong>Presentaciones por libras:</strong> ${data.presentacion}lbs</li>
            </ul>
        </div>
  </div>
`,
                    showCloseButton: true,
                    showConfirmButton: false,
                    customClass: {
                        closeButton: 'custom-close-button'
                    }
                })
            }
        });
    }



    $(document).on("input", ".search", function () {
        let search = $(this).val();

        if (search.length >= 2) {
            $.ajax({
                url: searchProductsUrl,
                method: 'GET',
                data: { search: search },
                success: function (data) {
                    if (data.success) {
                        if (data.data.length > 0) {
                            $("#toggle-main-search").empty();
                            $.each(data.data, function (index, p) {
                                $("#toggle-main-search").addClass("is-active");
                                var productList =
                                    '<div class="search-card productDetailsButton" data-id="' + p.id_producto + '">' +
                                    '<div class="search-image">' +
                                    '<img class="img-fluid" src="/media/landingproducts/products/' + p.iProductImg_name + '" alt="Imagen"></div>' +
                                    '<p class="search-title">' + p.nombre_producto + '</p></div >';
                                $("#toggle-main-search").append(productList);
                            });
                            $('.productDetailsButton').click(function () {
                                id_producto = $(this).data("id")
                                closeMains()
                                $("#search-input").val("");
                                $("#toggle-main-search").empty();
                                $("#toggle-main-search").removeClass("is-active");
                                setTimeout(function () {
                                    cargarDetalle(id_producto);
                                }, 200);
                            });
                        } else {
                            $("#toggle-main-search").empty();
                            $("#toggle-main-search").removeClass("is-active");
                        }
                    }
                }
            });
        } else {
            $("#toggle-main-search").empty();
            $("#toggle-main-search").removeClass("is-active");
        }
    });

    $("#search-clear").on("click", function () {
        $("#search-input").val("");
        $("#toggle-main-search").empty();
        $("#toggle-main-search").removeClass("is-active");
    });


    function filterProducts(valor, tipo = "productos") {
        $.ajax({
            url: filterProductsUrl,
            method: 'GET',
            data: { valor: valor, tipo: tipo },
            success: function (data) {
                if (data.success) {
                    $("#product-container").empty();

                    $.each(data.data, function (index, p) {
                        var productCard =
                            '<div class="product-card productDetailsButton" data-id="' + p.id_producto + '">' +
                            '<div class="product-image">' +
                            '<img src="/media/landingproducts/products/' + p.iProductImg_name + '" alt="Imagen"></div>' +
                            '<div class="product-details">' +
                            '<h3 class="product-title">' + p.nombre_producto + '</h3>' +
                            '<div class="product-description">' +
                            '<p>' + p.descripcion + '</p></div>' +
                            '<div class="product-price">' +
                            '<span>' + p.precio + '</span>' +
                            '<span class="product-search">' +
                            '<i class="fas fa-search"></i></span></div>' +
                            '</div ></div >';

                        $("#dynamic-title").text(p.dynamicTitle);
                        $("#dynamic-title").data("id-filter", p.identificador);
                        $("#product-container").append(productCard);
                    });
                    $('.productDetailsButton').click(function () {
                        id_producto = $(this).data("id")
                        cargarDetalle(id_producto);
                    });
                }
            }
        });
    }



    /***********************++++++++++++++ */
    const toggleProductos = document.getElementById("toggle-main-productos");
    const toggleMarcas = document.getElementById("toggle-main-marcas");
    const toggleCategorias = document.getElementById("toggle-main-categorias");
    const mainOptionsProductos = document.getElementById("main-options-products");
    const mainOptionsMarcas = document.getElementById("main-options-marcas");
    const mainOptionsCategorias = document.getElementById("main-options-categorias");

    const iconProductos = toggleProductos.querySelector("i");
    const iconMarcas = toggleMarcas.querySelector("i");
    const iconCategorias = toggleCategorias.querySelector("i");

    const closeSubMainOptions = document.getElementById('close-submain-options');

    function toggleCloseSubMain() {
        // Cerrar opciones
        mainOptionsProductos.classList.remove("is-active");
        mainOptionsMarcas.classList.remove("is-active");
        mainOptionsCategorias.classList.remove("is-active");
        // Volver iconos a su estado original
        iconProductos.classList.remove("fa-chevron-up");
        iconProductos.classList.add("fa-chevron-down");
        iconMarcas.classList.remove("fa-chevron-up");
        iconMarcas.classList.add("fa-chevron-down");
        iconCategorias.classList.remove("fa-chevron-up");
        iconCategorias.classList.add("fa-chevron-down");
    }
    function resetSortSelect() {
        const sortSelect = document.getElementById('sort');
        sortSelect.value = 'all';
    }
    closeSubMainOptions.addEventListener('click', () => toggleCloseSubMain());

    function toggleActiveClass(element, iconElement, otherElements, otherIcons) {
        // Desactiva todas las opciones
        otherElements.forEach((otherElement) => {
            otherElement.classList.remove("is-active");
        });
        // Restaura los íconos a su estado original
        otherIcons.forEach((otherIcon) => {
            otherIcon.classList.remove("fa-chevron-up");
            otherIcon.classList.add("fa-chevron-down");
        });

        // Activa la opción seleccionada
        element.classList.toggle("is-active");
        iconElement.classList.toggle("fa-chevron-up");
        iconElement.classList.toggle("fa-chevron-down");
    }

    toggleProductos.addEventListener("click", function () {
        toggleActiveClass(mainOptionsProductos, iconProductos, [mainOptionsMarcas, mainOptionsCategorias], [iconMarcas, iconCategorias]);
        resetSortSelect();
    });

    toggleMarcas.addEventListener("click", function () {
        toggleActiveClass(mainOptionsMarcas, iconMarcas, [mainOptionsProductos, mainOptionsCategorias], [iconProductos, iconCategorias]);
        resetSortSelect();
    });

    toggleCategorias.addEventListener("click", function () {
        toggleActiveClass(mainOptionsCategorias, iconCategorias, [mainOptionsProductos, mainOptionsMarcas], [iconProductos, iconMarcas]);
        resetSortSelect();
    });


    /**************************************************/
    function closeMains() {
        document.getElementById('options-submain-products').classList.remove('is-active');
        document.getElementById('main-menu').classList.remove('is-active');
        const checkbox = document.getElementById("hamburgerCheckbox");
        checkbox.checked = false;
        toggleCloseSubMain()
    }
    $(document).ready(function () {
        $("#sort").change(function () {
            let selectedValue = $(this).val();
            if (selectedValue == "defect") location.reload();
            const tipo = $("#dynamic-title").data('id-filter');
            filterProducts(selectedValue, tipo);
        });
        const menuListItems = document.querySelectorAll('.menu-list-item');

        menuListItems.forEach((menuItem) => {
            menuItem.addEventListener('click', function () {
                const itemName = menuItem.textContent;
                const tipo = menuItem.getAttribute('data-id-filter');
                filterProducts(itemName, tipo);
                closeMains()
            });
        });
    })




    $('.productDetailsButton').off('click').click(function () {
        id_producto = $(this).data("id")
        cargarDetalle(id_producto);
    });

    let css = '.custom-close-button { border: none !important; color: black !important; }',
        head = document.head || document.getElementsByTagName('head')[0],
        style = document.createElement('style');

    head.appendChild(style);

    style.type = 'text/css';
    if (style.styleSheet) {
        style.styleSheet.cssText = css;
    } else {
        style.appendChild(document.createTextNode(css));
    }

});
