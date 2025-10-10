// ---- Carrito funcional ----
const addToCartButtons = document.querySelectorAll(".add-to-cart");
const cartBtn = document.getElementById("cart-btn");
const cartModal = document.getElementById("cart-modal");
const closeCart = document.getElementById("close-cart");
const cartItemsElem = document.getElementById("cart-items");
const totalText = document.getElementById("total");
const clearCartBtn = document.getElementById("clear-cart");
const buyBtn = document.getElementById("buy-btn");
const cartCount = document.getElementById("cart-count");

let cart = [];

function updateCartView() {
  cartItemsElem.innerHTML = "";
  let total = 0;
  cart.forEach((item, idx) => {
    total += item.price;
    const li = document.createElement("li");
    li.innerHTML = `
      ${item.name} — COP $${item.price.toLocaleString()} 
      <span class="trash" data-index="${idx}">🗑️</span>
    `;
    cartItemsElem.appendChild(li);
  });
  totalText.textContent = `Total: COP $${total.toLocaleString()}`;
  cartCount.textContent = cart.length;
}

// Agregar al carrito
addToCartButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const name = btn.dataset.name;
    const price = parseInt(btn.dataset.price);
    cart.push({ name, price });
    updateCartView();
  });
});

// Mostrar modal carrito
cartBtn.addEventListener("click", () => {
  cartModal.classList.remove("hidden");
});

// Cerrar modal (botón “Cerrar”)
closeCart?.addEventListener("click", () => {
  cartModal.classList.add("hidden");
});

// Limpiar carrito
clearCartBtn.addEventListener("click", () => {
  cart = [];
  updateCartView();
});

// Comprar acción
buyBtn.addEventListener("click", () => {
  if (cart.length === 0) {
    alert("Tu carrito está vacío.");
    return;
  }
  alert("¡Gracias por tu compra!");
  cart = [];
  updateCartView();
  cartModal.classList.add("hidden");
});

// Remover item individual
cartItemsElem.addEventListener("click", (e) => {
  if (e.target.classList.contains("trash")) {
    const idx = parseInt(e.target.dataset.index);
    cart.splice(idx, 1);
    updateCartView();
  }
});

// ---- Carrusel automático ----
const carouselInner = document.querySelector(".carousel-inner");
let slideIndex = 0;

function showNextSlide() {
  slideIndex++;
  const totalSlides = carouselInner.children.length;
  if (slideIndex >= totalSlides) {
    slideIndex = 0;
  }
  const offset = -slideIndex * 100; // porcentaje para mover
  carouselInner.style.transform = `translateX(${offset}%)`;
}

// Cambiar cada 5 segundos
setInterval(showNextSlide, 5000);

// ---- Mejora del scroll del menú ----
document.querySelectorAll('.nav-menu a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    const headerOffset = 70; // altura del header
    const elementPosition = target.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = elementPosition - headerOffset;

    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    });
  });
});
