document.addEventListener("DOMContentLoaded", () => {
  // === REFERENCIAS A SECCIONES ===
  const sections = {
    Catalogos: document.querySelector("#admin"), // sección de catálogos
    Productos: document.querySelector("#productos"),
    Usuarios: document.querySelector("#usuarios"),
    Ventas: document.querySelector("#ventas"),
    Reportes: document.querySelector("#reportes"),
  };

  const navLinks = document.querySelectorAll("nav a[data-section]");

  // === CAMBIO DE SECCIONES ===
  function showSection(sectionName) {
    Object.keys(sections).forEach((key) => {
      if (sections[key]) {
        if (key === sectionName) {
          sections[key].style.display = "block";
          sections[key].style.opacity = "1";
          sections[key].style.animation = "fadeInUp 0.5s ease";
        } else {
          sections[key].style.display = "none";
          sections[key].style.opacity = "0";
        }
      }
    });
  }

  // === ASIGNAR EVENTOS A LOS LINKS DEL NAV ===
  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const sectionName = e.target.dataset.section;
      if (sectionName) {
        e.preventDefault();
        showSection(sectionName);

        // Cargar dinámicamente si se requiere
        if (sectionName === "Catalogos") loadCatalogos?.();
        if (sectionName === "Productos") loadProductos?.();
        if (sectionName === "Usuarios") loadUsuarios?.();
        if (sectionName === "Reportes") initReportes?.();
      }
    });
  });

  // === MOSTRAR POR DEFECTO CATÁLOGOS ===
  showSection("Catalogos");

  // === FUNCIONES EXISTENTES ===
  const modal = document.getElementById("catalogModal");
  const openModalBtn = document.getElementById("openModalBtn");
  const closeModal = document.getElementById("closeModal");
  const cancelModal = document.getElementById("cancelModal");
  const catalogForm = document.getElementById("catalogForm");
  const catalogBody = document.getElementById("catalogBody");
  const modalTitle = document.getElementById("modalTitle");

  let editMode = false;
  let currentId = null;

  const open = () => modal.classList.add("active");
  const close = () => {
    modal.classList.remove("active");
    catalogForm.reset();
    editMode = false;
    currentId = null;
    modalTitle.textContent = "Agregar Catálogo";
  };

  if (openModalBtn && closeModal && cancelModal) {
    openModalBtn.addEventListener("click", open);
    closeModal.addEventListener("click", close);
    cancelModal.addEventListener("click", close);
  }

  // === CARGAR CATÁLOGOS ===
  async function loadCatalogos() {
    const res = await fetch("/catalogo");
    const data = await res.json();
    if (!catalogBody) return;
    catalogBody.innerHTML = "";

    data.forEach((cat) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${cat[0]}</td>
        <td>${cat[1]}</td>
        <td>${cat[2]}</td>
        <td>
          <button class="edit" data-id="${cat[0]}" title="Editar">✏️</button>
          <button class="delete" data-id="${cat[0]}" title="Eliminar">🗑️</button>
        </td>
      `;
      catalogBody.appendChild(tr);
    });
  }

  // === GUARDAR / EDITAR CATÁLOGO ===
  if (catalogForm) {
    catalogForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const Id_catalogo = document.getElementById("id_catalogo").value.trim();
      const Name_catalogo = document.getElementById("name_catalogo").value.trim();

      if (!Id_catalogo || !Name_catalogo) {
        Swal.fire("Campos vacíos", "Completa todos los campos", "warning");
        return;
      }

      const payload = { Id_catalogo, Name_catalogo };
      const url = editMode ? `/catalogo/${currentId}` : "/catalogo";
      const method = editMode ? "PUT" : "POST";

      try {
        const res = await fetch(url, {
          method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await res.json();

        if (result.success) {
          Swal.fire({
            icon: "success",
            title: "Éxito",
            text: result.message,
            timer: 1800,
            confirmButtonColor: "#e62e7a",
            showConfirmButton: false,
          });
          close();
          loadCatalogos();
        } else {
          Swal.fire("Error", result.message, "error");
        }
      } catch {
        Swal.fire("Error", "No se pudo conectar con el servidor", "error");
      }
    });
  }

  // === EDITAR / ELIMINAR CATÁLOGO ===
  if (catalogBody) {
    catalogBody.addEventListener("click", async (e) => {
      if (e.target.classList.contains("edit")) {
        editMode = true;
        currentId = e.target.dataset.id;
        const row = e.target.closest("tr");
        document.getElementById("id_catalogo").value = row.children[1].textContent;
        document.getElementById("name_catalogo").value = row.children[2].textContent;
        modalTitle.textContent = "Editar Catálogo";
        open();
      }

      if (e.target.classList.contains("delete")) {
        const id = e.target.dataset.id;
        Swal.fire({
          title: "¿Eliminar catálogo?",
          text: "Esta acción no se puede deshacer",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#e62e7a",
          cancelButtonColor: "#aaa",
          confirmButtonText: "Sí, eliminar",
          cancelButtonText: "Cancelar",
        }).then(async (result) => {
          if (result.isConfirmed) {
            const res = await fetch(`/catalogo/${id}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
              Swal.fire("Eliminado", data.message, "success");
              loadCatalogos();
            } else {
              Swal.fire("Error", data.message, "error");
            }
          }
        });
      }
    });
  }

  // === CARGA INICIAL ===
  loadCatalogos();
  loadUsuarios(); 
  loadProductos();
});

