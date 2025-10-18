# GirlStore

Aplicación web sencilla de tienda de maquillaje y cosméticos construida con Python (Flask) y MySQL. Incluye autenticación básica, panel de administración, catálogo de productos, carrito de compras, gestión de ventas y generación de reportes en PDF.

## Contenidos
- Qué es este proyecto
- Requisitos previos
- Instalación paso a paso (Windows)
- Configuración de la base de datos
- Cómo ejecutar la aplicación
- Usuarios de prueba
- Estructura del proyecto
- Endpoints (API) principales y ejemplos
- Flujo de la interfaz (pantallas)
- Reportes en PDF
- Solución de problemas
- Mejoras recomendadas

---

## Qué es este proyecto
GirlStore es una app educativa para aprender los fundamentos de un stack típico web:
- Backend en Flask (Python), sirviendo HTML (Jinja) y una API JSON.
- Base de datos MySQL con tablas de usuarios, catálogos, productos, ventas y detalles de ventas.
- Frontend con HTML, CSS y JavaScript simple (sin frameworks) en `templates/` y `static/`.

Con esto puedes:
- Registrarte, iniciar sesión y cerrar sesión.
- Navegar productos por catálogo y usar un carrito local.
- Comprar (registrar ventas) si has iniciado sesión.
- Usar un panel de administración (solo rol admin) para CRUD de catálogos, productos, usuarios y ventas.
- Generar reportes en PDF de usuarios, productos, catálogos y ventas.

---

## Requisitos previos
- Python 3.10+ (recomendado 3.11 o superior)
- MySQL 8.x o MariaDB compatible
- Pip (gestor de paquetes de Python)

Opcional pero recomendado en Windows:
- PowerShell (ya incluido)
- Editor de código (VS Code, Cursor, etc.)

---

## Instalación paso a paso (Windows)
1) Clona o descarga este repositorio.

2) Crea y activa un entorno virtual de Python (opcional, recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

3) Instala las dependencias:

```powershell
pip install -r requirements.txt
```

4) Configura la base de datos (ver siguiente sección) y confirma credenciales en `src/service/connection.py`.

---

## Configuración de la base de datos
1) Abre tu cliente MySQL (Workbench, consola, etc.) con un usuario que tenga permisos para crear BD/tablas.

2) Ejecuta todo el contenido de `src/bd.sql`. Esto:
   - Crea la base de datos `GirlStore`.
   - Crea las tablas: `Users`, `Catalogo`, `Productos`, `Ventas`, `Detalle_Venta`.
   - Inserta datos de ejemplo (usuarios, catálogos, productos y una venta de ejemplo).

3) Revisa o ajusta credenciales de conexión en:
   - `src/service/connection.py` → método `get_data_conection()`
     - Usuario por defecto: `root`
     - Contraseña por defecto: vacía
     - Host: `localhost`
     - Puerto: `3306`
     - Base de datos: `GirlStore`

Si tu MySQL usa otra contraseña/usuario, cámbialo ahí. Ejemplo:

```python
"user": "mi_usuario",
"pwd": "mi_contraseña",
```

---

## Cómo ejecutar la aplicación
Desde la raíz del proyecto (donde está este README):

```powershell
python src/main.py
```

Por defecto inicia en `http://localhost:9000/home` (puerto 9000). Si ya está ocupado, cambia el puerto en la última línea de `src/main.py`.

---

## Usuarios de prueba
Estos se crean al ejecutar `src/bd.sql`:

- Administrador:
  - Email: `nicol@gmail.com`
  - Contraseña: `nicol123`
- Usuario normal:
  - Email: `juan@gmail.com`
  - Contraseña: `juan123`

Con el usuario admin verás el enlace "Administrar" y podrás acceder al panel `/admin`.

---

## Estructura del proyecto
```
src/
  main.py                # App Flask: rutas web y API, sesión y reportes PDF
  bd.sql                 # Script SQL para crear BD, tablas y datos de ejemplo
  service/
    connection.py        # Conexión MySQL y funciones auxiliares
  templates/             # Vistas HTML (Jinja)
    home.html            # Página de inicio con secciones por catálogo y carrito
    login.html           # Formulario de inicio de sesión
    registro.html        # Formulario de registro
    admin.html           # Panel de administración (solo admin)
  static/
    css/                 # Estilos
    js/                  # Lógica del cliente (carrito, CRUD admin, etc.)
    img/                 # Imágenes
```

