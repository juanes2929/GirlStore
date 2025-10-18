import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from datetime import datetime

from service.connection import ConnectionDB
import flask_cors
from flask import Flask, request, redirect, render_template, url_for, session, flash, jsonify, send_file, make_response

app = Flask(__name__)
app.secret_key = "GirlStore"
flask_cors.CORS(app)

dbconection = ConnectionDB() 

@app.errorhandler(404)
def PaginaNoEncontrada(error): 
    return redirect("/home")

@app.route("/")
def tologin():
    return redirect("/home")

@app.route("/registro", methods=['POST', 'GET'])
def registro():
    if request.method == "GET":
        return render_template("registro.html")

    user = request.form.get("usuario")
    phone = request.form.get("telefono")
    email = request.form.get("email")
    passwd = request.form.get("password")
    direction = request.form.get("direccion")
    isAdmin = request.form.get("user_type", "0")  

    if not all([user, phone, email, passwd, direction]):
        return jsonify({"success": False, "message": "Campos vacíos"})

    try:
        valIsAdmin = bool(int(isAdmin))
    except ValueError:
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
    if request.method == "GET":
        return render_template("login.html")

    user = request.form["email"]
    passw = request.form["password"]

    if not user or not passw:
        return jsonify({"success": False, "message": "Campos vacíos"})

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
    if not session.get('Rol') == 1:
        return redirect(url_for('home'))  
    return render_template("admin.html")

@app.route("/check_session")
def check_session():
    if 'Name' in session:
        return jsonify({"logged_in": True})
    else:
        return jsonify({"logged_in": False})

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/ProdCat", methods=["GET"])
def ProdCat():
    res = dbconection.get_cat_products()
    return jsonify(res)


@app.route("/catalogo", methods=["GET"])
def get_catalogos():
    conn, cursor = dbconection.iniciarConexion()
    data = dbconection.doQuery(cursor, "SELECT * FROM Catalogo;")
    conn.close()
    return jsonify(data)


@app.route("/catalogo", methods=["POST"])
def add_catalogo():
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
    try:
        conn, cursor = dbconection.iniciarConexion()
        cursor.execute("DELETE FROM Users WHERE IdUser=%s;", (id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Usuario eliminado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


def crear_reporte_pdf(titulo_reporte, encabezados, filas, nombre_archivo):
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
    if 'Name' not in session:
        return jsonify({"success": False, "message": "Usuario no autenticado"}), 401

    data = request.json
    carrito = data.get("carrito", [])
    total = data.get("total", 0)

    if not carrito or total <= 0:
        return jsonify({"success": False, "message": "Carrito vacío o inválido"}), 400

    # Buscar el usuario en la BD
    conn, cursor = dbconection.iniciarConexion()
    cursor.execute("SELECT IdUser FROM Users WHERE UserName = %s", (session["Name"],))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    id_user = user[0]

    try:
        # Registrar venta
        cursor.execute("""
            INSERT INTO Ventas (IdUser, Total, MetodoPago)
            VALUES (%s, %s, %s)
        """, (id_user, total, "Tarjeta"))
        conn.commit()

        id_venta = cursor.lastrowid

        # Registrar detalle de venta
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=9000)