import mysql.connector as MsqlCon

class ConnectionDB:
    def __init__(self):
        self.cursor = None

    def get_data_conection(self):
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
            print(f"{self.__class__.__name__}: Problemas de conexion")

    def doQuery(self, cursor, query: str, params=()) -> dict:
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