// === VARIABLES ===
let allProductos = [];
let currentPage = 1;
const itemsPerPage = 10;
let sortField = null;
let sortOrder = "asc";

// === CARGAR PRODUCTOS ===
async function loadProductos() {
  const res = await fetch("/productos");
  allProductos = await res.json();
  renderProductos();
}

// === RENDERIZAR PRODUCTOS CON PAGINACIÓN Y ORDEN ===
function renderProductos() {
  const productoBody = document.getElementById("productoBody");
  if (!productoBody) return;

  let productos = [...allProductos];

  // Ordenamiento
    if (sortField) {
    productos.sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];

        if (sortField === "Price") {
        valA = parseFloat(valA);
        valB = parseFloat(valB);
        }

        if (sortField === "IsActive") {
        // true debe ir antes que false cuando ascendente
        valA = a.IsActive ? 1 : 0;
        valB = b.IsActive ? 1 : 0;
        }

        if (valA < valB) return sortOrder === "asc" ? -1 : 1;
        if (valA > valB) return sortOrder === "asc" ? 1 : -1;
        return 0;
    });
    }


  // Paginación
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const currentItems = productos.slice(start, end);

  productoBody.innerHTML = "";

  currentItems.forEach((p) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.Id_producto}</td>
      <td>${p.Name_product}</td>
      <td><img src="${p.Img}" alt="img" style="width:50px;height:50px;border-radius:8px;"></td>
      <td>$${new Intl.NumberFormat("es-CO").format(p.Price)}</td>
      <td>${p.Name_catalogo || "Sin catálogo"}</td>
      <td>${p.IsActive ? "Activo" : "Inactivo"}</td>
      <td>
        <button class="edit-prod" data-id="${p.Id_producto}" title="Editar">✏️</button>
        <button class="delete-prod" data-id="${p.Id_producto}" title="Eliminar">🗑️</button>
      </td>
    `;
    productoBody.appendChild(tr);
  });

  renderPagination(productos.length);
}

// === PAGINACIÓN ===
function renderPagination(totalItems) {
  const pagination = document.getElementById("paginationControls");
  pagination.innerHTML = "";

  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    if (i === currentPage) btn.classList.add("active");
    btn.addEventListener("click", () => {
      currentPage = i;
      renderProductos();
    });
    pagination.appendChild(btn);
  }
}

// === MODAL PRODUCTO ===
const productoModal = document.getElementById("productoModal");
const openProductoModal = document.getElementById("openProductoModal");
const closeProductoModal = document.getElementById("closeProductoModal");
const cancelProductoModal = document.getElementById("cancelProductoModal");
const productoForm = document.getElementById("productoForm");
const productoModalTitle = document.getElementById("productoModalTitle");
const priceInput = document.getElementById("price_product");

let editProductoMode = false;
let currentProdId = null;

const openProd = () => productoModal.classList.add("active");
const closeProd = () => {
  productoModal.classList.remove("active");
  productoForm.reset();
  editProductoMode = false;
  currentProdId = null;
  productoModalTitle.textContent = "Agregar Producto";
};

if (openProductoModal && closeProductoModal && cancelProductoModal) {
  openProductoModal.addEventListener("click", async () => {
    await loadCatalogOptions();
    openProd();
  });
  closeProductoModal.addEventListener("click", closeProd);
  cancelProductoModal.addEventListener("click", closeProd);
}

// === FORMATEO DE PRECIO (COP) ===
priceInput.addEventListener("input", (e) => {
  let value = e.target.value.replace(/\D/g, "");
  if (!value) {
    e.target.value = "";
    return;
  }
  e.target.value = new Intl.NumberFormat("es-CO").format(value);
});

// === CARGAR CATÁLOGOS EN SELECT ===
async function loadCatalogOptions(selectedId = null) {
  const res = await fetch("/catalogo");
  const catalogs = await res.json();
  const select = document.getElementById("id_cat");
  select.innerHTML = "";

  catalogs.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c[0];
    opt.textContent = c[2];
    if (selectedId && selectedId == c[0]) opt.selected = true;
    select.appendChild(opt);
  });
}

// === GUARDAR PRODUCTO ===
productoForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const Name_product = document.getElementById("name_product").value.trim();
  const Img = document.getElementById("img_product").value.trim();
  let Price = document.getElementById("price_product").value.trim();
  Price = Price.replace(/\./g, ""); // quitar puntos
  const Id_cat = document.getElementById("id_cat").value;
  const IsActive = document.getElementById("is_active").checked;

  if (!Name_product || !Img || !Price || !Id_cat) {
    Swal.fire("Campos vacíos", "Completa todos los campos", "warning");
    return;
  }

  const payload = { Name_product, Img, Price, Id_cat, IsActive };
  const url = editProductoMode ? `/productos/${currentProdId}` : "/productos";
  const method = editProductoMode ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await res.json();

    if (result.success) {
      Swal.fire({
        icon: "success",
        title: "Éxito",
        text: result.message,
        timer: 1800,
        confirmButtonColor: "#e62e7a",
        showConfirmButton: false,
      });
      closeProd();
      loadProductos();
    } else {
      Swal.fire("Error", result.message, "error");
    }
  } catch {
    Swal.fire("Error", "No se pudo conectar con el servidor", "error");
  }
});

// === EDITAR / ELIMINAR PRODUCTO ===
document.getElementById("productoBody").addEventListener("click", async (e) => {
  if (e.target.classList.contains("edit-prod")) {
    editProductoMode = true;
    currentProdId = e.target.dataset.id;

    const res = await fetch(`/productos/${currentProdId}`);
    const data = await res.json();

    document.getElementById("name_product").value = data.Name_product;
    document.getElementById("img_product").value = data.Img;
    document.getElementById("price_product").value = new Intl.NumberFormat("es-CO").format(data.Price);
    await loadCatalogOptions(data.Id_cat);
    document.getElementById("is_active").checked = data.IsActive;

    productoModalTitle.textContent = "Editar Producto";
    openProd();
  }

  if (e.target.classList.contains("delete-prod")) {
    const id = e.target.dataset.id;
    Swal.fire({
      title: "¿Desactivar producto?",
      text: "Esta acción lo marcará como inactivo.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#e62e7a",
      cancelButtonColor: "#aaa",
      confirmButtonText: "Sí, desactivar",
      cancelButtonText: "Cancelar",
    }).then(async (result) => {
      if (result.isConfirmed) {
        const res = await fetch(`/productos/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
          Swal.fire("Hecho", data.message, "success");
          loadProductos();
        } else {
          Swal.fire("Error", data.message, "error");
        }
      }
    });
  }
});

