
-- =====================================
-- CREACIÓN DE BASE DE DATOS
-- =====================================
CREATE DATABASE GirlStore;
USE GirlStore;

-- =====================================
-- TABLA: Users (usuarios del sistema)
-- =====================================
CREATE TABLE Users(
    IdUser INT AUTO_INCREMENT PRIMARY KEY NOT NULL,   -- Identificador único del usuario
    UserName VARCHAR(50) NOT NULL,                    -- Nombre del usuario
    Phone VARCHAR(15) NOT NULL,                       -- Teléfono de contacto
    Email VARCHAR(50) NOT NULL,                       -- Correo electrónico
    Pswd VARCHAR(100) NOT NULL,                       -- Contraseña
    Direction VARCHAR(100) NOT NULL,                  -- Dirección del usuario
    IsAdmin BOOLEAN                                   -- Indica si el usuario es administrador (TRUE/FALSE)
);

-- Datos iniciales de ejemplo
INSERT INTO Users (UserName, Phone, Email, Pswd, Direction, IsAdmin)
VALUES 
('Nicol', '3214567890', 'nicol@gmail.com', 'nicol123', 'calle 70 sur pepito', TRUE),
('Juan', '3214568675', 'juan@gmail.com', 'juan123', 'calle 80 sur 18', FALSE);

-- =====================================
-- TABLA: Catalogo (categorías o marcas)
-- =====================================
CREATE TABLE Catalogo (
    Id_cat INT AUTO_INCREMENT PRIMARY KEY NOT NULL,   -- Identificador del catálogo
    Id_catalogo INT NOT NULL,                         -- Código interno del catálogo
    Name_catalogo VARCHAR(100) NOT NULL               -- Nombre del catálogo o marca
);

-- Datos iniciales de ejemplo
INSERT INTO Catalogo (Id_catalogo, Name_catalogo)
VALUES 
(1, 'Trendy'),
(2, 'Montoc'),
(3, 'Milagros');

-- =====================================
-- TABLA: Productos (productos disponibles)
-- =====================================
CREATE TABLE Productos (
    Id_producto INT AUTO_INCREMENT PRIMARY KEY NOT NULL,  -- Identificador único del producto
    Name_product VARCHAR(600) NOT NULL,                   -- Nombre del producto
    Img TEXT NOT NULL,                                   -- URL de la imagen del producto
    Price VARCHAR(200) NOT NULL,                         -- Precio (se recomienda DECIMAL en lugar de VARCHAR)
    Id_cat INT,                                          -- Relación con el catálogo al que pertenece
    IsActive BOOLEAN,                                    -- Indica si el producto está activo o no
    FOREIGN KEY (Id_cat) REFERENCES Catalogo(Id_cat)     -- Clave foránea: cada producto pertenece a un catálogo
);

