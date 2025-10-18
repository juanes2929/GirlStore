import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from datetime import datetime

from service.connection import ConnectionDB  # Capa de acceso a datos (MySQL)
import flask_cors
from flask import Flask, request, redirect, render_template, url_for, session, flash, jsonify, send_file, make_response

app = Flask(__name__)
app.secret_key = "GirlStore"  # Clave para firmar cookies de sesión
flask_cors.CORS(app)  # Permite peticiones desde el frontend (si fuese otro dominio)

dbconection = ConnectionDB()  # Instancia para interactuar con la BD

@app.errorhandler(404)
def PaginaNoEncontrada(error):
    """Si una ruta no existe, redirige a Home para mejorar UX."""
    return redirect("/home")

@app.route("/")
def tologin():
    """Redirige al Home por defecto."""
    return redirect("/home")

@app.route("/registro", methods=['POST', 'GET'])
def registro():
    """Muestra el formulario de registro (GET) y crea usuario (POST)."""
    if request.method == "GET":
        return render_template("registro.html")

    user = request.form.get("usuario")
    phone = request.form.get("telefono")
    email = request.form.get("email")
    passwd = request.form.get("password")
    direction = request.form.get("direccion")
    isAdmin = request.form.get("user_type", "0")  

    # Validación simple de campos vacíos (lado servidor)
    if not all([user, phone, email, passwd, direction]):
        return jsonify({"success": False, "message": "Campos vacíos"})

    try:
        valIsAdmin = bool(int(isAdmin))
    except ValueError:
        # Si el valor de admin no es convertible a entero, lo tomamos como False
        valIsAdmin = False

    res = dbconection.insert_users(
        username=user,
        phone=phone,
        email=email,
        pswd=passwd,
        direction=direction,
        admin=valIsAdmin
    )

    print(res)

    if not res.get("success"):
        return jsonify({"success": False, "message": "No se pudo registrar el usuario"})

    return jsonify({"success": True, "message": "Se agregó el usuario correctamente", "href": "/login"})

@app.route("/login", methods=["GET", "POST"])
def login():
    """Muestra login (GET) y autentica contra la tabla Users (POST)."""
    if request.method == "GET":
        return render_template("login.html")

    user = request.form["email"]
    passw = request.form["password"]

    if not user or not passw:
        return jsonify({"success": False, "message": "Campos vacíos"})

    # NOTA: Para producción, hacer SELECT con WHERE Email = %s LIMIT 1
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("SELECT * FROM Users;")
    resU = cursor.fetchall()
    conn.close()

    for u in resU:
        if u[3] == user and u[4] == passw:
            session['Name'] = u[1]
            session['Rol'] = u[6]  
            return jsonify({"success": True, "message": f"Bienvenido, {u[1]}"})


    return jsonify({"success": False, "message": "Correo y/o Contraseña incorrectos"})

@app.route("/admin")
def admin():
    """Página del panel de administración (solo Rol == 1)."""
    if not session.get('Rol') == 1:
        return redirect(url_for('home'))
    return render_template("admin.html")

@app.route("/check_session")
def check_session():
    """Endpoint ligero para que el frontend detecte si hay sesión activa."""
    if 'Name' in session:
        return jsonify({"logged_in": True})
    else:
        return jsonify({"logged_in": False})

@app.route("/home")
def home():
    """Renderiza la página principal (Home)."""
    return render_template("home.html")

@app.route("/ProdCat", methods=["GET"])
def ProdCat():
    """Devuelve catálogos + productos (JOIN) para poblar secciones del Home."""
    res = dbconection.get_cat_products()
    return jsonify(res)


@app.route("/catalogo", methods=["GET"])
def get_catalogos():
    """Lista todos los catálogos."""
    conn, cursor = dbconection.iniciarConexion()
    data = dbconection.doQuery(cursor, "SELECT * FROM Catalogo;")
    conn.close()
    return jsonify(data)