Puntos clave del código:
- `src/main.py` define todas las rutas (web y API), maneja sesión con `Flask` y genera PDFs con `reportlab`.
- `src/service/connection.py` gestiona la conexión MySQL (usando `mysql-connector-python`).
- Las plantillas en `templates/` usan datos de sesión (`session['Name']`, `session['Rol']`) para mostrar opciones.

---

## Endpoints (API) principales y ejemplos
Formato general de respuestas: JSON.

Autenticación y sesión
- `GET /registro` → HTML de registro
- `POST /registro` → Crea un usuario desde formulario (`multipart/form-data`)
- `GET /login` → HTML de login
- `POST /login` → Inicia sesión. Body (form): `email`, `password`
- `GET /logout` → Cierra sesión y redirige a inicio
- `GET /check_session` → `{ "logged_in": true|false }`

Catálogos
- `GET /catalogo` → Lista catálogos
- `POST /catalogo` → Crea catálogo. JSON:
  ```json
  { "Id_catalogo": 10, "Name_catalogo": "MiMarca" }
  ```
- `PUT /catalogo/<id>` → Actualiza por `Id_cat`. JSON como arriba
- `DELETE /catalogo/<id>` → Elimina por `Id_cat`

Productos
- `GET /productos` → Lista productos con info de catálogo
- `GET /productos/<id>` → Detalle de un producto
- `POST /productos` → Crea. JSON:
  ```json
  {
    "Name_product": "Labial",
    "Img": "https://...",
    "Price": "25000",
    "Id_cat": 1,
    "IsActive": true
  }
  ```
- `PUT /productos/<id>` → Actualiza con JSON similar
- `DELETE /productos/<id>` → Desactiva (`IsActive = FALSE`)

Usuarios
- `GET /usuarios` → Lista usuarios
- `GET /usuarios/<id>` → Detalle
- `POST /usuarios` → Crea. JSON:
  ```json
  {
    "UserName": "Ana",
    "Phone": "3001234567",
    "Email": "ana@example.com",
    "Direction": "Calle 1",
    "Pswd": "secreto",
    "IsAdmin": false
  }
  ```
- `PUT /usuarios/<id>` → Actualiza (sin cambiar contraseña en este endpoint)
- `DELETE /usuarios/<id>` → Elimina

Ventas y compra
- `POST /comprar` → Requiere sesión iniciada. JSON:
  ```json
  {
    "carrito": [{ "id": 2, "price": 15000, "cantidad": 1 }],
    "total": 15000
  }
  ```
- `GET /ventas` → Lista ventas con conteo de items
- `GET /ventas/<id>` → Detalle de venta (incluye productos)
- `POST /ventas` → Crea venta desde admin. JSON flexible en claves de detalle (`Id_producto`/`id`, `Cantidad`/`cantidad`)
- `PUT /ventas/<id>` → Actualiza cabecera y, opcionalmente, reemplaza detalles
- `DELETE /ventas/<id>` → Elimina venta y sus detalles

Reportes (PDF)
- `GET /reportes/usuarios`
- `GET /reportes/productos`
- `GET /reportes/catalogos`
- `GET /reportes/ventas`

---

## Flujo de la interfaz (pantallas)
- `home.html`: Muestra secciones por catálogo (Trendy, Montoc, Milagros) y el carrito. Si hay sesión activa, saluda por nombre; si es admin, muestra enlace a `Administrar`.
- `login.html`: Formulario de acceso. Enlace a registro.
- `registro.html`: Formulario de registro de usuario.
- `admin.html` (solo admin): Panel con pestañas para Catálogos, Productos, Usuarios, Ventas y Reportes. Incluye tablas, ordenamiento, paginación y modales para crear/editar.

El JS en `static/js/` maneja la interacción (cargar datos vía fetch, abrir/cerrar modales, enviar formularios, carrito, etc.).

---

