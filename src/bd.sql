CREATE DATABASE GirlStore;
USE GirlStore;
CREATE TABLE Users(
    IdUser INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    UserName VARCHAR (50) NOT NULL,
    Phone VARCHAR (15) NOT NULL,
    Email VARCHAR (50) NOT NULL,
    Pswd VARCHAR (100) NOT NULL,
    Direction VARCHAR (100) NOT NULL,
    IsAdmin	BOOLEAN
);
INSERT INTO Users (UserName, Phone, Email, Pswd, Direction, IsAdmin) VALUES ('Nicol', '3214567890', 'nicol@gmail.com', 'nicol123', 'calle 70 sur pepito', true);
INSERT INTO Users (UserName, Phone, Email, Pswd, Direction, IsAdmin) VALUES ('Juan', '3214568675', 'juan@gmail.com', 'juan123', 'calle 80 sur 18', false);
CREATE TABLE Catalogo (
    Id_cat INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    Id_catalogo INT NOT NULL,
    Name_catalogo VARCHAR(100) NOT NULL
);
INSERT INTO Catalogo (Id_catalogo, Name_catalogo) VALUES (1, 'Trendy');
INSERT INTO Catalogo (Id_catalogo, Name_catalogo) VALUES (2, 'Montoc');
INSERT INTO Catalogo (Id_catalogo, Name_catalogo) VALUES (3, 'Milagros');
CREATE TABLE Productos (
    Id_producto INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    Name_product VARCHAR(600) NOT NULL,
    Img TEXT NOT NULL,
    Price VARCHAR(200) NOT NULL,
    Id_cat INT,
    IsActive BOOLEAN,
    FOREIGN KEY (Id_cat) REFERENCES Catalogo(Id_cat)
);

-- INSERT TABLE PRODUCTS

INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('', '', '', , true);

INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Polvo De Hadas Golden', 'https://b2ctrendy.vtexassets.com/arquivos/ids/160255-800-auto?v=638774844777370000&width=800&height=auto&aspect=true', '12000', 1, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Gloss Barbie Vaquera', 'https://b2ctrendy.vtexassets.com/arquivos/ids/161842-800-auto?v=638956512676370000&width=800&height=auto&aspect=true', '15000', 1, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Kit X 2 Delineadores Stitch', 'https://b2ctrendy.vtexassets.com/arquivos/ids/161419-800-auto?v=638902941272970000&width=800&height=auto&aspect=true', '25000', 1, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Borlas Intensamente', 'https://b2ctrendy.vtexassets.com/arquivos/ids/159875-800-auto?v=638772158219530000&width=800&height=auto&aspect=true', '5000', 1, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Kit X 2 Esponjas Intensamente', 'https://b2ctrendy.vtexassets.com/arquivos/ids/159309-800-auto?v=638735411683500000&width=800&height=auto&aspect=true', '10000',1 , true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Pestañina Para Cejas', 'https://b2ctrendy.vtexassets.com/arquivos/ids/156579-800-auto?v=638615838527770000&width=800&height=auto&aspect=true', '3000', 1, true);

INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Polvo Suelto traslúcido soft-powder 30G nueva presentación', 'https://montoccosmetictools.com/cdn/shop/files/POLVOSOFTPOWDER30GR_3.jpg?v=1742560792&width=1200', '65000', 2, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Lápiz De Labios Montoc', 'https://montoccosmetictools.com/cdn/shop/files/LAPIZ_NUEVO.jpg?v=1752266292&width=1200', '14000', 2, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Gel Facial Hidratante Hydromontoc', 'https://montoccosmetictools.com/cdn/shop/files/MG_5971.jpg?v=1711482762&width=1200', '60800', 2, true);

INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Kit Emergencia y Reparación Profunda', 'https://milagrosbeauty.com/cdn/shop/files/Emergencia-PNG_649fc1ed-8f72-4f00-beb7-d79306a117f5.png?v=1759866594&width=1500', '113700', 3, true);
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive) VALUES ('Shampoo Exfoliante Capilar', 'https://milagrosbeauty.com/cdn/shop/files/Shampoo-Exfoliante-fondo-blanco_1.png?v=1759934214&width=535', '31990', 3, true);


SELECT * FROM Users;
SELECT * FROM Catalogo;
SELECT * FROM Productos;