@app.route("/catalogo", methods=["POST"])
def add_catalogo():
    """Crea un catálogo nuevo (Id_catalogo, Name_catalogo)."""
    data = request.json
    Id_catalogo = data.get("Id_catalogo")
    Name_catalogo = data.get("Name_catalogo")
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("INSERT INTO Catalogo (Id_catalogo, Name_catalogo) VALUES (%s, %s)", (Id_catalogo, Name_catalogo))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Catálogo agregado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/catalogo/<int:id>", methods=["PUT"])
def update_catalogo(id):
    """Actualiza un catálogo por su Id_cat interno."""
    data = request.json
    Id_catalogo = data.get("Id_catalogo")
    Name_catalogo = data.get("Name_catalogo")
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("""
            UPDATE Catalogo SET Id_catalogo=%s, Name_catalogo=%s WHERE Id_cat=%s
        """, (Id_catalogo, Name_catalogo, id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Catálogo actualizado"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/catalogo/<int:id>", methods=["DELETE"])
def delete_catalogo(id):
    """Elimina un catálogo por Id_cat."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("DELETE FROM Catalogo WHERE Id_cat=%s", (id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Catálogo eliminado"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/productos", methods=["GET"])
def get_productos():
    """Lista productos enriquecidos con datos de catálogo."""
    try:
        res = dbconection.get_cat_products()
        productos = []
        for row in res:
            if row[0] is None:
                continue
            productos.append({
                "Id_producto": row[0],
                "Name_product": row[1],
                "Img": row[2],
                "Price": row[3],
                "IsActive": bool(row[4]),
                "Id_cat": row[5],
                "Id_catalogo": row[6],
                "Name_catalogo": row[7],
            })
        return jsonify(productos)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/productos/<int:id>", methods=["GET"])
def get_producto_by_id(id):
    """Devuelve un producto por Id_producto."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("""
            SELECT Id_producto, Name_product, Img, Price, Id_cat, IsActive
            FROM Productos WHERE Id_producto = %s;
        """, (id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404

        return jsonify({
            "Id_producto": row[0],
            "Name_product": row[1],
            "Img": row[2],
            "Price": row[3],
            "Id_cat": row[4],
            "IsActive": bool(row[5])
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/productos", methods=["POST"])
def add_producto():
    """Crea un producto nuevo."""
    data = request.json
    Name_product = data.get("Name_product")
    Img = data.get("Img")
    Price = data.get("Price")
    Id_cat = data.get("Id_cat")
    IsActive = data.get("IsActive", True)

    if not all([Name_product, Img, Price, Id_cat]):
        return jsonify({"success": False, "message": "Campos vacíos"})

    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("""
            INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive)
            VALUES (%s, %s, %s, %s, %s);
        """, (Name_product, Img, Price, Id_cat, IsActive))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Producto agregado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/productos/<int:id>", methods=["PUT"])
def update_producto(id):
    """Actualiza un producto existente."""
    data = request.json
    Name_product = data.get("Name_product")
    Img = data.get("Img")
    Price = data.get("Price")
    Id_cat = data.get("Id_cat")
    IsActive = data.get("IsActive", True)

    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("""
            UPDATE Productos
            SET Name_product=%s, Img=%s, Price=%s, Id_cat=%s, IsActive=%s
            WHERE Id_producto=%s;
        """, (Name_product, Img, Price, Id_cat, IsActive, id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Producto actualizado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/productos/<int:id>", methods=["DELETE"])
def delete_producto(id):
    """Desactiva un producto (soft-delete)."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("UPDATE Productos SET IsActive = FALSE WHERE Id_producto = %s;", (id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Producto desactivado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    """Lista usuarios (sin contraseñas)."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("SELECT * FROM Users;")
        rows = cursor.fetchall()
        conn.close()

        usuarios = []
        for u in rows:
            usuarios.append({
                "IdUser": u[0],
                "UserName": u[1],
                "Phone": u[2],
                "Email": u[3],
                "Direction": u[4],
                "IsAdmin": bool(u[6])
            })

        print(usuarios)
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/usuarios/<int:id>", methods=["GET"])
def get_usuario_by_id(id):
    """Detalle de usuario por IdUser."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("SELECT IdUser, UserName, Phone, Email, Direction, IsAdmin FROM Users WHERE IdUser=%s;", (id,))
        u = cursor.fetchone()
        conn.close()

        if not u:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        return jsonify({
            "IdUser": u[0],
            "UserName": u[1],
            "Phone": u[2],
            "Email": u[3],
            "Direction": u[4],
            "IsAdmin": bool(u[5])
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/usuarios", methods=["POST"])
def add_usuario():
    """Crea un usuario (incluye contraseña en texto plano: solo educativa)."""
    data = request.json
    UserName = data.get("UserName")
    Phone = data.get("Phone")
    Email = data.get("Email")
    Direction = data.get("Direction")
    Pswd = data.get("Pswd")
    IsAdmin = data.get("IsAdmin", False)

    if not all([UserName, Phone, Email, Direction, Pswd]):
        return jsonify({"success": False, "message": "Campos vacíos"})

    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("""
            INSERT INTO Users (UserName, Phone, Email, Pswd, Direction, IsAdmin)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (UserName, Phone, Email, Pswd, Direction, IsAdmin))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Usuario agregado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/usuarios/<int:id>", methods=["PUT"])