## Reportes en PDF
Se generan con `reportlab` y se entregan directamente al navegador. Cada reporte incluye:
- Logo, título, tabla de datos y pie con fecha/hora.
- Estilos básicos (colores, rejilla, filas alternadas).

Puedes abrirlos en una pestaña o descargar desde el navegador.

---

## Solución de problemas (FAQ)
- Error de conexión MySQL (Access denied): verifica usuario/contraseña en `src/service/connection.py` y que MySQL esté iniciado.
- Puerto 9000 en uso: cambia el `port=9000` al final de `src/main.py` por otro (p.ej. 5000).
- PDFs no se ven: asegúrate de tener `reportlab` instalado (`pip show reportlab`) y que el navegador no bloquee popups.
- Login falla con usuarios de ejemplo: ejecuta `src/bd.sql` contra tu servidor MySQL correcto (la BD debe llamarse exactamente `GirlStore`).

---

## Mejoras recomendadas (para producción)
- Hash de contraseñas (p.ej., `werkzeug.security.generate_password_hash` y `check_password_hash`).
- Cambiar el tipo de `Price` a `DECIMAL` en `Productos` (ahora es `VARCHAR`).
- Mover `app.secret_key` y credenciales a variables de entorno.
- Añadir validaciones y manejo de errores más robusto en la API.
- Paginación/filtrado en endpoints de listas.

---

¡Listo! Si seguiste los pasos, deberías poder abrir `http://localhost:9000/home`, registrarte/iniciar sesión y, con el usuario admin, administrar el catálogo y generar reportes.

---

## Cómo funciona el código (para sustentación)

### 1) Arquitectura general
- Backend: `Flask` en `src/main.py` expone páginas HTML y una API JSON para CRUD y reportes.
- Capa de datos: `src/service/connection.py` maneja credenciales, apertura de conexión y consultas a MySQL.
- Vistas (UI): HTML en `src/templates/` con Jinja y estáticos en `src/static/` (CSS/JS/IMG).
- Sesiones: `Flask` guarda en `session` el nombre del usuario y su rol para mostrar opciones y restringir acceso al admin.

### 2) `src/main.py` en detalle
- Configuración inicial: crea la app Flask, activa CORS y define `secret_key`.
- Errores y navegación: redirige 404 a `/home`; `/` redirige a `/home`.
- Registro (`/registro` GET/POST):
  - GET devuelve el formulario HTML.
  - POST valida campos y llama a `ConnectionDB.insert_users()` para insertar en `Users`.
  - Responde JSON indicando éxito/fracaso y, si todo va bien, sugiere navegar a `/login`.
- Login (`/login` GET/POST):
  - GET devuelve el formulario.
  - POST lee `email` y `password`, consulta `Users` y, si coincide, escribe en `session`:
    - `session['Name']`: nombre del usuario.
    - `session['Rol']`: 1 si es admin, 0 si es usuario normal.
  - Responde JSON con mensaje de bienvenida o error.
- Logout (`/logout`): borra la sesión y redirige a `/`.
- Verificación de sesión (`/check_session`): devuelve `{logged_in:true|false}` para que el frontend decida qué mostrar.
- Acceso admin (`/admin`): solo permite entrar si `session['Rol'] == 1`; si no, redirige a `home`.
- Catálogos (`/catalogo`):
  - `GET`: lista catálogos.
  - `POST`: crea.
  - `PUT /catalogo/<id>`: actualiza el catálogo con `Id_cat = id`.
  - `DELETE /catalogo/<id>`: elimina.
- Productos:
  - `GET /productos`: usa `ConnectionDB.get_cat_products()` para traer productos junto con su catálogo (LEFT JOIN). Mapea cada fila a un diccionario JSON.
  - `GET /productos/<id>`: obtiene un solo producto.
  - `POST /productos`: inserta un producto nuevo.
  - `PUT /productos/<id>`: actualiza un producto existente.
  - `DELETE /productos/<id>`: desactiva el producto (soft-delete mediante `IsActive = FALSE`).
- Usuarios:
  - `GET /usuarios`: lista todos con campos básicos (sin contraseñas).
  - `GET /usuarios/<id>`: detalle por ID.
  - `POST /usuarios`: crea usuario (incluye contraseña en texto plano; ver mejoras).
  - `PUT /usuarios/<id>`: actualiza datos (sin contraseña).
  - `DELETE /usuarios/<id>`: elimina definitivamente.
