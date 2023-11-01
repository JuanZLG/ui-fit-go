// Barra principal ----------------------- 
document.addEventListener('DOMContentLoaded', function () {

  let main = document.getElementById("main-menu");
  document.getElementById("hamburgerCheckbox").addEventListener("click", function () {
    main.classList.toggle("is-active");
  });


  // Despliegue de menu productos ----------------------- 
  // Despliegue de menú productos ----------------------- 
  const toggleMenu = document.getElementById('toggle-menu');
  const menuOptions = document.getElementById('menu-options');

  const toggleMenuProducts = document.getElementById('toggle-main-products');
  const OptionsProductsMain = document.getElementById('main-options-products');
  const iconProducts = toggleMenuProducts.querySelector('.icon'); 

  const toggleMenumarcas = document.getElementById('toggle-main-marcas');
  const OptionsMarcasMain = document.getElementById('main-options-marcas');
  const iconMarcas = toggleMenumarcas.querySelector('.icon'); 

  toggleMenu.addEventListener('click', function () {
    menuOptions.classList.toggle('is-active');
  });

  toggleMenuProducts.addEventListener('click', function () {
    OptionsProductsMain.classList.toggle('is-active');

    iconProducts.classList.toggle('fa-chevron-up');
    iconProducts.classList.toggle('fa-chevron-down');
  });

  toggleMenumarcas.addEventListener('click', function () {
    OptionsMarcasMain.classList.toggle('is-active');

    iconMarcas.classList.toggle('fa-chevron-up');
    iconMarcas.classList.toggle('fa-chevron-down');
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
  const listButton = document.getElementById('list');
  const gridButton = document.getElementById('grid');
  const productContainer = document.getElementById('product-container');

  listButton.addEventListener('click', function (e) {
    productContainer.classList.remove('grid-view');
    productContainer.classList.add('list-view');
  });

  gridButton.addEventListener('click', function (e) {
    productContainer.classList.remove('list-view');
    productContainer.classList.add('grid-view');
  });





});  
