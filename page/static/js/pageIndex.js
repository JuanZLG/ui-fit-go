let main = document.getElementById("main-menu");
document.getElementById("hamburgerCheckbox").addEventListener("click", function () {
  main.classList.toggle("is-active");
});


document.addEventListener('DOMContentLoaded', function () {
  const toggleMenu = document.getElementById('toggle-menu');
  const toggleMenuProducts = document.getElementById('toggle-main-products');

  const menuOptions = document.getElementById('menu-options');
  const mainOptions = document.getElementById('main-options-products');

  toggleMenu.addEventListener('click', function () {
    menuOptions.classList.toggle('is-active');
  });
  toggleMenuProducts.addEventListener('click', function () {
    mainOptions.classList.toggle('is-active');
  });
});


const radioInputs = document.querySelectorAll('.radio input');
const contentSections = document.querySelectorAll('.menu-column');
const initialOption = 3;

const initialContent = document.querySelector(`.menu-column[data-option="${initialOption}"]`);
if (initialContent) {
  initialContent.style.display = 'block';
}

radioInputs.forEach((input) => {
  input.addEventListener('change', (event) => {
    const selectedOption = event.target.parentElement.getAttribute('data-option');

    contentSections.forEach((section) => {
      section.style.display = 'none';
    });

    const selectedContent = document.querySelector(`.menu-column[data-option="${selectedOption}"]`);
    if (selectedContent) {
      selectedContent.style.display = 'block';
    }
  });
});