- Ventas (panel/admin y compra):
  - `POST /comprar`: flujo de cliente con carrito. Requiere sesión:
    1) Valida sesión y carrito.
    2) Busca `IdUser` del usuario logueado.
    3) Inserta cabecera en `Ventas` y detalles en `Detalle_Venta`.
  - `GET /ventas`: lista ventas con conteo de ítems.
  - `GET /ventas/<id>`: devuelve cabecera e items (JOIN con `Productos`).
  - `POST /ventas` (admin): crea venta; acepta formatos de claves flexibles en detalles.
  - `PUT /ventas/<id>` (admin): actualiza cabecera y, si vienen detalles, los reemplaza.
  - `DELETE /ventas/<id>` (admin): elimina venta y sus detalles.
- Reportes PDF:
  - Endpoints: `/reportes/usuarios`, `/reportes/productos`, `/reportes/catalogos`, `/reportes/ventas`.
  - Usan `crear_reporte_pdf(...)` que arma un PDF con `reportlab` (logo, títulos, tabla y pie con fecha).

### 3) Capa de datos: `src/service/connection.py`
- `get_data_conection()`: centraliza credenciales de MySQL.
- `iniciarConexion()`: abre la conexión (`mysql-connector-python`) y retorna `(conn, cursor)`; el cursor se usa para ejecutar SQL parametrizado.
- `doQuery(cursor, query, params)`: ejecuta SELECT y devuelve `fetchall()`.
- `insert_users(...)`: inserta en `Users` con transacción (hace `commit`/`rollback` y maneja excepciones).
- `get_cat_products()`: hace un LEFT JOIN `Catalogo` ↔ `Productos` para devolver el catálogo con productos (activos e inactivos si existen).

### 4) Plantillas y estáticos
- `templates/home.html`: muestra secciones por catálogo (Trendy, Montoc, Milagros), botón del carrito y, si hay sesión, saluda por nombre y muestra enlace a Admin si el rol es 1.
- `templates/login.html` y `templates/registro.html`: formularios. El JS asociado envía datos a `/login` y `/registro`.
- `templates/admin.html`: panel con pestañas (Catálogos, Productos, Usuarios, Ventas y Reportes). Usa tablas, paginación, ordenamiento y modales.
- `static/js/*.js`: maneja el consumo de la API (fetch), abre/cierra modales, arma tablas, controla el carrito, envía formularios y descarga reportes.

#### Explicación HTML (plantillas)
- `home.html`:
  - Header fijo: navegación por secciones y botón del carrito.
  - Secciones `#trendy`, `#montoc`, `#milagros`: contenedores `.products` donde el JS inyecta tarjetas.
  - Modal del carrito: lista los productos agregados y permite comprar, vaciar o cerrar.
- `login.html`:
  - Formulario con `id="loginForm"` que al enviar llama a `/login` (POST). El JS intercepta y muestra alertas.
- `registro.html`:
  - Formulario con clase `.register-form` que envía los campos como `FormData` a `/registro` (POST).
- `admin.html`:
  - Secciones ocultables para CRUD de Catálogos, Productos, Usuarios y Ventas; y una sección de Reportes con botones que abren PDFs.

### 5) Ciclo petición-respuesta (ejemplo)
Compra desde `home.html`:
1) El usuario agrega productos al carrito (JS guarda/actualiza el carrito y muestra total).
2) Clic en "Comprar" → el JS hace `POST /comprar` con `{carrito, total}`.
3) Backend valida sesión, obtiene `IdUser`, inserta registro en `Ventas` y líneas en `Detalle_Venta`.
4) Respuesta JSON `{success:true,...}`; el frontend muestra confirmación.

### 6) Seguridad y validaciones (qué hace y qué falta)
Lo que hace:
- Parametriza consultas SQL (evita inyección).
- Usa `session` para rol/usuario y restringir `/admin`.

Lo que falta para producción:
- Hash de contraseñas (actualmente texto plano).
- Validar/normalizar tipos (p.ej., `Price` como `DECIMAL` y no `VARCHAR`).
- Mover `secret_key` y credenciales a variables de entorno.
- Agregar protección CSRF en formularios si se usan cookies de sesión en producción.

