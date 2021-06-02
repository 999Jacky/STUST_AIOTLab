CREATE DATABASE  IF NOT EXISTS `Med` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `Med`;
-- MySQL dump 10.13  Distrib 8.0.25, for Win64 (x86_64)
--
-- Host: 192.168.20.1    Database: Med
-- ------------------------------------------------------
-- Server version	5.7.34-0ubuntu0.18.04.1

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
-- Table structure for table `Detection`
--

DROP TABLE IF EXISTS `Detection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Detection` (
  `DID` int(11) NOT NULL AUTO_INCREMENT,
  `PID` int(11) DEFAULT NULL,
  `stafes_id` int(11) DEFAULT NULL,
  `machine` char(32) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`DID`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Detection`
--

LOCK TABLES `Detection` WRITE;
/*!40000 ALTER TABLE `Detection` DISABLE KEYS */;
INSERT INTO `Detection` VALUES (1,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:36:39'),(2,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:39:56'),(3,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:40:25'),(4,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:47:09'),(5,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:49:58'),(6,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:50:37'),(7,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:51:15'),(8,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:52:46'),(9,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:54:50'),(10,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 01:59:50'),(11,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:09:42'),(12,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:10:05'),(13,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:10:31'),(14,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:10:45'),(15,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:17:36'),(16,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:29:04'),(17,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:30:26'),(18,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:30:55'),(19,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:31:34'),(20,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:41:08'),(21,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:41:43'),(22,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:43:45'),(23,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:46:40'),(24,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:52:09'),(25,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:52:34'),(26,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:55:25'),(27,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:55:43'),(28,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:56:00'),(29,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:56:08'),(30,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:56:26'),(31,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:56:39'),(32,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 02:57:05'),(33,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:00:02'),(34,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:00:17'),(35,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:00:28'),(36,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:03:42'),(37,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:08:26'),(38,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:15:56'),(39,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:16:12'),(40,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:19:51'),(41,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:20:15'),(42,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:20:26'),(43,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 04:10:32'),(44,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:36:28'),(45,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:32:53'),(46,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:32:57'),(47,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:33:20'),(48,1,3,'afed7b4b646cc5793b5776f87a0161ac','2021-05-13 03:34:01');
/*!40000 ALTER TABLE `Detection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MKUPPrescription`
--

DROP TABLE IF EXISTS `MKUPPrescription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MKUPPrescription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `PID` int(11) DEFAULT NULL,
  `med_code` char(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MKUPPrescription`
--

LOCK TABLES `MKUPPrescription` WRITE;
/*!40000 ALTER TABLE `MKUPPrescription` DISABLE KEYS */;
INSERT INTO `MKUPPrescription` VALUES (1,1,'MEDCOL'),(2,1,'MEDCOU'),(3,2,'MEDCOL'),(4,2,'MEDCOU'),(5,2,'MEDPAI'),(6,2,'MEDRHI');
/*!40000 ALTER TABLE `MKUPPrescription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MedList`
--

DROP TABLE IF EXISTS `MedList`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MedList` (
  `code` char(6) NOT NULL,
  `img` varchar(255) DEFAULT NULL,
  `ch_name` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `product_name` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `type` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `color` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `shape` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `notch` char(1) DEFAULT NULL,
  `print` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MedList`
--

LOCK TABLES `MedList` WRITE;
/*!40000 ALTER TABLE `MedList` DISABLE KEYS */;
INSERT INTO `MedList` VALUES ('MEDAPI',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('MEDCOL',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('MEDCOU',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),('MEDRHI',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `MedList` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Patients`
--

DROP TABLE IF EXISTS `Patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Patients` (
  `personal_id` char(10) NOT NULL,
  `name` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`personal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Patients`
--

LOCK TABLES `Patients` WRITE;
/*!40000 ALTER TABLE `Patients` DISABLE KEYS */;
INSERT INTO `Patients` VALUES ('E111111111','MedEye'),('E123456789','王大明');
/*!40000 ALTER TABLE `Patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Prescription`
--

DROP TABLE IF EXISTS `Prescription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Prescription` (
  `PID` int(11) NOT NULL AUTO_INCREMENT,
  `patients_id` char(10) DEFAULT NULL,
  `stafes_id` int(11) DEFAULT NULL,
  `type` char(2) CHARACTER SET utf8 DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`PID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Prescription`
--

LOCK TABLES `Prescription` WRITE;
/*!40000 ALTER TABLE `Prescription` DISABLE KEYS */;
INSERT INTO `Prescription` VALUES (1,'E123456789',3,'病房','2021-05-13 09:10:12'),(2,'E123456789',3,'病房','2021-05-13 09:10:12');
/*!40000 ALTER TABLE `Prescription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Stafes`
--

DROP TABLE IF EXISTS `Stafes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Stafes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_code` char(1) DEFAULT NULL,
  `name` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `passwd` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Stafes`
--

LOCK TABLES `Stafes` WRITE;
/*!40000 ALTER TABLE `Stafes` DISABLE KEYS */;
INSERT INTO `Stafes` VALUES (0,'D','MedEye','57cf655a5cc4fa33d9c838f48eb6749d'),(3,'N','hunter','e99a18c428cb38d5f260853678922e03');
/*!40000 ALTER TABLE `Stafes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `result`
--

DROP TABLE IF EXISTS `result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `DID` int(11) DEFAULT NULL,
  `med_code` char(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `result`
--

LOCK TABLES `result` WRITE;
/*!40000 ALTER TABLE `result` DISABLE KEYS */;
INSERT INTO `result` VALUES (1,4,'MEDPAI'),(2,4,'MEDCOU'),(3,4,'MEDCOL'),(4,4,'MEDRHI'),(5,5,'MEDPAI'),(6,5,'MEDCOU'),(7,5,'MEDCOL'),(8,5,'MEDRHI'),(9,6,'MEDCOU'),(10,6,'MEDCOL'),(11,6,'MEDRHI'),(12,6,'MEDPAI'),(13,7,'MEDCOU'),(14,7,'MEDCOL'),(15,7,'MEDRHI'),(16,7,'MEDPAI'),(17,8,'MEDCOU'),(18,8,'MEDCOL'),(19,8,'MEDRHI'),(20,8,'MEDPAI'),(21,9,'MEDRHI'),(22,9,'MEDCOL'),(23,10,'MEDRHI'),(24,10,'MEDCOL'),(25,11,'MEDPAI'),(26,11,'MEDRHI'),(27,11,'MEDCOU'),(28,11,'MEDCOL'),(29,13,'MEDRHI'),(30,14,'MEDRHI'),(31,15,'MEDCOL'),(32,15,'MEDRHI'),(33,17,'MEDCOU'),(34,17,'MEDRHI'),(35,17,'MEDPAI'),(36,17,'MEDCOL'),(37,18,'MEDCOU'),(38,18,'MEDRHI'),(39,18,'MEDPAI'),(40,18,'MEDCOL'),(41,19,'MEDCOU'),(42,19,'MEDRHI'),(43,19,'MEDPAI'),(44,19,'MEDCOL'),(45,24,'MEDRHI'),(46,24,'MEDPAI'),(47,24,'MEDCOL'),(48,24,'MEDCOU'),(49,25,'MEDRHI'),(50,25,'MEDCOU'),(51,25,'MEDPAI'),(52,25,'MEDCOL'),(53,29,'MEDRHI'),(54,29,'MEDPAI'),(55,30,'MEDRHI'),(56,30,'MEDPAI'),(57,31,'MEDRHI'),(58,31,'MEDPAI'),(59,32,'MEDRHI'),(60,32,'MEDPAI'),(61,36,'MEDRHI'),(62,36,'MEDPAI'),(63,36,'MEDCOU'),(64,37,'MEDPAI'),(65,37,'MEDRHI'),(66,37,'MEDCOU'),(67,38,'MEDPAI'),(68,38,'MEDRHI'),(69,38,'MEDCOU'),(70,39,'MEDRHI'),(71,39,'MEDPAI'),(72,39,'MEDCOU'),(73,40,'MEDPAI'),(74,40,'MEDCOU'),(75,41,'MEDPAI'),(76,41,'MEDCOU'),(77,42,'MEDCOU'),(78,42,'MEDPAI'),(79,45,'MEDCOU'),(80,45,'MEDPAI'),(81,45,'MEDRHI'),(82,46,'MEDCOU'),(83,46,'MEDPAI'),(84,46,'MEDRHI'),(85,47,'MEDPAI'),(86,47,'MEDRHI'),(87,48,'MEDCOU'),(88,48,'MEDRHI'),(89,48,'MEDPAI'),(90,48,'MEDCOL');
/*!40000 ALTER TABLE `result` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-05-14 13:23:02