// === ORDENAR POR PRECIO / CATÁLOGO ===
document.getElementById("sortPrice")?.addEventListener("click", () => {
  toggleSort("Price");
});
document.getElementById("sortCatalog")?.addEventListener("click", () => {
  toggleSort("Name_catalogo");
});
document.getElementById("sortEstado")?.addEventListener("click", () => {
  toggleSort("IsActive");
});


function toggleSort(field) {
  if (sortField === field) {
    sortOrder = sortOrder === "asc" ? "desc" : "asc";
  } else {
    sortField = field;
    sortOrder = "asc";
  }
  currentPage = 1;
  renderProductos();
}

// ==== USUARIOS ====
let allUsuarios = [];
let currentPageUser = 1;
const usersPerPage = 10;
let userSortField = null;
let userSortOrder = "asc";

// === Cargar todos los usuarios ===
async function loadUsuarios() {
  try {
    const res = await fetch("/usuarios");
    if (!res.ok) throw new Error("Error al cargar usuarios");
    allUsuarios = await res.json();
    renderUsuarios();
  } catch (error) {
    console.error("Error al cargar usuarios:", error);
    Swal.fire("Error", "No se pudieron cargar los usuarios", "error");
  }
}

// === Renderizar tabla ===
function renderUsuarios() {
  const body = document.getElementById("usuarioBody");
  if (!body) return;

  let usuarios = [...allUsuarios];

  // Ordenamiento
  if (userSortField) {
    usuarios.sort((a, b) => {
      let valA = a[userSortField];
      let valB = b[userSortField];

      if (userSortField === "IsAdmin") {
        valA = parseInt(a.IsAdmin);
        valB = parseInt(b.IsAdmin);
      }

      if (valA < valB) return userSortOrder === "asc" ? -1 : 1;
      if (valA > valB) return userSortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }

  // Paginación
  const start = (currentPageUser - 1) * usersPerPage;
  const end = start + usersPerPage;
  const currentUsers = usuarios.slice(start, end);

  // Renderizar filas
  body.innerHTML = "";
  currentUsers.forEach((u) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${u.IdUser}</td>
      <td>${u.UserName}</td>
      <td>${u.Phone}</td>
      <td>${u.Email}</td>
      <td>${u.Direction}</td>
      <td>${u.IsAdmin == 1 ? "Administrador" : "Usuario"}</td>
      <td>
        <button class="edit-user" data-id="${u.IdUser}" title="Editar">✏️</button>
        <button class="delete-user" data-id="${u.IdUser}" title="Eliminar">🗑️</button>
      </td>
    `;
    body.appendChild(tr);
  });

  renderPaginationUsuarios(usuarios.length);
}

// === Paginación ===
function renderPaginationUsuarios(total) {
  const pag = document.getElementById("paginationUsuarios");
  pag.innerHTML = "";
  const totalPages = Math.ceil(total / usersPerPage);
  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    if (i === currentPageUser) btn.classList.add("active");
    btn.addEventListener("click", () => {
      currentPageUser = i;
      renderUsuarios();
    });
    pag.appendChild(btn);
  }
}

// === Modal ===
const usuarioModal = document.getElementById("usuarioModal");
const openUsuarioModal = document.getElementById("openUsuarioModal");
const closeUsuarioModal = document.getElementById("closeUsuarioModal");
const cancelUsuarioModal = document.getElementById("cancelUsuarioModal");
const usuarioForm = document.getElementById("usuarioForm");
const usuarioModalTitle = document.getElementById("usuarioModalTitle");

let editUserMode = false;
let currentUserId = null;

const openUser = () => usuarioModal.classList.add("active");
const closeUser = () => {
  usuarioModal.classList.remove("active");
  usuarioForm.reset();
  editUserMode = false;
  currentUserId = null;
  usuarioModalTitle.textContent = "Agregar Usuario";
};

openUsuarioModal?.addEventListener("click", openUser);
closeUsuarioModal?.addEventListener("click", closeUser);
cancelUsuarioModal?.addEventListener("click", closeUser);

// === Guardar usuario ===
usuarioForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    UserName: document.getElementById("username").value.trim(),
    Phone: document.getElementById("phone").value.trim(),
    Email: document.getElementById("email").value.trim(),
    Direction: document.getElementById("direction").value.trim(),
    Pswd: document.getElementById("password").value.trim(),
    IsAdmin: document.getElementById("is_admin").checked ? 1 : 0,
  };

  if (!payload.UserName || !payload.Phone || !payload.Email || !payload.Direction) {
    Swal.fire("Campos vacíos", "Completa todos los campos obligatorios", "warning");
    return;
  }

  const url = editUserMode ? `/usuarios/${currentUserId}` : "/usuarios";
  const method = editUserMode ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await res.json();
    if (result.success) {
      Swal.fire("Éxito", result.message, "success");
      closeUser();
      loadUsuarios();
    } else {
      Swal.fire("Error", result.message, "error");
    }
  } catch (error) {
    Swal.fire("Error", "Error al guardar el usuario", "error");
    console.error(error);
  }
});

// === Editar / Eliminar usuario ===
document.getElementById("usuarioBody")?.addEventListener("click", async (e) => {
  if (e.target.classList.contains("edit-user")) {
    editUserMode = true;
    currentUserId = e.target.dataset.id;
    const res = await fetch(`/usuarios/${currentUserId}`);
    const data = await res.json();

    document.getElementById("username").value = data.UserName;
    document.getElementById("phone").value = data.Phone;
    document.getElementById("email").value = data.Email;
    document.getElementById("direction").value = data.Direction;
    document.getElementById("is_admin").checked = parseInt(data.IsAdmin) === 1;

    usuarioModalTitle.textContent = "Editar Usuario";
    openUser();
  }

  if (e.target.classList.contains("delete-user")) {
    const id = e.target.dataset.id;
    Swal.fire({
      title: "¿Eliminar usuario?",
      text: "Esta acción no se puede deshacer",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#e62e7a",
      cancelButtonColor: "#aaa",
      confirmButtonText: "Sí, eliminar",
      cancelButtonText: "Cancelar",
    }).then(async (resu) => {
      if (resu.isConfirmed) {
        const res = await fetch(`/usuarios/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
          Swal.fire("Eliminado", data.message, "success");
          loadUsuarios();
        } else {
          Swal.fire("Error", data.message, "error");
        }
      }
    });
  }
});

// === Ordenar por nombre / rol ===
document.getElementById("sortUserName")?.addEventListener("click", () => toggleUserSort("UserName"));
document.getElementById("sortRol")?.addEventListener("click", () => toggleUserSort("IsAdmin"));

function toggleUserSort(field) {
  if (userSortField === field) {
    userSortOrder = userSortOrder === "asc" ? "desc" : "asc";
  } else {
    userSortField = field;
    userSortOrder = "asc";
  }
  currentPageUser = 1;
  renderUsuarios();
}


// ============ SECCIÓN REPORTES ============

function initReportes() {
  console.log("Sección Reportes activa");

  document.getElementById("reporteUsuarios")?.addEventListener("click", () => {
    window.open("/reportes/usuarios", "_blank");
  });

  document.getElementById("reporteProductos")?.addEventListener("click", () => {
    window.open("/reportes/productos", "_blank");
  });

  document.getElementById("reporteCatalogos")?.addEventListener("click", () => {
    window.open("/reportes/catalogos", "_blank");
  });
}

