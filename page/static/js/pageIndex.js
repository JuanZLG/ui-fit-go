document.addEventListener('DOMContentLoaded', function () {

  let toggleInfo = document.getElementById('toggle-info');
  let menuInfo = document.getElementById('menu-info');

  toggleInfo.addEventListener('mouseover', function () {
    menuInfo.classList.add('show');
  });

  toggleInfo.addEventListener('mouseout', function () {
    menuInfo.classList.remove('show');
  });
  // Barra principal ----------------------- 
  let main = document.getElementById("main-menu");
  document.getElementById("hamburgerCheckbox").addEventListener("click", function () {
    main.classList.toggle("is-active");
  });

  let mediaQuery = window.matchMedia("(min-width: 768px)");
  let hamburgerCheckbox = document.getElementById('hamburgerCheckbox');

  function handleWidthChange(e) {
    if (e.matches) {
      main.classList.remove("is-active");
      hamburgerCheckbox.checked = false;
      document.getElementById("options-submain-products").classList.remove("is-active")
    }
  }

  mediaQuery.addListener(handleWidthChange);

  handleWidthChange(mediaQuery);
// Obtén el input por su id


  // Despliegue de menu productos -----------------------

  const togglesSubmenuProducts = document.getElementById('toggle-submain-products');
  const closeSubMainOptions = document.getElementById('close-submain-options');
  const OptionsProductsMain = document.getElementById('options-submain-products');

  togglesSubmenuProducts.addEventListener('click', function () {
    OptionsProductsMain.classList.toggle('is-active');
  });

  closeSubMainOptions.addEventListener('click', function () {
    OptionsProductsMain.classList.toggle('is-active');
  });

  // Opciones de menu productos ----------------------- 
  const radioInputs = document.querySelectorAll('.radio input');
  const contentSections = document.querySelectorAll('.menu-column');

  function showSelectedContent() {
    const checkedInput = document.querySelector('.radio input:checked');
    if (checkedInput) {
      const selectedOption = checkedInput.parentElement.getAttribute('data-option');

      contentSections.forEach((section) => {
        section.style.display = 'none';
      });

      const selectedContent = document.querySelector(`.menu-column[data-option="${selectedOption}"]`);
      if (selectedContent) {
        selectedContent.style.display = 'block';
      }
    }
  }

  showSelectedContent();

  radioInputs.forEach((input) => {
    input.addEventListener('change', showSelectedContent);
  });

  // Ordenar productos por Lista o Grillas ----------------------- 
  function toggleView(viewType, containerSelector) {
    const productContainer = document.querySelector(containerSelector);

    if (viewType === 'list') {
      productContainer.classList.remove('grid-view');
      productContainer.classList.add('list-view');
    } else if (viewType === 'grid') {
      productContainer.classList.remove('list-view');
      productContainer.classList.add('grid-view');
    }
  }

  // Evento de clic para la versión móvil
  document.querySelectorAll('.mobile .view-options .list').forEach(function (element) {
    element.addEventListener('click', function (e) {
      toggleView('list', '#product-container-mobile');
    });
  });

  document.querySelectorAll('.mobile .view-options .grid').forEach(function (element) {
    element.addEventListener('click', function (e) {
      toggleView('grid', '#product-container-mobile');
    });
  });

  // Evento de clic para la versión de escritorio
  // document.querySelectorAll('.desktop .view-options .list').forEach(function (element) {
  //   element.addEventListener('click', function (e) {
  //     toggleView('list', '#product-container-desk');
  //   });
  // });

  // document.querySelectorAll('.desktop .view-options .grid').forEach(function (element) {
  //   element.addEventListener('click', function (e) {
  //     toggleView('grid', '#product-container-desk');
  //   });
  // });


  // Opciones SubMenu ----------------------- 


  var activeElement = null;

  document.querySelectorAll('.element-container').forEach(function (element) {
    element.addEventListener('click', function (event) {
      event.stopPropagation();
      var optionElement = this.querySelector('.element-option');
      if (activeElement && activeElement === optionElement) {
        activeElement.style.display = 'none';
        activeElement = null;
      } else {
        if (activeElement) {
          activeElement.style.display = 'none';
        }
        optionElement.style.display = 'block';
        activeElement = optionElement;
      }
    });
  });

  document.addEventListener('click', function () {
    if (activeElement) {
      activeElement.style.display = 'none';
      activeElement = null;
    }
  });

  window.addEventListener('scroll', function () {
    if (activeElement) {
      activeElement.style.display = 'none';
      activeElement = null;
    }
  });
  document.getElementById("product-container-desk").addEventListener('scroll', function () {
    if (activeElement) {
      activeElement.style.display = 'none';
      activeElement = null;
    }
  });

});  