import mysql.connector as MsqlCon

class ConnectionDB:
    def __init__(self, user:str="", pwd:str="", host:str="", db:str="", port:str=""):
        self.conn   = None
        if user == "" or host == "" or db == "" or port == "":
            print("Faltan datos para la coneccion")
        else:
            self.user   = user
            self.pwd    = pwd
            self.host   = host
            self.db     = db
            self.port   = port
            self.start_connection_db()

    def start_connection_db(self, *args):
        conn = MsqlCon.connect(
            user        =   self.user,
            password    =   self.pwd,
            host        =   self.host,
            database    =   self.db,
            port        =   self.port
        )

        if conn:
            print(f"Conectado a la base de datos correctamente -> {conn=}")
            self.conn = conn
        else:
            print("Error al conectar")
            self.conn = None
        


if __name__ == "__main__":
    con = ConnectionDB(
        user    =   "root",
        pwd     =   "",
        host    =   "localhost",
        db      =   "GirlStore",
        port    =   "3306"
    )        
        
