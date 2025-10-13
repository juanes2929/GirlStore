// ==============================
// CARGAR PRODUCTOS DINÁMICOS
// ==============================
window.addEventListener('DOMContentLoaded', function () {
  fetch('/ProdCat', { method: 'GET' })
    .then(response => response.json())
    .then(data => {
      const catalogos = [...new Set(data.map(item => item[item.length - 1]))];

      catalogos.forEach(catalogo => {
        const productos = data.filter(item => item[item.length - 1] === catalogo);
        const contenedor = document.querySelector(`#${catalogo.toLowerCase()} .products`);
        if (!contenedor) return;

        contenedor.innerHTML = '';

        productos.forEach(prod => {
          const [id, nombre, imagen, precio] = prod;

          const card = document.createElement('div');
          card.classList.add('product-card');
          card.innerHTML = `
            <img src="${imagen}" alt="${nombre}">
            <div class="product-info">
              <h3>${nombre}</h3>
              <p class="price">COP $${parseInt(precio).toLocaleString()}</p>
              <button class="add-btn" data-name="${nombre}" data-price="${precio}">Agregar</button>
            </div>
          `;
          contenedor.appendChild(card);
        });
      });

      activarBotonesCarrito();
      initCarruseles();
    })
    .catch(error => console.error('Error cargando productos:', error));
});

// ==============================
// ANIMACIÓN DE HEADER Y SCROLL
// ==============================
const header = document.getElementById("header");
window.addEventListener("scroll", () => {
  header.classList.toggle("scrolled", window.scrollY > 50);

  document.querySelectorAll("[data-animate]").forEach((el) => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight - 100) el.classList.add("visible");
  });
});

function smoothScrollTo(target) {
  const start = window.scrollY;
  const end = document.querySelector(target).offsetTop - 60;
  const duration = 800;
  let startTime = null;

  function animation(currentTime) {
    if (!startTime) startTime = currentTime;
    const progress = currentTime - startTime;
    const ease = progress / duration < 1
      ? 1 - Math.pow(1 - progress / duration, 3)
      : 1;
    window.scrollTo(0, start + (end - start) * ease);
    if (progress < duration) requestAnimationFrame(animation);
  }
  requestAnimationFrame(animation);
}

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    const target = link.getAttribute("href");
    smoothScrollTo(target);
  });
});

// ==============================
// SISTEMA DE CARRITO
// ==============================
const cartBtn = document.getElementById("cart-btn");
const cartModal = document.getElementById("cart-modal");
const closeCart = document.getElementById("close-cart");
const cartItemsElem = document.getElementById("cart-items");
const totalText = document.getElementById("total");
const clearCart = document.getElementById("clear-cart");
const buyBtn = document.getElementById("buy-btn");
const cartCount = document.getElementById("cart-count");

let cart = [];

function updateCart() {
  cartItemsElem.innerHTML = "";
  let total = 0;
  cart.forEach((item, i) => {
    total += item.price;
    const li = document.createElement("li");
    li.innerHTML = `
      <img src="${item.img}" alt="${item.name}" class="cart-item-img">
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-price">COP $${item.price.toLocaleString()}</div>
      </div>
      <span class="remove-item" data-i="${i}">✖</span>
    `;
    cartItemsElem.appendChild(li);
  });
  totalText.textContent = `Total: COP $${total.toLocaleString()}`;
  cartCount.textContent = cart.length;
}

function activarBotonesCarrito() {
  document.querySelectorAll(".add-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const name = btn.dataset.name;
      const price = parseInt(btn.dataset.price);
      const img = btn.parentElement.parentElement.querySelector("img").src;
      cart.push({ name, price, img });
      updateCart();
    });
  });
}

cartBtn.onclick = () => cartModal.classList.add("active");
closeCart.onclick = () => cartModal.classList.remove("active");
clearCart.onclick = () => { cart = []; updateCart(); };

buyBtn.onclick = () => {
  if (cart.length === 0) {
    alert("Tu carrito está vacío.");
    return;
  }
  alert("¡Gracias por tu compra!");
  cart = [];
  updateCart();
  cartModal.classList.remove("active");
};

cartItemsElem.addEventListener("click", (e) => {
  if (e.target.dataset.i) {
    cart.splice(e.target.dataset.i, 1);
    updateCart();
  }
});

// ==============================
// CARRUSEL CON FLECHAS + ANIMACIÓN
// ==============================
function initCarruseles() {
  document.querySelectorAll("section").forEach(section => {
    const contenedor = section.querySelector(".products");
    if (!contenedor) return;

    const cards = Array.from(contenedor.querySelectorAll(".product-card"));
    if (cards.length <= 4) return;

    // Crear estructura
    const wrapper = document.createElement("div");
    wrapper.classList.add("carousel-wrapper");
    contenedor.parentNode.insertBefore(wrapper, contenedor);
    wrapper.appendChild(contenedor);

    const prevBtn = document.createElement("button");
    const nextBtn = document.createElement("button");
    prevBtn.className = "carousel-arrow prev";
    nextBtn.className = "carousel-arrow next";
    prevBtn.innerHTML = "&#10094;";
    nextBtn.innerHTML = "&#10095;";
    wrapper.appendChild(prevBtn);
    wrapper.appendChild(nextBtn);

    let startIndex = 0;
    const visible = 4;
    let interval;

    // Mostrar visibles con animación
    function render() {
      // contenedor.style.opacity = "0";
      setTimeout(() => {
        contenedor.innerHTML = "";
        for (let i = 0; i < visible; i++) {
          const index = (startIndex + i) % cards.length;
          contenedor.appendChild(cards[index]);
        }
        contenedor.style.opacity = "1";
      }, 250);
    }

    function next() {
      startIndex = (startIndex + 1) % cards.length;
      render();
    }

    function prev() {
      startIndex = (startIndex - 1 + cards.length) % cards.length;
      render();
    }

    nextBtn.addEventListener("click", () => {
      next();
      resetAuto();
    });

    prevBtn.addEventListener("click", () => {
      prev();
      resetAuto();
    });

    function startAuto() {
      interval = setInterval(next, 5000);
    }

    function resetAuto() {
      clearInterval(interval);
      startAuto();
    }

    wrapper.addEventListener("mouseenter", () => clearInterval(interval));
    wrapper.addEventListener("mouseleave", startAuto);

    render();
    startAuto();
  });
}
