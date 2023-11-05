document.addEventListener('DOMContentLoaded', function () {
  
  
  window.addEventListener('resize', function() {
    var width = window.innerWidth;
    var breakpoint = 768;
    if (width >= breakpoint) {
        document.querySelector('.mobile-header').style.display = 'none';
        document.querySelector('.desktop-header').style.display = 'block';
    } else {
        document.querySelector('.mobile-header').style.display = 'block';
        document.querySelector('.desktop-header').style.display = 'none';
    }
  });
  window.dispatchEvent(new Event('resize'));
  
  
  // Barra principal ----------------------- 
  let main = document.getElementById("main-menu");
  document.getElementById("hamburgerCheckbox").addEventListener("click", function () {
    main.classList.toggle("is-active");
  });


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


  // Opciones SubMenu ----------------------- 

});  