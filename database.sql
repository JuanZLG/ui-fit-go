/*!DROP database IF EXISTS `rantuiran`;
create database rantuiran;
use rantuiran;
select * from departamentos dep order by dep.nombre_departamento desc;
select * from municipios mun order by mun.nombre_municipio desc; 
select * from categorias;
select * from departamentos;
select * from municipios;
select * from marcas;*/;

-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: ranfit
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categorias`
--
DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(50) NOT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'Proteínas'),(2,'Creatinas'),(3,'Aminoacidos');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departamentos`
--

DROP TABLE IF EXISTS `departamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departamentos` (
  `id_departamento` int NOT NULL AUTO_INCREMENT,
  `nombre_departamento` varchar(50) NOT NULL,
  PRIMARY KEY (`id_departamento`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Dumping data for table `departamentos`
--

LOCK TABLES `departamentos` WRITE;
/*!40000 ALTER TABLE `departamentos` DISABLE KEYS */;
INSERT INTO `departamentos` 
VALUES 
(1,'Antioquia'),
(2,'Nariño'),
(3,'Cauca'),
(4,'Huila'),
(5,'Quindío'),
(6,'La Guajira'),
(7,'Caquetá'),
(8,'Atlántico'),
(9,'Santander'),
(10,'Valle del cauca'),
(11,'Caldas'),
(12,'Amazonas'),
(13,'Cundinamarca'),
(14,'Bolivar');
/*!40000 ALTER TABLE `departamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `municipios`
--

DROP TABLE IF EXISTS `municipios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `municipios` (
  `id_municipio` int NOT NULL AUTO_INCREMENT,
  `id_departamento` int NOT NULL,
  `nombre_municipio` varchar(60) NOT NULL,
  PRIMARY KEY (`id_municipio`),
  KEY `id_departamento` (`id_departamento`),
  CONSTRAINT `municipios_ibfk_1` FOREIGN KEY (`id_departamento`) REFERENCES `departamentos` (`id_departamento`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `municipios`
--

LOCK TABLES `municipios` WRITE;
/*!40000 ALTER TABLE `municipios` DISABLE KEYS */;
INSERT INTO `municipios` VALUES 
(1,1,'Medellín'),
(2,5,'Calarca'),
(3,1,'Retiro'),
(4,6,'Rioacha'),
(5,4,'Neiva'),
(6,5,'Armenia'),
(7,9,'Bucaramanga'),
(8,14,'Cartagena'),
(9,7,'Florencia'),
(10,8,'Barranquilla'),
(11,13,'Soacha'),
(12,10,'Cali'),
(13,11,'Manizales'),
(14,4,'Pitalito'),
(15,12,'Leticia'),
(16,2,'Pasto'),
(17,8,'Soledad');
/*!40000 ALTER TABLE `municipios` ENABLE KEYS */;
UNLOCK TABLES;
--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `id_municipio` int NOT NULL,
  `documento` varchar(25) NOT NULL,
  `nombres` varchar(60) NOT NULL,
  `apellidos` varchar(60) NOT NULL,
  `celular` varchar(15) NOT NULL,
  `barrio` varchar(40) NOT NULL,
  `direccion` varchar(50) NOT NULL,
  `estado` tinyint NOT NULL,
  `correo` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  KEY `id_municipio` (`id_municipio`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`id_municipio`) REFERENCES `municipios` (`id_municipio`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES 
(1,1,'1000088092','Juan','Zuluaga Aristizábal','3117146361','Las Playas','CR 71 #16-10',1,'jczuluaga2003@gmail.com'),
(2,16,'1000088382','Juan Pablo','Escobar E','3227465362','Tunjuelito','Cr 71 #12-17',0,'jczuluaga2003@gmail.com'),
(3,13,'1000077062','Jose','Martinez','3116548362','Curramba','Cr 12 #16-19',1,'elotrocorreodecami@gmail.com');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id_proveedor` int NOT NULL AUTO_INCREMENT,
  `nombre_proveedor` varchar(65) NOT NULL,
  `telefono` varchar(10) NOT NULL,
  `correo` varchar(65) NOT NULL,
  `direccion` varchar(50) DEFAULT NULL,
  `informacion_adicional` text,
  `tipo_documento` varchar(50) DEFAULT NULL,
  `numero_documento_nit` varchar(50) DEFAULT NULL,
  `estado` tinyint NOT NULL,
  PRIMARY KEY (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES 
(1,'Suplementos Colombia','3157592564','colsupplements@sppmail.com','Remota','','NIT','340.327.142-2',0),
(2,'Daniel Hernández','3226391894','dher732@gmail.com','Loma de los Bernal, Medellín Cr.12 #12-16','','DOC','1001424856',1),
(3,'MedellinFit Suplementos','3118659281','mfit2025@gmail.com','Remota','Proveedor de Medellín','DOC','1000099054',1);
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id_compra` int NOT NULL AUTO_INCREMENT,
  `id_proveedor` int NOT NULL,
  `fechareg` date NOT NULL,
  `estado` tinyint NOT NULL,
  `totalCompra` float DEFAULT NULL,
  PRIMARY KEY (`id_compra`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
INSERT INTO `compras` VALUES (1,1,'2023-12-11',1,464000),
(2,2,'2023-12-11',0,60000),
(3,2,'2023-12-11',1,696000),
(4,1,'2023-12-11',1,1190000),
(5,3,'2023-12-11',1,1224000);
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `marcas`
--

DROP TABLE IF EXISTS `marcas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marcas` (
  `id_marca` int NOT NULL AUTO_INCREMENT,
  `nombre_marca` varchar(50) NOT NULL,
  PRIMARY KEY (`id_marca`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marcas`
--

LOCK TABLES `marcas` WRITE;
/*!40000 ALTER TABLE `marcas` DISABLE KEYS */;
INSERT INTO `marcas` VALUES (1,'Megaplex'),(2,'Bi-Pro'),(3,'ProScience'),(4,'NutriAmerica');
/*!40000 ALTER TABLE `marcas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `id_categoria` int NOT NULL,
  `id_marca` int NOT NULL,
  `nombre_producto` varchar(75) NOT NULL,
  `descripcion` varchar(1600) NOT NULL,
  `cantidad` int NOT NULL,
  `fechaven` datetime DEFAULT NULL,
  `sabor` varchar(50) NOT NULL,
  `presentacion` varchar(45) DEFAULT NULL,
  `precio` float DEFAULT NULL,
  `estado` tinyint NOT NULL,
  `iProductImg` blob,
  `iInfoImg` blob,
  `precio_pub` float DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `id_categoria` (`id_categoria`),
  KEY `id_marca` (`id_marca`),
  CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `productos_ibfk_3` FOREIGN KEY (`id_marca`) REFERENCES `marcas` (`id_marca`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES 
(1,1,2,'Bi-Pro Classic 2lb','Bipro classic es una proteína de alta concentración y pureza con mínimo niveles de grasa y lactosa. Contiene proteina de suero de leche, la proteína con mayor evidencia en la contrucción de tejidos musculares, también aporta el mayor perfil de aminoácidos esenciales para tener una nutrición saludable.\r\n\r\nModo de uso de BiPro Classic: Mezcle Bi pro classic 26g (1/2 medida/cucharada) con 4 onzas de agua o adicione su bebida favorita. Consúmalo inmediatamente después de entrenar.',15,'2027-03-01 05:00:00','Chocolate, Vainilla','2',116000,1,_binary 'landingproducts/products/bipro-classic-2-lb.jpg',_binary 'landingproducts/nutritiondex/megaplex.png',150000),
(2,1,3,'Best Protein 2lbs','BEST PROTEIN es una mezcla 3 en 1, Proteína aislada de suero de leche de altísima calidad, Caseina Micelar (proteína de absorción lenta) y Leucina. BEST PROTEIN no contiene azúcar, grasa, carbohidratos ni lactosa, lo cual la hace una aliada perfecta para tu proceso.',7,'2025-06-04 05:00:00','Vainilla, Chicle','2',170000,0,_binary 'landingproducts/products/betterthanAll.webp',_binary 'landingproducts/nutritiondex/best-table.webp',222000),
(3,2,1,'Creatine Power 2lbs','De Nutramerican para el mundo.\r\n\r\nMEGAPLEX CREATINE POWER es una fórmula avanzada que proporciona a los deportistas un aumento extremo de masa muscular, masivas calorías para máxima ganancia de peso. Este producto está elaborado con proteína de suero, brindando al consumidor todos los aminoácidos esenciales y no esenciales para la construcción y mantenimiento de la masa muscular.\r\nMega Plex Creatine Power contiene 5g de creatina monohidratada por dosis, producto que incrementa notoriamente la fuerza y potencia, que mezclándolo con el excelente perfil nutricional da como resultado un aumento extremo de masa muscular.',0,'2025-06-04 05:00:00','Frutos Rojos, Fresa','2',30000,1,_binary 'landingproducts/products/megaplexpower.png',_binary 'landingproducts/nutritiondex/MEGAPLEX-TABLA-600x600.jpg',55000),
(4,2,3,'Legacy','Es muy mala proteina',10,'2024-11-12 05:00:00','Fresa, vainila','1',90000,1,_binary 'landingproducts/products/legacy-proscience1.webp',_binary 'landingproducts/nutritiondex/legacy-50serv-tabla-800.webp',115000);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detallecompra`
--

DROP TABLE IF EXISTS `detallecompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detallecompra` (
  `id_detallecompra` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `id_compra` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_uni` float DEFAULT NULL,
  `precio_tot` float DEFAULT NULL,
  `estado` tinyint DEFAULT NULL,
  PRIMARY KEY (`id_detallecompra`),
  KEY `id_producto` (`id_producto`,`id_compra`),
  KEY `id_compra` (`id_compra`),
  CONSTRAINT `detallecompra_ibfk_1` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detallecompra_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detallecompra`
--

LOCK TABLES `detallecompra` WRITE;
/*!40000 ALTER TABLE `detallecompra` DISABLE KEYS */;
INSERT INTO `detallecompra` VALUES 
(1,1,1,4,116000,464000,1),
(2,3,2,2,30000,60000,1),
(3,1,3,6,116000,696000,1),
(4,2,4,7,170000,1190000,1),
(5,1,5,9,116000,1044000,1),
(6,4,5,2,90000,180000,1);
/*!40000 ALTER TABLE `detallecompra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id_venta` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `fechareg` date DEFAULT NULL,
  `estado` tinyint NOT NULL,
  `totalVenta` float DEFAULT NULL,
  `descuentoVenta` varchar(255) DEFAULT 'No aplica',
  `totalVentaDescuento` varchar(255) DEFAULT NULL,
  `margenGanancia` float DEFAULT NULL,
  PRIMARY KEY (`id_venta`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,1,'2023-12-11',0,1674560,'5','88135',308565),(2,1,'2023-12-11',1,763200,'4','31800',145200);
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT,
  `id_venta` int DEFAULT NULL,
  `id_cliente` int DEFAULT NULL,
  `fecha_pedido` date DEFAULT NULL,
  `total_pedido` float DEFAULT NULL,
  `estado` enum('cancelado','en proceso','confirmado') DEFAULT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `id_venta` (`id_venta`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`),
  CONSTRAINT `pedidos_ibfk_2` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (1,NULL,3,'2023-12-11',680000,'cancelado'),(2,NULL,1,'2023-12-11',795000,'en proceso');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detallepedido`
--

DROP TABLE IF EXISTS `detallepedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detallepedido` (
  `id_detallepedido` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int DEFAULT NULL,
  `id_producto` int DEFAULT NULL,
  `sabor` varchar(50) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `precio_uni` float DEFAULT NULL,
  `precio_tot` float DEFAULT NULL,
  PRIMARY KEY (`id_detallepedido`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `detallepedido_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `detallepedido_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detallepedido`
--

LOCK TABLES `detallepedido` WRITE;
/*!40000 ALTER TABLE `detallepedido` DISABLE KEYS */;
INSERT INTO `detallepedido` VALUES 
(1,1,4,'Fresa',2,115000,230000),
(2,1,1,'Chocolate',3,150000,450000),
(3,2,4,'Fresa',3,115000,345000),
(4,2,1,'Chocolate',3,150000,450000);
/*!40000 ALTER TABLE `detallepedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalleventa`
--

DROP TABLE IF EXISTS `detalleventa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalleventa` (
  `id_detalleventa` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `id_venta` int NOT NULL,
  `cantidad` int NOT NULL,
  `estado` tinyint NOT NULL,
  `totalProductoDescuento` varchar(255) DEFAULT NULL,
  `margenGanancia` float DEFAULT NULL,
  `precio_compra` float DEFAULT NULL,
  `precio_venta` float DEFAULT NULL,
  `precio_tot` float DEFAULT NULL,
  `descuentoProducto` varchar(255) DEFAULT 'No aplica',
  PRIMARY KEY (`id_detalleventa`),
  KEY `id_producto` (`id_producto`,`id_venta`),
  KEY `id_venta` (`id_venta`),
  CONSTRAINT `detalleventa_ibfk_1` FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detalleventa_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalleventa`
--

LOCK TABLES `detalleventa` WRITE;
/*!40000 ALTER TABLE `detalleventa` DISABLE KEYS */;
INSERT INTO `detalleventa` VALUES 
(1,1,1,11,0,'No aplica',374000,116000,150000,1650000,'0'),
(2,4,1,1,0,'2300',22700,90000,112700,112700,'2'),
(3,1,2,3,1,'No aplica',102000,116000,150000,450000,'0'),
(4,4,2,3,1,'No aplica',75000,90000,115000,345000,'0');
/*!40000 ALTER TABLE `detalleventa` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id_permiso` int NOT NULL AUTO_INCREMENT,
  `clientes` tinyint NOT NULL,
  `usuarios` tinyint NOT NULL,
  `proveedores` tinyint NOT NULL,
  `productos` tinyint NOT NULL,
  `compras` tinyint NOT NULL,
  `ventas` tinyint NOT NULL,
  PRIMARY KEY (`id_permiso`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
INSERT INTO `permisos` VALUES (1,1,1,1,1,1,1),(3,0,0,0,1,1,0),(4,1,0,1,1,0,0);
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;





--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(37) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador'),(3,'Inventario'),(4,'Gerente');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rolespermisos`
--

DROP TABLE IF EXISTS `rolespermisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rolespermisos` (
  `id_rol` int NOT NULL,
  `id_permiso` int NOT NULL,
  `id_rolespermisos` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id_rolespermisos`),
  KEY `id_rol` (`id_rol`,`id_permiso`),
  KEY `id_permiso` (`id_permiso`),
  CONSTRAINT `rolespermisos_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `rolespermisos_ibfk_2` FOREIGN KEY (`id_permiso`) REFERENCES `permisos` (`id_permiso`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rolespermisos`
--

LOCK TABLES `rolespermisos` WRITE;
/*!40000 ALTER TABLE `rolespermisos` DISABLE KEYS */;
INSERT INTO `rolespermisos` VALUES (1,1,1),(3,3,3),(4,4,4);
/*!40000 ALTER TABLE `rolespermisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `id_rol` int DEFAULT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `correo` varchar(60) NOT NULL,
  `contrasena` varchar(64) DEFAULT NULL,
  `estado` tinyint NOT NULL,
  PRIMARY KEY (`id_usuario`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES 
(1,1,'Juanca','jczuluaga2003@gmail.com','Monitoc10',1),
(2,3,'Camille','camilozlgahre@gmail.com','Monitoc10',0),
(3,1,'Juan Manuel','jczuluaga29@misena.edu.co','uiUyVIaN',1),
(4,4,'Camilo','elotrocorreodecami@gmail.com','Monitoc10',1);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;



/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-30 18:57:29