### 7) Dónde cambiar o ampliar
- Nueva tabla: crea en SQL, añade funciones en `connection.py` si hace falta, y expón endpoints en `main.py`.
- Nuevo endpoint: define la ruta en `main.py`, consulta a la BD con `iniciarConexion()` y responde JSON.
- Nueva vista: agrega HTML en `templates/` y el JS en `static/js/` que consuma tu endpoint.

### 8) Conceptos clave para explicar en la sustentación
- HTML: estructura semántica, plantillas Jinja para mostrar/ocultar según `session`.
- CSS: variables de tema (`:root`), layout responsivo, modales y animaciones (transiciones y keyframes).
- JavaScript: `fetch` para consumir API; manejo del DOM para tablas, modales y carrito; paginación, orden y toasts con SweetAlert2.
- Python (Flask): rutas con `@app.route`, manejo de `request`/`session`, `jsonify` para respuestas JSON, `render_template` para vistas, conexión a MySQL.

---

## Explicación rápida por archivos (HTML, CSS, JS, Python)

### HTML (vistas)
- `templates/home.html`: Estructura de la página principal, con contenedores que el JS llena con productos y un modal de carrito.
- `templates/login.html`: Formulario de acceso; al enviar, el JS hace POST a `/login` y redirige si es correcto.
- `templates/registro.html`: Formulario de registro que envía `FormData` a `/registro` y muestra feedback con SweetAlert2.
- `templates/admin.html`: Panel SPA sencillo que alterna secciones y abre modales para CRUDs.

### CSS (estilos)
- `static/css/home.css`: Estilos del Home (header fijo, hero con imagen, tarjetas de producto, carrito modal y carrusel).
- `static/css/login.css`: Tarjeta de login con blur, sombras y animaciones de entrada.
- `static/css/registro.css`: Estilos similares al login, adaptados al formulario de registro.
- `static/css/admin.css`: Tabla, modales, paginación y botones del panel de administración.

### JavaScript (comportamiento)
- `static/js/home.js`:
  - Pide `/ProdCat` y llena las secciones de productos.
  - Carrito en memoria: agrega, calcula total y hace POST a `/comprar`.
  - Efectos: header al hacer scroll, animaciones y carrusel simple.
- `static/js/login.js`:
  - Intercepta `#loginForm`, envía POST a `/login` y redirige al Home si autentica.
- `static/js/resgistro.js`:
  - Intercepta `.register-form`, envía `FormData` a `/registro` y redirige a `/login` tras éxito.
- `static/js/admin.js`:
  - Navega entre secciones del panel.
  - CRUD de catálogos (`/catalogo`), productos (`/productos`), usuarios (`/usuarios`) y ventas (`/ventas`).
  - Modales para crear/editar, paginación y ordenamiento.
  - Descarga de reportes PDF abriendo endpoints `/reportes/*`.

### Python (servidor Flask)
- `src/main.py`:
  - Rutas HTML: `/home`, `/login`, `/registro`, `/admin`.
  - API CRUD: `/catalogo`, `/productos`, `/usuarios`, `/ventas`.
  - Compra del carrito: `POST /comprar` (requiere sesión activa).
  - Reportes PDF: `/reportes/usuarios|productos|catalogos|ventas`.
  - Utilidad `crear_reporte_pdf(...)` con `reportlab`.
- `src/service/connection.py`:
  - `iniciarConexion()`: abre conexión con MySQL y retorna `(conn, cursor)`.
  - `doQuery(...)`: ejecuta SELECT y retorna filas.
  - `insert_users(...)`: inserta un usuario (con commit/rollback).
  - `get_cat_products()`: LEFT JOIN de catálogos con productos.

- Ruteo en Flask: `@app.route` y métodos HTTP.
- Objetos `request`, `session`, `jsonify` y `render_template`.
- Conexión a MySQL con `mysql-connector-python` (transacciones, `commit`/`rollback`).
- Plantillas Jinja: uso de `{{ }}` y lógica condicional con variables de sesión.
- Generación de PDF con `reportlab` y estilos de tabla.

