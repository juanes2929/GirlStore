import mysql.connector as MsqlCon  # Conector oficial de MySQL para Python

class ConnectionDB:
    """Capa simple de acceso a datos para MySQL.

    Responsable de:
    - Centralizar credenciales de conexión.
    - Abrir conexiones y devolver (conn, cursor).
    - Ejecutar consultas de lectura (SELECT) y escritura (INSERT/UPDATE/DELETE).
    """
    def __init__(self):
        self.cursor = None

    def get_data_conection(self):
        """Devuelve las credenciales de conexión a la base de datos.

        NOTA: Para producción, mover a variables de entorno en vez de hardcodear.
        """
        return {
            "dataBaseInfo": {
                "user": "root",
                "pwd": "",
                "server": "localhost",
                "port": "3306",
                "dataBase": "GirlStore"
            }
        }

    def iniciarConexion(self):
        """Abre una conexión a MySQL y retorna (conn, cursor).

        El `cursor` permite ejecutar sentencias SQL. Quien lo use debe
        cerrar `conn` al terminar (commit/rollback según corresponda).
        """
        dataConnecton = self.get_data_conection()
        try:
            conn = MsqlCon.connect(
                user=dataConnecton['dataBaseInfo']['user'],
                password=dataConnecton['dataBaseInfo']['pwd'],
                host=dataConnecton['dataBaseInfo']['server'],
                database=dataConnecton['dataBaseInfo']['dataBase'],
                port=dataConnecton['dataBaseInfo']['port']
            )
            print(conn)
            self.cursor = conn.cursor()
            return conn, self.cursor
        except Exception as e:
            # En un escenario real, registrar el error con más detalle
            print(f"{self.__class__.__name__}: Problemas de conexion")

    def doQuery(self, cursor, query: str, params=()) -> dict:
        """Ejecuta una consulta SELECT y retorna todas las filas.

        Usa parámetros para prevenir inyección SQL.
        """
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            resultado = cursor.fetchall()
            return resultado
        except Exception as e:
            print(f"Error: {e}")
            return {"error": str(e)}

    def insert_users(self, username, phone, email, pswd, direction, admin, *args):
        """Inserta un usuario en la tabla Users.

        Realiza commit en éxito o rollback en excepción.
        """
        try:
            conn, cursor = self.iniciarConexion()
            try:
                query = """
                    INSERT INTO Users (UserName, Phone, Email, Pswd, Direction, IsAdmin)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(query, (username, phone, email, pswd, direction, admin))
                conn.commit() 
                return {"success": True, "message": "Usuario insertado correctamente"}
            except Exception as e:
                conn.rollback() 
                print(f"Error al insertar usuario: {e}")
                return {"success": False, "message": str(e)}
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"{self.__class__.__name__}: Problemas al conectar - {e}")
            return {"success": False, "message": "Problemas de conexión"}

    def get_cat_products(self, *args):
        """Obtiene catálogos con sus productos (LEFT JOIN).

        Retorna una lista de tuplas: (Id_producto, Name_product, Img, Price,
        IsActive, Id_cat, Id_catalogo, Name_catalogo). Cuando no hay producto,
        los campos de producto pueden venir como None.
        """
        try:
            conn, cursor = self.iniciarConexion()
            fullcat = None
            try:
                fullcat = self.doQuery(cursor, query="""
                    SELECT p.Id_producto, p.Name_product, p.Img, p.Price, p.IsActive,
                        c.Id_cat, c.Id_catalogo, c.Name_catalogo
                    FROM Catalogo c
                    LEFT JOIN Productos p ON c.Id_cat = p.Id_cat;
                """)
            except Exception as e:
                print(f"Error: {e}")
            finally:
                conn.close()
                return fullcat
        except Exception as e:
            print(f"{self.__class__.__name__}: Problemas al consultar")

if __name__ == "__main__":
    con = ConnectionDB()
    res = con.get_cat_products()