def update_usuario(id):
    """Actualiza datos de un usuario (sin cambiar contraseña)."""
    data = request.json
    UserName = data.get("UserName")
    Phone = data.get("Phone")
    Email = data.get("Email")
    Direction = data.get("Direction")
    IsAdmin = data.get("IsAdmin", False)

    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("""
            UPDATE Users SET UserName=%s, Phone=%s, Email=%s, Direction=%s, IsAdmin=%s
            WHERE IdUser=%s;
        """, (UserName, Phone, Email, Direction, IsAdmin, id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Usuario actualizado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/usuarios/<int:id>", methods=["DELETE"])
def delete_usuario(id):
    """Elimina un usuario de la base de datos."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("DELETE FROM Users WHERE IdUser=%s;", (id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Usuario eliminado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


def crear_reporte_pdf(titulo_reporte, encabezados, filas, nombre_archivo):
    """Construye y retorna un PDF con tabla estilizada usando reportlab.

    - Encabezado con logo y título
    - Tabla central con encabezados y filas
    - Pie con fecha/hora
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=40, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    # --- LOGO Y TÍTULO PRINCIPAL ---
    logo_path = os.path.join("static", "img", "maquillaje.png")
    if os.path.exists(logo_path):
        img = Image(logo_path, width=60, height=60)
        img.hAlign = "CENTER"
        elements.append(img)

    titulo_principal = Paragraph("<b>GirlStore | Maquillaje & Cosméticos</b>", styles["Title"])
    titulo_principal.alignment = 1  # Centrado
    elements.append(titulo_principal)

    subtitulo = Paragraph(f"<font color='#e91e63'><b>{titulo_reporte}</b></font>", styles["Heading2"])
    subtitulo.alignment = 1  # Centrado
    elements.append(subtitulo)
    elements.append(Spacer(1, 12))

    # --- TABLA ---
    tabla = Table([encabezados] + filas, hAlign='CENTER')
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e91e63")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 20))

    # --- PIE DE PÁGINA ---
    fecha = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    pie = Paragraph(f"<font size=8 color=gray>Generado el {fecha} - GirlStore © 2025</font>", styles["Normal"])
    pie.alignment = 1  # Centrado
    elements.append(pie)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=False, download_name=nombre_archivo, mimetype="application/pdf")


@app.route("/comprar", methods=["POST"])
def comprar():
    """Flujo de compra desde el Home: registra venta y detalle para el usuario en sesión."""
    if 'Name' not in session:
        return jsonify({"success": False, "message": "Usuario no autenticado"}), 401

    data = request.json
    carrito = data.get("carrito", [])
    total = data.get("total", 0)

    if not carrito or total <= 0:
        return jsonify({"success": False, "message": "Carrito vacío o inválido"}), 400

    # Buscar el usuario en la BD (por nombre guardado en sesión)
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("SELECT IdUser FROM Users WHERE UserName = %s", (session["Name"],))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    id_user = user[0]

    try:
        # Registrar venta (cabecera)
        cursor.execute("""
            INSERT INTO Ventas (IdUser, Total, MetodoPago)
            VALUES (%s, %s, %s)
        """, (id_user, total, "Tarjeta"))
        conn.commit()

        id_venta = cursor.lastrowid

        # Registrar detalle de venta (una línea por producto)
        for item in carrito:
            cursor.execute("""
                INSERT INTO Detalle_Venta (IdVenta, Id_producto, Cantidad, PrecioUnitario)
                VALUES (%s, %s, %s, %s)
            """, (id_venta, item["id"], item.get("cantidad", 1), item["price"]))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Compra registrada correctamente"})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "message": str(e)})


# -------------------------------
# 📋 REPORTE DE USUARIOS
# -------------------------------
@app.route("/reportes/usuarios")
def reporte_usuarios():
    """Genera PDF con usuarios y su rol."""
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("SELECT IdUser, UserName, Phone, Email, Direction, IsAdmin FROM Users;")
    rows = cursor.fetchall()
    conn.close()

    datos = [
        [
            r[0],
            r[1],
            r[2],
            r[3],
            r[4],
            "Administrador" if r[5] == 1 else "Usuario"
        ]
        for r in rows
    ]

    return crear_reporte_pdf(
        "Reporte de Usuarios",
        ["ID", "Nombre", "Teléfono", "Email", "Dirección", "Rol"],
        datos,
        "reporte_usuarios.pdf"
    )


# -------------------------------
# 💄 REPORTE DE PRODUCTOS
# -------------------------------
@app.route("/reportes/productos")
def reporte_productos():
    """Genera PDF con productos, precio y estado."""
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("SELECT Id_producto, Name_product, Price, Id_cat, IsActive FROM Productos;")
    rows = cursor.fetchall()
    conn.close()

    datos = [
        [
            r[0],
            r[1],
            f"${int(r[2]):,}".replace(",", "."),
            r[3],
            "Activo" if r[4] else "Inactivo"
        ]
        for r in rows
    ]

    return crear_reporte_pdf(
        "Reporte de Productos",
        ["ID", "Nombre", "Precio", "Categoría", "Estado"],
        datos,
        "reporte_productos.pdf"
    )


# -------------------------------
# 🗂️ REPORTE DE CATÁLOGOS
# -------------------------------
@app.route("/reportes/catalogos")
def reporte_catalogos():
    """Genera PDF con catálogos (ID, código y nombre)."""
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("SELECT Id_cat, Id_catalogo, Name_catalogo FROM Catalogo;")
    rows = cursor.fetchall()
    conn.close()

    datos = [[r[0], r[1], r[2]] for r in rows]

    return crear_reporte_pdf(
        "Reporte de Catálogos",
        ["ID", "Código", "Nombre del Catálogo"],
        datos,
        "reporte_catalogos.pdf"
    )


# -------------------------------
# 🧾 ENDPOINTS DE VENTAS
# -------------------------------
@app.route("/ventas", methods=["GET"])
def get_ventas():
    """Lista todas las ventas con conteo de ítems."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        # Obtener ventas con información del usuario y cantidad de items
        cursor.execute("""
            SELECT v.IdVenta, u.UserName, v.FechaVenta, v.Total, v.MetodoPago, v.Estado,
                   (SELECT COUNT(*) FROM Detalle_Venta dv WHERE dv.IdVenta = v.IdVenta) as items_count
            FROM Ventas v
            LEFT JOIN Users u ON u.IdUser = v.IdUser
            ORDER BY v.FechaVenta DESC;
        """)
        rows = cursor.fetchall()
        conn.close()

        ventas = []
        for r in rows:
            ventas.append({
                "IdVenta": r[0],
                "UserName": r[1],
                "FechaVenta": r[2].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[2], 'strftime') else str(r[2]),
                "Total": float(r[3]) if r[3] is not None else 0,
                "MetodoPago": r[4],
                "Estado": r[5],
                "ItemsCount": int(r[6])
            })

        return jsonify(ventas)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/ventas/<int:id>", methods=["GET"])
def get_venta_by_id(id):
    """Detalle completo de una venta (cabecera + líneas)."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        # Cabecera de la venta
        cursor.execute("SELECT IdVenta, IdUser, FechaVenta, Total, MetodoPago, Estado FROM Ventas WHERE IdVenta = %s;", (id,))
        venta = cursor.fetchone()
        if not venta:
            conn.close()
            return jsonify({"success": False, "message": "Venta no encontrada"}), 404

        # Obtener nombre del usuario
        cursor.execute("SELECT UserName, Email FROM Users WHERE IdUser = %s;", (venta[1],))
        user = cursor.fetchone()

        # Detalle de la venta con nombre de producto
        cursor.execute("""
            SELECT dv.IdDetalle, p.Id_producto, p.Name_product, dv.Cantidad, dv.PrecioUnitario, dv.Subtotal
            FROM Detalle_Venta dv
            LEFT JOIN Productos p ON p.Id_producto = dv.Id_producto
            WHERE dv.IdVenta = %s;
        """, (id,))
        detalles = cursor.fetchall()
        conn.close()

        detalle_list = []
        for d in detalles:
            detalle_list.append({
                "IdDetalle": d[0],
                "Id_producto": d[1],
                "Name_product": d[2],
                "Cantidad": int(d[3]),
                "PrecioUnitario": float(d[4]),
                "Subtotal": float(d[5])
            })

        result = {
            "IdVenta": venta[0],
            "IdUser": venta[1],
            "UserName": user[0] if user else None,
            "Email": user[1] if user else None,
            "FechaVenta": venta[2].strftime("%Y-%m-%d %H:%M:%S") if hasattr(venta[2], 'strftime') else str(venta[2]),
            "Total": float(venta[3]) if venta[3] is not None else 0,
            "MetodoPago": venta[4],
            "Estado": venta[5],
            "Detalles": detalle_list
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------
# 🧾 REPORTE DE VENTAS
# -------------------------------
@app.route("/reportes/ventas")
def reporte_ventas():
    """Genera PDF con ventas (ID, fecha, usuario, total, método, estado, items)."""
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("""
        SELECT v.IdVenta,
               u.UserName,
               v.FechaVenta,
               v.Total,
               v.MetodoPago,
               v.Estado,
               (SELECT COUNT(*) FROM Detalle_Venta dv WHERE dv.IdVenta = v.IdVenta) AS items_count
        FROM Ventas v
        LEFT JOIN Users u ON u.IdUser = v.IdUser
        ORDER BY v.FechaVenta DESC;
    """)
    rows = cursor.fetchall()
    conn.close()

    # Formateo de filas para la tabla PDF
    datos = []
    for r in rows:
        id_venta   = r[0]
        user_name  = r[1] or ""
        fecha      = r[2].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[2], "strftime") else str(r[2])
        total      = float(r[3]) if r[3] is not None else 0.0
        metodo     = r[4] or ""
        estado     = r[5] or ""
        items      = int(r[6]) if r[6] is not None else 0

        # COP con separador de miles como punto (sin decimales para uniformar con otros reportes)
        total_str = f"${total:,.0f}".replace(",", ".")

        datos.append([id_venta, fecha, user_name, total_str, metodo, estado, items])

    return crear_reporte_pdf(
        "Reporte de Ventas",
        ["ID Venta", "Fecha", "Usuario", "Total", "Método", "Estado", "Items"],
        datos,
        "reporte_ventas.pdf"
    )


##########################
## VENTAS ###############
##########################

@app.route("/ventas", methods=["POST"])
def add_venta():
    """Crea una venta (uso desde Admin)."""
    data = request.json
    IdUser = data.get("IdUser")
    Total = data.get("Total")
    MetodoPago = data.get("MetodoPago", "Tarjeta")
    Estado = data.get("Estado", "Completada")
    Detalles = data.get("Detalles", [])

    if not IdUser or Total is None:
        return jsonify({"success": False, "message": "Campos vacíos"}), 400

    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("INSERT INTO Ventas (IdUser, Total, MetodoPago, Estado) VALUES (%s, %s, %s, %s)", (IdUser, Total, MetodoPago, Estado))
        conn.commit()
        id_venta = cursor.lastrowid

        for d in Detalles:
            pid = d.get('Id_producto') or d.get('IdProducto') or d.get('id')
            cantidad = d.get('Cantidad') or d.get('cantidad') or 1
            precio = d.get('PrecioUnitario') or d.get('Precio') or d.get('price') or 0
            cursor.execute("INSERT INTO Detalle_Venta (IdVenta, Id_producto, Cantidad, PrecioUnitario) VALUES (%s, %s, %s, %s)", (id_venta, pid, cantidad, precio))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Venta creada correctamente"})
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/ventas/<int:id>", methods=["PUT"])
def update_venta(id):
    """Actualiza una venta; si vienen Detalles, reemplaza las líneas."""
    data = request.json
    Total = data.get("Total")
    MetodoPago = data.get("MetodoPago")
    Estado = data.get("Estado")
    Detalles = data.get("Detalles", None)

    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("UPDATE Ventas SET Total=%s, MetodoPago=%s, Estado=%s WHERE IdVenta=%s", (Total, MetodoPago, Estado, id))
        # Si vienen detalles, reemplazarlos
        if Detalles is not None:
            cursor.execute("DELETE FROM Detalle_Venta WHERE IdVenta=%s", (id,))
            for d in Detalles:
                pid = d.get('Id_producto') or d.get('IdProducto') or d.get('id')
                cantidad = d.get('Cantidad') or d.get('cantidad') or 1
                precio = d.get('PrecioUnitario') or d.get('Precio') or d.get('price') or 0
                cursor.execute("INSERT INTO Detalle_Venta (IdVenta, Id_producto, Cantidad, PrecioUnitario) VALUES (%s, %s, %s, %s)", (id, pid, cantidad, precio))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Venta actualizada correctamente"})
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/ventas/<int:id>", methods=["DELETE"])
def delete_venta(id):
    """Elimina una venta y su detalle asociado."""
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("DELETE FROM Detalle_Venta WHERE IdVenta=%s", (id,))
        cursor.execute("DELETE FROM Ventas WHERE IdVenta=%s", (id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Venta eliminada correctamente"})
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({"success": False, "message": str(e)}), 500



@app.route("/logout")
def logout():
    """Cierra sesión y redirige al inicio."""
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=9000)