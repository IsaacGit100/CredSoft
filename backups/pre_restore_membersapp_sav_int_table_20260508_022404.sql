-- MySQL dump 10.13  Distrib 8.0.29, for Win64 (x86_64)
--
-- Host: localhost    Database: CredDb
-- ------------------------------------------------------
-- Server version	8.0.29

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `membersapp_sav_int_table`
--

DROP TABLE IF EXISTS `membersapp_sav_int_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membersapp_sav_int_table` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `min_date` date DEFAULT NULL,
  `sav_avail_bal` decimal(15,2) DEFAULT NULL,
  `sav_min_bal` decimal(15,2) DEFAULT NULL,
  `sav_min_days` int NOT NULL,
  `sav_int` decimal(15,2) DEFAULT NULL,
  `last_min_date` date DEFAULT NULL,
  `sav_int_calc_date` date DEFAULT NULL,
  `master_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `MembersApp_sav_int_t_master_id_301dfa31_fk_MembersAp` (`master_id`),
  CONSTRAINT `MembersApp_sav_int_t_master_id_301dfa31_fk_MembersAp` FOREIGN KEY (`master_id`) REFERENCES `membersapp_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membersapp_sav_int_table`
--

LOCK TABLES `membersapp_sav_int_table` WRITE;
/*!40000 ALTER TABLE `membersapp_sav_int_table` DISABLE KEYS */;
INSERT INTO `membersapp_sav_int_table` VALUES (1,'2026-05-01',0.00,0.00,2,0.00,'2026-05-01',NULL,6),(2,'2026-05-01',0.00,0.00,2,0.00,'2026-05-01',NULL,4),(3,'2026-05-01',0.00,0.00,2,0.00,'2026-05-01',NULL,5),(4,'2026-05-01',5000.00,5000.00,2,0.00,'2026-05-01',NULL,2),(5,'2026-05-01',20000.00,20000.00,2,0.00,'2026-05-01',NULL,3),(6,'2026-05-01',5000.00,5000.00,2,0.00,'2026-05-01',NULL,1),(7,'2026-05-03',200.00,200.00,4,0.00,'2026-05-03',NULL,6),(8,'2026-05-03',0.00,0.00,4,0.00,'2026-05-03',NULL,4),(9,'2026-05-03',0.00,0.00,4,0.00,'2026-05-03',NULL,5),(10,'2026-05-03',5000.00,5000.00,4,0.00,'2026-05-03',NULL,2),(11,'2026-05-03',20000.00,20000.00,4,0.00,'2026-05-03',NULL,3),(12,'2026-05-03',5000.00,5000.00,4,0.00,'2026-05-03',NULL,1),(13,'2026-05-07',1200.00,200.00,20,0.00,'2026-05-07',NULL,6),(14,'2026-05-07',0.00,0.00,20,0.00,'2026-05-07',NULL,4),(15,'2026-05-07',0.00,0.00,20,0.00,'2026-05-07',NULL,5),(16,'2026-05-07',5000.00,5000.00,20,0.00,'2026-05-07',NULL,2),(17,'2026-05-07',20000.00,20000.00,20,0.00,'2026-05-07',NULL,3),(18,'2026-05-07',5000.00,5000.00,20,0.00,'2026-05-07',NULL,1);
/*!40000 ALTER TABLE `membersapp_sav_int_table` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-08  2:24:05
