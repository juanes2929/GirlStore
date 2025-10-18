// ==============================
// CARGAR PRODUCTOS DINÁMICOS
// Obtiene catálogos+productos desde /ProdCat y
// crea tarjetas dentro de cada sección (Trendy/Montoc/Milagros)
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
              <button class="add-btn" 
                      data-id="${id}" 
                      data-name="${nombre}" 
                      data-price="${precio}" 
                      data-img="${imagen}">
                Agregar
              </button>
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
// Cambia estilo del header al hacer scroll y revela secciones con data-animate
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
// Carrito en memoria: agrega productos, calcula total y permite comprar
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
  document.querySelectorAll(".add-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.dataset.id);
      const name = btn.dataset.name;
      const price = parseInt(btn.dataset.price);
      const img = btn.dataset.img;

      cart.push({ id, name, price, img });
      updateCart();
    });
  });
}



cartBtn.onclick = () => cartModal.classList.add("active");
closeCart.onclick = () => {
  cartModal.classList.remove("active");
  cartBtn.focus(); // mueve el foco al botón del carrito
};

clearCart.onclick = () => { cart = []; updateCart(); };

/* COMPRAR EN PAGINA: envía carrito al backend (requiere sesión iniciada) */
buyBtn.onclick = async () => {
  if (cart.length === 0) {
    Swal.fire({
      title: "Carrito vacío",
      text: "Agrega productos antes de comprar.",
      icon: "warning",
      confirmButtonColor: "#e62e7a",
    });
    return;
  }

  const total = cart.reduce((acc, item) => acc + item.price, 0);

  try {
    const resCompra = await fetch("/comprar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        carrito: cart.map(item => ({
          id: item.id || null,
          name: item.name,
          price: item.price,
          cantidad: 1,
        })),
        total,
      }),
    });

    const dataCompra = await resCompra.json();

    if (dataCompra.success) {
      // Cerrar el modal de carrito inmediatamente
      cartModal.classList.remove("active");

      // Mostrar alerta de éxito
      Swal.fire({
        title: "¡Compra exitosa!",
        text: "Tu pedido ha sido registrado con método de pago Tarjeta.",
        icon: "success",
        confirmButtonColor: "#e62e7a",
      });

      // Vaciar carrito y actualizar contador
      cart = [];
      updateCart();
    } else {
      Swal.fire({
        title: "Error",
        text: dataCompra.message || "No se pudo registrar la compra.",
        icon: "error",
        confirmButtonColor: "#e62e7a",
      });
    }
  } catch (err) {
    console.error(err);
    Swal.fire({
      title: "Error",
      text: "Ocurrió un error al procesar la compra.",
      icon: "error",
      confirmButtonColor: "#e62e7a",
    });
  }
};

// ==============================
// CARRUSEL CON FLECHAS + ANIMACIÓN
// Reconstruye el contenedor para mostrar 4 ítems a la vez y auto-avanza
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