-- Inserción de productos
INSERT INTO Productos (Name_product, Img, Price, Id_cat, IsActive)
VALUES
('Polvo De Hadas Golden', 'https://b2ctrendy.vtexassets.com/arquivos/ids/160255-800-auto?v=638774844777370000&width=800&height=auto&aspect=true', '12000', 1, TRUE),
('Gloss Barbie Vaquera', 'https://b2ctrendy.vtexassets.com/arquivos/ids/161842-800-auto?v=638956512676370000&width=800&height=auto&aspect=true', '15000', 1, TRUE),
('Kit X 2 Delineadores Stitch', 'https://b2ctrendy.vtexassets.com/arquivos/ids/161419-800-auto?v=638902941272970000&width=800&height=auto&aspect=true', '25000', 1, TRUE),
('Borlas Intensamente', 'https://b2ctrendy.vtexassets.com/arquivos/ids/159875-800-auto?v=638772158219530000&width=800&height=auto&aspect=true', '5000', 1, TRUE),
('Kit X 2 Esponjas Intensamente', 'https://b2ctrendy.vtexassets.com/arquivos/ids/159309-800-auto?v=638735411683500000&width=800&height=auto&aspect=true', '10000', 1, TRUE),
('Pestañina Para Cejas', 'https://b2ctrendy.vtexassets.com/arquivos/ids/156579-800-auto?v=638615838527770000&width=800&height=auto&aspect=true', '3000', 1, TRUE),
('Polvo Suelto traslúcido soft-powder 30G nueva presentación', 'https://montoccosmetictools.com/cdn/shop/files/POLVOSOFTPOWDER30GR_3.jpg?v=1742560792&width=1200', '65000', 2, TRUE),
('Lápiz De Labios Montoc', 'https://montoccosmetictools.com/cdn/shop/files/LAPIZ_NUEVO.jpg?v=1752266292&width=1200', '14000', 2, TRUE),
('Gel Facial Hidratante Hydromontoc', 'https://montoccosmetictools.com/cdn/shop/files/MG_5971.jpg?v=1711482762&width=1200', '60800', 2, TRUE),
('Kit Emergencia y Reparación Profunda', 'https://milagrosbeauty.com/cdn/shop/files/Emergencia-PNG_649fc1ed-8f72-4f00-beb7-d79306a117f5.png?v=1759866594&width=1500', '113700', 3, TRUE),
('Shampoo Exfoliante Capilar', 'https://milagrosbeauty.com/cdn/shop/files/Shampoo-Exfoliante-fondo-blanco_1.png?v=1759934214&width=535', '31990', 3, TRUE);

-- =====================================
-- TABLA: Ventas (registro de compras)
-- =====================================
CREATE TABLE Ventas (
    IdVenta INT AUTO_INCREMENT PRIMARY KEY NOT NULL,  -- Identificador de la venta
    IdUser INT NOT NULL,                              -- Usuario que realizó la compra
    FechaVenta DATETIME DEFAULT CURRENT_TIMESTAMP,    -- Fecha y hora de la venta
    Total DECIMAL(10,2) NOT NULL,                     -- Monto total de la venta
    MetodoPago VARCHAR(50),                           -- Forma de pago (Tarjeta, Efectivo, etc.)
    Estado VARCHAR(50) DEFAULT 'Completada',          -- Estado del pedido
    FOREIGN KEY (IdUser) REFERENCES Users(IdUser)     -- Clave foránea al usuario comprador
);

-- =====================================
-- TABLA: Detalle_Venta (productos por venta)
-- =====================================
CREATE TABLE Detalle_Venta (
    IdDetalle INT AUTO_INCREMENT PRIMARY KEY NOT NULL, -- Identificador del detalle
    IdVenta INT NOT NULL,                              -- Relación con la venta
    Id_producto INT NOT NULL,                          -- Relación con el producto vendido
    Cantidad INT NOT NULL DEFAULT 1,                   -- Cantidad comprada
    PrecioUnitario DECIMAL(10,2) NOT NULL,             -- Precio unitario al momento de la venta
    Subtotal DECIMAL(10,2) GENERATED ALWAYS AS (Cantidad * PrecioUnitario) STORED,  -- Subtotal automático
    FOREIGN KEY (IdVenta) REFERENCES Ventas(IdVenta),
    FOREIGN KEY (Id_producto) REFERENCES Productos(Id_producto)
);

-- =====================================
-- EJEMPLOS DE INSERCIÓN DE UNA VENTA
-- =====================================
INSERT INTO Ventas (IdUser, Total, MetodoPago)
VALUES (2, 47000, 'Tarjeta');

INSERT INTO Detalle_Venta (IdVenta, Id_producto, Cantidad, PrecioUnitario)
VALUES 
(1, 2, 1, 15000),  -- Gloss Barbie Vaquera
(1, 4, 2, 5000),   -- Borlas Intensamente (x2)
(1, 6, 1, 22000);  -- Pestañina Para Cejas

-- =====================================
-- CONSULTAS DE VERIFICACIÓN
-- =====================================
SELECT * FROM Users;
SELECT * FROM Catalogo;
SELECT * FROM Productos;
SELECT * FROM Ventas;
SELECT * FROM Detalle_Venta;
