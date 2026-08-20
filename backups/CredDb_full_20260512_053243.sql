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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=209 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add system settings',7,'add_systemsettings'),(26,'Can change system settings',7,'change_systemsettings'),(27,'Can delete system settings',7,'delete_systemsettings'),(28,'Can view system settings',7,'view_systemsettings'),(29,'Can add user profile',8,'add_userprofile'),(30,'Can change user profile',8,'change_userprofile'),(31,'Can delete user profile',8,'delete_userprofile'),(32,'Can view user profile',8,'view_userprofile'),(33,'Can approve loans',8,'can_approve_loans'),(34,'Can post transactions',8,'can_post_transactions'),(35,'Can view reports',8,'can_view_reports'),(36,'Can manage users',8,'can_manage_users'),(37,'Can add master',9,'add_master'),(38,'Can change master',9,'change_master'),(39,'Can delete master',9,'delete_master'),(40,'Can view master',9,'view_master'),(41,'Can add ledger',10,'add_ledger'),(42,'Can change ledger',10,'change_ledger'),(43,'Can delete ledger',10,'delete_ledger'),(44,'Can view ledger',10,'view_ledger'),(45,'Can add chart of accounts',11,'add_chartofaccounts'),(46,'Can change chart of accounts',11,'change_chartofaccounts'),(47,'Can delete chart of accounts',11,'delete_chartofaccounts'),(48,'Can view chart of accounts',11,'view_chartofaccounts'),(49,'Can add Transaction',12,'add_trans'),(50,'Can change Transaction',12,'change_trans'),(51,'Can delete Transaction',12,'delete_trans'),(52,'Can view Transaction',12,'view_trans'),(53,'Can add loan',13,'add_loan'),(54,'Can change loan',13,'change_loan'),(55,'Can delete loan',13,'delete_loan'),(56,'Can view loan',13,'view_loan'),(57,'Can add guarantor',14,'add_guarantor'),(58,'Can change guarantor',14,'change_guarantor'),(59,'Can delete guarantor',14,'delete_guarantor'),(60,'Can view guarantor',14,'view_guarantor'),(61,'Can add bank',15,'add_bank'),(62,'Can change bank',15,'change_bank'),(63,'Can delete bank',15,'delete_bank'),(64,'Can view bank',15,'view_bank'),(65,'Can add investment',16,'add_investment'),(66,'Can change investment',16,'change_investment'),(67,'Can delete investment',16,'delete_investment'),(68,'Can view investment',16,'view_investment'),(69,'Can add journal line',17,'add_journalline'),(70,'Can change journal line',17,'change_journalline'),(71,'Can delete journal line',17,'delete_journalline'),(72,'Can view journal line',17,'view_journalline'),(73,'Can add general ledger',18,'add_generalledger'),(74,'Can change general ledger',18,'change_generalledger'),(75,'Can delete general ledger',18,'delete_generalledger'),(76,'Can view general ledger',18,'view_generalledger'),(77,'Can add journal entry',19,'add_journalentry'),(78,'Can change journal entry',19,'change_journalentry'),(79,'Can delete journal entry',19,'delete_journalentry'),(80,'Can view journal entry',19,'view_journalentry'),(81,'Can add help feedback',20,'add_helpfeedback'),(82,'Can change help feedback',20,'change_helpfeedback'),(83,'Can delete help feedback',20,'delete_helpfeedback'),(84,'Can view help feedback',20,'view_helpfeedback'),(85,'Can add help search',21,'add_helpsearch'),(86,'Can change help search',21,'change_helpsearch'),(87,'Can delete help search',21,'delete_helpsearch'),(88,'Can view help search',21,'view_helpsearch'),(89,'Can add user guide',22,'add_userguide'),(90,'Can change user guide',22,'change_userguide'),(91,'Can delete user guide',22,'delete_userguide'),(92,'Can view user guide',22,'view_userguide'),(93,'Can add help article',23,'add_helparticle'),(94,'Can change help article',23,'change_helparticle'),(95,'Can delete help article',23,'delete_helparticle'),(96,'Can view help article',23,'view_helparticle'),(97,'Can add help category',24,'add_helpcategory'),(98,'Can change help category',24,'change_helpcategory'),(99,'Can delete help category',24,'delete_helpcategory'),(100,'Can view help category',24,'view_helpcategory'),(101,'Can add help topic',25,'add_helptopic'),(102,'Can change help topic',25,'change_helptopic'),(103,'Can delete help topic',25,'delete_helptopic'),(104,'Can view help topic',25,'view_helptopic'),(105,'Can add ledger',26,'add_ledger'),(106,'Can change ledger',26,'change_ledger'),(107,'Can delete ledger',26,'delete_ledger'),(108,'Can view ledger',26,'view_ledger'),(109,'Can add transaction',27,'add_transaction'),(110,'Can change transaction',27,'change_transaction'),(111,'Can delete transaction',27,'delete_transaction'),(112,'Can view transaction',27,'view_transaction'),(113,'Can add journal line',28,'add_journalline'),(114,'Can change journal line',28,'change_journalline'),(115,'Can delete journal line',28,'delete_journalline'),(116,'Can view journal line',28,'view_journalline'),(117,'Can add journal entry',29,'add_journalentry'),(118,'Can change journal entry',29,'change_journalentry'),(119,'Can delete journal entry',29,'delete_journalentry'),(120,'Can view journal entry',29,'view_journalentry'),(121,'Can add account',30,'add_account'),(122,'Can change account',30,'change_account'),(123,'Can delete account',30,'delete_account'),(124,'Can view account',30,'view_account'),(125,'Can add branch',31,'add_branch'),(126,'Can change branch',31,'change_branch'),(127,'Can delete branch',31,'delete_branch'),(128,'Can view branch',31,'view_branch'),(129,'Can add chart of accounts',32,'add_chartofaccounts'),(130,'Can change chart of accounts',32,'change_chartofaccounts'),(131,'Can delete chart of accounts',32,'delete_chartofaccounts'),(132,'Can view chart of accounts',32,'view_chartofaccounts'),(133,'Can add ledger',33,'add_ledger'),(134,'Can change ledger',33,'change_ledger'),(135,'Can delete ledger',33,'delete_ledger'),(136,'Can view ledger',33,'view_ledger'),(137,'Can add account visibility preference',34,'add_accountvisibilitypreference'),(138,'Can change account visibility preference',34,'change_accountvisibilitypreference'),(139,'Can delete account visibility preference',34,'delete_accountvisibilitypreference'),(140,'Can view account visibility preference',34,'view_accountvisibilitypreference'),(141,'Can add audit log',35,'add_auditlog'),(142,'Can change audit log',35,'change_auditlog'),(143,'Can delete audit log',35,'delete_auditlog'),(144,'Can view audit log',35,'view_auditlog'),(145,'Can add fiscal period',36,'add_fiscalperiod'),(146,'Can change fiscal period',36,'change_fiscalperiod'),(147,'Can delete fiscal period',36,'delete_fiscalperiod'),(148,'Can view fiscal period',36,'view_fiscalperiod'),(149,'Can add system preference',37,'add_systempreference'),(150,'Can change system preference',37,'change_systempreference'),(151,'Can delete system preference',37,'delete_systempreference'),(152,'Can view system preference',37,'view_systempreference'),(153,'Can add loan repayment',38,'add_loanrepayment'),(154,'Can change loan repayment',38,'change_loanrepayment'),(155,'Can delete loan repayment',38,'delete_loanrepayment'),(156,'Can view loan repayment',38,'view_loanrepayment'),(157,'Can add loan schedule',39,'add_loanschedule'),(158,'Can change loan schedule',39,'change_loanschedule'),(159,'Can delete loan schedule',39,'delete_loanschedule'),(160,'Can view loan schedule',39,'view_loanschedule'),(161,'Can add Saved Report',40,'add_savedreport'),(162,'Can change Saved Report',40,'change_savedreport'),(163,'Can delete Saved Report',40,'delete_savedreport'),(164,'Can view Saved Report',40,'view_savedreport'),(165,'Can add batch process',41,'add_batchprocess'),(166,'Can change batch process',41,'change_batchprocess'),(167,'Can delete batch process',41,'delete_batchprocess'),(168,'Can view batch process',41,'view_batchprocess'),(169,'Can add batch process log',42,'add_batchprocesslog'),(170,'Can change batch process log',42,'change_batchprocesslog'),(171,'Can delete batch process log',42,'delete_batchprocesslog'),(172,'Can view batch process log',42,'view_batchprocesslog'),(173,'Can add database backup',43,'add_databasebackup'),(174,'Can change database backup',43,'change_databasebackup'),(175,'Can delete database backup',43,'delete_databasebackup'),(176,'Can view database backup',43,'view_databasebackup'),(177,'Can add member login history',44,'add_memberloginhistory'),(178,'Can change member login history',44,'change_memberloginhistory'),(179,'Can delete member login history',44,'delete_memberloginhistory'),(180,'Can view member login history',44,'view_memberloginhistory'),(181,'Can add admin login history',45,'add_adminloginhistory'),(182,'Can change admin login history',45,'change_adminloginhistory'),(183,'Can delete admin login history',45,'delete_adminloginhistory'),(184,'Can view admin login history',45,'view_adminloginhistory'),(185,'Can add loan transaction',46,'add_loantransaction'),(186,'Can change loan transaction',46,'change_loantransaction'),(187,'Can delete loan transaction',46,'delete_loantransaction'),(188,'Can view loan transaction',46,'view_loantransaction'),(189,'Can add sav_ int_ table',47,'add_sav_int_table'),(190,'Can change sav_ int_ table',47,'change_sav_int_table'),(191,'Can delete sav_ int_ table',47,'delete_sav_int_table'),(192,'Can view sav_ int_ table',47,'view_sav_int_table'),(193,'Can add state update',48,'add_stateupdate'),(194,'Can change state update',48,'change_stateupdate'),(195,'Can delete state update',48,'delete_stateupdate'),(196,'Can view state update',48,'view_stateupdate'),(197,'Can add state trans',49,'add_statetrans'),(198,'Can change state trans',49,'change_statetrans'),(199,'Can delete state trans',49,'delete_statetrans'),(200,'Can view state trans',49,'view_statetrans'),(201,'Can add Backup Log',50,'add_backuplog'),(202,'Can change Backup Log',50,'change_backuplog'),(203,'Can delete Backup Log',50,'delete_backuplog'),(204,'Can view Backup Log',50,'view_backuplog'),(205,'Can add restore job',51,'add_restorejob'),(206,'Can change restore job',51,'change_restorejob'),(207,'Can delete restore job',51,'delete_restorejob'),(208,'Can view restore job',51,'view_restorejob');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$FwsuGGFDmxWfVCjZKOZRv5$WoGi1h16GH6JcwF5vC4QF9eP6C+bHRhZUBFucHiHxn0=','2026-05-12 05:30:48.390626',1,'Admin','','','isaac_quaye@yahoo.com',1,1,'2026-03-28 04:23:33.165808'),(2,'pbkdf2_sha256$1000000$QSSEOdpXLe22Dl6I7dwoil$RdO5KJbOXRJ2uUJHiuCyZ2Seu7Qyb99mA9mytOX8jW4=','2026-04-02 17:05:10.114280',1,'isaac','','','I@gmail.com',1,1,'2026-04-02 00:22:52.707809');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `backuprestore_backuplog`
--

DROP TABLE IF EXISTS `backuprestore_backuplog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `backuprestore_backuplog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timestamp` datetime(6) NOT NULL,
  `action` varchar(10) NOT NULL,
  `result` varchar(10) NOT NULL,
  `table_name` varchar(100) DEFAULT NULL,
  `backup_file` varchar(255) DEFAULT NULL,
  `details` longtext,
  `ip_address` char(39) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `BackupRestore_backuplog_user_id_60bc4929_fk_auth_user_id` (`user_id`),
  CONSTRAINT `BackupRestore_backuplog_user_id_60bc4929_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backuprestore_backuplog`
--

LOCK TABLES `backuprestore_backuplog` WRITE;
/*!40000 ALTER TABLE `backuprestore_backuplog` DISABLE KEYS */;
INSERT INTO `backuprestore_backuplog` VALUES (1,'2026-05-08 10:51:15.462991','RESTORE','FAILURE','accounting_account','CredDb_full_20260507_203528.sql','Table is empty after restore.','127.0.0.1',1),(2,'2026-05-11 11:07:55.072840','RESTORE','FAILURE','accounting_account','CredDb_full_20260511_110406.sql','Table is empty after restore.','127.0.0.1',1),(3,'2026-05-11 15:47:08.982017','BACKUP','SUCCESS',NULL,'CredDb_full_20260511_154707.sql',NULL,'127.0.0.1',1),(4,'2026-05-12 05:10:37.435897','RESTORE','SUCCESS','auth_group','pre_restore_auth_group_20260512_041509.sql',NULL,NULL,1),(5,'2026-05-12 05:16:26.895563','RESTORE','SUCCESS','auth_group','pre_restore_auth_group_20260512_051035.sql',NULL,NULL,1),(6,'2026-05-12 05:17:30.565562','RESTORE','SUCCESS','auth_group','pre_restore_auth_group_20260512_051035.sql',NULL,NULL,1),(7,'2026-05-12 05:19:39.553741','RESTORE','SUCCESS','auth_group','CredDb_full_20260512_051746.sql',NULL,NULL,1),(8,'2026-05-12 05:31:00.860130','RESTORE','SUCCESS','auth_group','pre_restore_auth_group_20260512_051758.sql',NULL,NULL,1);
/*!40000 ALTER TABLE `backuprestore_backuplog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `backuprestore_restorejob`
--

DROP TABLE IF EXISTS `backuprestore_restorejob`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `backuprestore_restorejob` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `job_id` varchar(100) NOT NULL,
  `status` varchar(10) NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `table_name` varchar(100) NOT NULL,
  `backup_file` varchar(255) NOT NULL,
  `error_message` longtext NOT NULL,
  `created_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `job_id` (`job_id`),
  KEY `BackupRestore_restorejob_created_by_id_ed11f588_fk_auth_user_id` (`created_by_id`),
  CONSTRAINT `BackupRestore_restorejob_created_by_id_ed11f588_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backuprestore_restorejob`
--

LOCK TABLES `backuprestore_restorejob` WRITE;
/*!40000 ALTER TABLE `backuprestore_restorejob` DISABLE KEYS */;
/*!40000 ALTER TABLE `backuprestore_restorejob` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coa_accountvisibilitypreference`
--

DROP TABLE IF EXISTS `coa_accountvisibilitypreference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coa_accountvisibilitypreference` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_visible` tinyint(1) NOT NULL,
  `order` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `coa_accountvisibilitypreference_user_id_account_id_e589d12e_uniq` (`user_id`,`account_id`),
  KEY `coa_accountvisibilit_account_id_877704a4_fk_coa_chart` (`account_id`),
  CONSTRAINT `coa_accountvisibilit_account_id_877704a4_fk_coa_chart` FOREIGN KEY (`account_id`) REFERENCES `coa_07052026` (`id`),
  CONSTRAINT `coa_accountvisibilitypreference_user_id_0d67d816_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coa_accountvisibilitypreference`
--

LOCK TABLES `coa_accountvisibilitypreference` WRITE;
/*!40000 ALTER TABLE `coa_accountvisibilitypreference` DISABLE KEYS */;
INSERT INTO `coa_accountvisibilitypreference` VALUES (93,0,0,'2026-04-06 04:00:29.518483','2026-04-06 04:00:29.518483',11,1),(94,0,0,'2026-04-06 04:00:29.518483','2026-04-06 04:00:29.518483',12,1),(95,0,0,'2026-04-06 04:00:29.518483','2026-04-06 04:00:29.518483',13,1),(96,0,0,'2026-04-06 04:00:29.534594','2026-04-06 04:00:29.534594',14,1),(97,0,0,'2026-04-06 04:00:29.536595','2026-04-06 04:00:29.536595',15,1),(98,0,0,'2026-04-06 04:00:29.538608','2026-04-06 04:00:29.538608',16,1),(99,1,0,'2026-04-06 04:00:29.541591','2026-04-06 04:00:29.541591',19,1),(100,1,0,'2026-04-06 04:00:29.543606','2026-04-06 04:00:29.543606',20,1),(101,1,0,'2026-04-06 04:00:29.549682','2026-04-06 04:00:29.549682',21,1),(102,1,0,'2026-04-06 04:00:29.551918','2026-04-06 04:00:29.551918',23,1),(103,1,0,'2026-04-06 04:00:29.551918','2026-04-06 04:00:29.551918',24,1),(104,1,0,'2026-04-06 04:00:29.551918','2026-04-06 04:00:29.551918',25,1),(105,1,0,'2026-04-06 04:00:29.551918','2026-04-06 04:00:29.551918',26,1),(106,0,0,'2026-04-06 04:00:29.551918','2026-04-06 04:00:29.551918',30,1),(107,1,0,'2026-04-06 04:00:29.567608','2026-04-06 04:00:29.567608',31,1),(108,1,0,'2026-04-06 04:00:29.567608','2026-04-06 04:00:29.567608',32,1),(109,0,0,'2026-04-06 04:00:29.567608','2026-04-06 04:00:29.567608',33,1),(110,1,0,'2026-04-06 04:00:29.567608','2026-04-06 04:00:29.567608',37,1);
/*!40000 ALTER TABLE `coa_accountvisibilitypreference` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coa_chartofaccounts`
--

DROP TABLE IF EXISTS `coa_chartofaccounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coa_chartofaccounts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `accountno` varchar(8) DEFAULT NULL,
  `name` varchar(200) NOT NULL,
  `account_type` varchar(20) NOT NULL,
  `behavior` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `parent_account_id` bigint DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_data_entry` tinyint(1) NOT NULL,
  `is_data_filled` tinyint(1) NOT NULL,
  `is_data_view` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_no` (`accountno`),
  KEY `coa_chartofaccounts_parent_account_id_b2b7c806_fk_coa_chart` (`parent_account_id`),
  CONSTRAINT `coa_chartofaccounts_parent_account_id_b2b7c806_fk_coa_chart` FOREIGN KEY (`parent_account_id`) REFERENCES `coa_chartofaccounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coa_chartofaccounts`
--

LOCK TABLES `coa_chartofaccounts` WRITE;
/*!40000 ALTER TABLE `coa_chartofaccounts` DISABLE KEYS */;
INSERT INTO `coa_chartofaccounts` VALUES (1,'10000000','ASSETS','ASSET','NORMAL',1,NULL,'2026-04-06 00:33:06.360990',0,0,1,'2026-04-06 00:33:06.360990'),(2,'20000000','LIABILITIES','LIABILITY','NORMAL',1,NULL,'2026-04-06 00:33:29.741800',0,0,1,'2026-04-06 00:33:29.741800'),(3,'30000000','EQUITY','EQUITY','NORMAL',1,NULL,'2026-04-06 00:33:57.734284',0,0,1,'2026-04-06 00:33:57.734284'),(4,'40000000','INCOME','INCOME','NORMAL',1,NULL,'2026-04-06 00:34:22.640991',0,0,1,'2026-04-06 00:34:22.640991'),(5,'50000000','EXPENSES','EXPENSE','NORMAL',1,NULL,'2026-04-06 00:34:46.714294',0,0,1,'2026-04-06 00:34:46.714294'),(6,'10100000','CASH AND CASH EQUIVALENTS','ASSET','NORMAL',1,1,'2026-04-06 00:35:49.007273',0,0,1,'2026-04-06 00:35:49.007273'),(7,'10101000','CASH IN HAND','ASSET','NORMAL',1,6,'2026-04-06 00:58:55.788056',0,0,1,'2026-04-06 00:58:55.788056'),(8,'10102000','BANK ACCOUNTS','ASSET','NORMAL',1,6,'2026-04-06 00:59:39.348661',0,0,1,'2026-04-06 00:59:39.348661'),(9,'10103000','MOBILE MONEY','ASSET','NORMAL',1,6,'2026-04-06 01:00:22.093415',0,0,1,'2026-04-06 01:00:22.093415'),(10,'10104000','CHEQUES IN CLEARING','ASSET','NORMAL',1,6,'2026-04-06 01:01:23.937996',0,0,1,'2026-04-06 01:01:23.937996'),(11,'10101001','Cash In Hand Cashier1','ASSET','CASH',1,7,'2026-04-06 06:40:29.188318',1,0,0,'2026-04-06 01:02:52.472237'),(12,'10101002','Cash In Hand Cashier2','ASSET','CASH',1,7,'2026-04-06 06:40:29.190300',1,0,0,'2026-04-06 01:03:57.894305'),(13,'10102001','GCB Bank Plc Haatso','ASSET','BANK',1,8,'2026-04-06 06:40:29.191318',1,0,0,'2026-04-06 01:05:26.681874'),(14,'10102002','GCB Bank PLC Adum','ASSET','BANK',1,8,'2026-04-06 06:40:29.192316',1,0,0,'2026-04-06 01:06:23.775518'),(15,'10102003','NIB Bank Head Office Accra','ASSET','BANK',1,8,'2026-04-06 06:40:29.193296',1,0,0,'2026-04-06 01:07:32.083039'),(16,'10103001','Mobile Money Account 0002456','ASSET','MOMO',1,9,'2026-04-06 06:40:29.194315',1,0,0,'2026-04-06 01:08:47.322151'),(17,'20100000','MEMBER LIABILITIES','LIABILITY','NORMAL',1,2,'2026-04-06 02:20:10.969982',0,0,1,'2026-04-06 02:20:10.969982'),(18,'20101000','MEMBER SAVINGS','LIABILITY','NORMAL',1,17,'2026-04-06 02:21:07.436904',0,0,1,'2026-04-06 02:21:07.436904'),(19,'20101001','Savings Deposit','LIABILITY','SAVINGS',1,18,'2026-04-06 02:22:14.469570',1,0,1,'2026-04-06 02:22:14.469570'),(20,'20101002','Savings Withdrawal','ASSET','SAVINGS',1,18,'2026-04-06 02:23:11.729722',1,0,1,'2026-04-06 02:23:11.729722'),(21,'20101003','Savings Interest Payable','LIABILITY','SAVINGS',1,18,'2026-04-06 02:24:23.839721',1,0,1,'2026-04-06 02:24:23.839721'),(22,'20102000','SHARE CAPITAL','LIABILITY','NORMAL',1,17,'2026-04-06 02:31:59.166067',0,0,1,'2026-04-06 02:31:59.166067'),(23,'20102001','Share Capital','LIABILITY','NORMAL',1,22,'2026-04-06 02:33:03.605501',1,0,1,'2026-04-06 02:33:03.605501'),(24,'20102002','Share Withdrawal','LIABILITY','NORMAL',1,22,'2026-04-06 02:34:06.242458',1,0,1,'2026-04-06 02:34:06.242458'),(25,'20102003','Dividend Payable','LIABILITY','NORMAL',1,22,'2026-04-06 02:35:30.002208',1,0,1,'2026-04-06 02:35:30.002208'),(26,'20102004','Dividend Withdrawal','LIABILITY','NORMAL',1,22,'2026-04-06 02:36:35.593213',1,0,1,'2026-04-06 02:36:35.593213'),(27,'40100000','OPERATING INCOME','INCOME','NORMAL',1,4,'2026-04-06 03:03:51.936968',0,0,1,'2026-04-06 03:03:51.936968'),(28,'40101000','INTEREST INCOME','INCOME','NORMAL',1,27,'2026-04-06 03:04:59.042122',0,0,1,'2026-04-06 03:04:59.042122'),(29,'40102000','FEE INCOME','INCOME','NORMAL',1,27,'2026-04-06 03:05:50.167207',0,0,1,'2026-04-06 03:05:50.167207'),(30,'40101001','Loan Interest Income','INCOME','NORMAL',1,28,'2026-04-06 06:40:29.195314',1,0,0,'2026-04-06 03:06:47.794256'),(31,'40101002','Investment Interest Income','INCOME','NORMAL',1,28,'2026-04-06 06:40:29.196314',1,0,0,'2026-04-06 03:07:57.219967'),(32,'40102001','Enrollment Fees','INCOME','NORMAL',1,29,'2026-04-06 03:09:00.995184',1,0,1,'2026-04-06 03:09:00.995184'),(33,'40102002','Loan Processing Fees','INCOME','NORMAL',1,29,'2026-04-06 03:09:57.855611',1,0,1,'2026-04-06 03:09:57.855611'),(34,'50100000','OPERATING EXPENSES','EXPENSE','NORMAL',1,5,'2026-04-06 03:13:47.606876',0,0,1,'2026-04-06 03:13:47.606876'),(35,'50101000','PERSONNEL EXPENSES','EXPENSE','NORMAL',1,34,'2026-04-06 03:14:55.923477',0,0,1,'2026-04-06 03:14:55.923477'),(36,'50102000','ADMNISTRATIVE EXPENSES','EXPENSE','NORMAL',1,34,'2026-04-06 03:15:51.459252',0,0,1,'2026-04-06 03:15:51.459252'),(37,'50101001','Salaries and Allowances','EXPENSE','NORMAL',1,35,'2026-04-06 03:17:01.765977',1,0,1,'2026-04-06 03:17:01.765977'),(38,'10105000','LOAN RECEIVABLES','ASSET','NORMAL',1,6,'2026-04-21 06:00:25.132400',0,0,1,'2026-04-21 06:00:25.132400'),(39,'10105001','Loan Disbursements','ASSET','NORMAL',1,38,'2026-04-21 06:01:25.713149',1,0,1,'2026-04-21 06:01:25.713149'),(40,'10105002','Loan Repayments ','ASSET','NORMAL',1,38,'2026-04-21 06:02:44.547964',1,0,1,'2026-04-21 06:02:44.547964'),(41,'10105003','Loan Interest Receivables','ASSET','NORMAL',1,38,'2026-04-21 06:19:17.999408',1,0,1,'2026-04-21 06:19:17.999408'),(42,'50102001','Furniture Repairs','EXPENSE','NORMAL',1,36,'2026-05-01 21:32:08.053815',0,0,1,'2026-05-01 21:32:08.053815'),(43,'50102002','Equipment Repairs','EXPENSE','NORMAL',1,36,'2026-05-01 21:33:21.206478',0,0,1,'2026-05-01 21:33:21.206478'),(44,'50102003','Stationery','EXPENSE','NORMAL',1,36,'2026-05-01 21:34:01.592372',0,0,1,'2026-05-01 21:34:01.592372'),(45,'50102004','T & T','EXPENSE','NORMAL',1,36,'2026-05-01 21:34:39.398073',0,0,1,'2026-05-01 21:34:39.398073');
/*!40000 ALTER TABLE `coa_chartofaccounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coaapp_chartofaccounts`
--

DROP TABLE IF EXISTS `coaapp_chartofaccounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coaapp_chartofaccounts` (
  `account_number` varchar(10) NOT NULL,
  `account_name` varchar(100) NOT NULL,
  `account_class` varchar(1) NOT NULL,
  `account_type` varchar(10) NOT NULL,
  `normal_balance` varchar(6) NOT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `level` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `parent_account_id` varchar(10) DEFAULT NULL,
  `line_order_no` int NOT NULL,
  PRIMARY KEY (`account_number`),
  KEY `CoaApp_chartofaccoun_parent_account_id_73fae8e9_fk_CoaApp_ch` (`parent_account_id`),
  CONSTRAINT `CoaApp_chartofaccoun_parent_account_id_73fae8e9_fk_CoaApp_ch` FOREIGN KEY (`parent_account_id`) REFERENCES `coaapp_chartofaccounts` (`account_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coaapp_chartofaccounts`
--

LOCK TABLES `coaapp_chartofaccounts` WRITE;
/*!40000 ALTER TABLE `coaapp_chartofaccounts` DISABLE KEYS */;
/*!40000 ALTER TABLE `coaapp_chartofaccounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coaapp_ledger`
--

DROP TABLE IF EXISTS `coaapp_ledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coaapp_ledger` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `Description` varchar(200) NOT NULL,
  `OpeningBalance` decimal(15,2) NOT NULL,
  `Debit` decimal(15,2) NOT NULL,
  `Credit` decimal(15,2) NOT NULL,
  `AccountNo_id` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `CoaApp_ledger_AccountNo_id_31f9ba7b_fk_CoaApp_ch` (`AccountNo_id`),
  CONSTRAINT `CoaApp_ledger_AccountNo_id_31f9ba7b_fk_CoaApp_ch` FOREIGN KEY (`AccountNo_id`) REFERENCES `coaapp_chartofaccounts` (`account_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coaapp_ledger`
--

LOCK TABLES `coaapp_ledger` WRITE;
/*!40000 ALTER TABLE `coaapp_ledger` DISABLE KEYS */;
/*!40000 ALTER TABLE `coaapp_ledger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coreapp_batchprocess`
--

DROP TABLE IF EXISTS `coreapp_batchprocess`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coreapp_batchprocess` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `process_type` varchar(50) NOT NULL,
  `process_name` varchar(100) NOT NULL,
  `frequency` varchar(20) NOT NULL,
  `last_run` datetime(6) DEFAULT NULL,
  `last_run_status` varchar(20) NOT NULL,
  `last_run_message` longtext NOT NULL,
  `next_run_due` datetime(6) DEFAULT NULL,
  `total_runs` int NOT NULL,
  `successful_runs` int NOT NULL,
  `failed_runs` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `requires_approval` tinyint(1) NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `approved_by_id` int DEFAULT NULL,
  `last_run_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `process_type` (`process_type`),
  KEY `CoreApp_batchprocess_approved_by_id_39b4c4e2_fk_auth_user_id` (`approved_by_id`),
  KEY `CoreApp_batchprocess_last_run_by_id_f8d884f6_fk_auth_user_id` (`last_run_by_id`),
  CONSTRAINT `CoreApp_batchprocess_approved_by_id_39b4c4e2_fk_auth_user_id` FOREIGN KEY (`approved_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `CoreApp_batchprocess_last_run_by_id_f8d884f6_fk_auth_user_id` FOREIGN KEY (`last_run_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coreapp_batchprocess`
--

LOCK TABLES `coreapp_batchprocess` WRITE;
/*!40000 ALTER TABLE `coreapp_batchprocess` DISABLE KEYS */;
INSERT INTO `coreapp_batchprocess` VALUES (1,'SAVINGS_INTEREST','Savings Interest Accrual','DAILY',NULL,'PENDING','','2026-04-19 18:35:54.701373',0,0,0,1,0,NULL,'2026-04-19 18:35:54.718220','2026-04-19 18:35:54.718220',NULL,NULL),(2,'LOAN_INTEREST','Loan Interest Calculation','DAILY',NULL,'PENDING','','2026-04-19 18:35:54.784825',0,0,0,1,0,NULL,'2026-04-19 18:35:54.801461','2026-04-19 18:35:54.801461',NULL,NULL),(3,'LOAN_PENALTY','Loan Penalty Calculation','DAILY',NULL,'PENDING','','2026-04-19 18:35:54.852607',0,0,0,1,0,NULL,'2026-04-19 18:35:54.852607','2026-04-19 18:35:54.852607',NULL,NULL),(4,'DAILY_REPORT','Daily Report Generation','DAILY',NULL,'PENDING','','2026-04-19 18:35:54.934767',0,0,0,1,0,NULL,'2026-04-19 18:35:54.934767','2026-04-19 18:35:54.934767',NULL,NULL),(5,'BACKUP','Database Backup','DAILY',NULL,'PENDING','','2026-04-19 18:35:54.969843',0,0,0,1,0,NULL,'2026-04-19 18:35:54.985285','2026-04-19 18:35:54.985285',NULL,NULL),(6,'MONTHLY_REPORT','Monthly Report Generation','MONTHLY',NULL,'PENDING','','2026-04-19 18:35:55.035824',0,0,0,1,0,NULL,'2026-04-19 18:35:55.051517','2026-04-19 18:35:55.051517',NULL,NULL),(7,'QUARTERLY_REPORT','Quarterly Report Generation','QUARTERLY',NULL,'PENDING','','2026-04-19 18:35:55.102615',0,0,0,1,0,NULL,'2026-04-19 18:35:55.102615','2026-04-19 18:35:55.102615',NULL,NULL),(8,'YEAR_END','Year End Closing','YEARLY',NULL,'PENDING','','2026-04-19 18:35:55.152210',0,0,0,1,0,NULL,'2026-04-19 18:35:55.152210','2026-04-19 18:35:55.152210',NULL,NULL);
/*!40000 ALTER TABLE `coreapp_batchprocess` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coreapp_batchprocesslog`
--

DROP TABLE IF EXISTS `coreapp_batchprocesslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coreapp_batchprocesslog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `started_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `message` longtext NOT NULL,
  `error_details` longtext NOT NULL,
  `records_processed` int NOT NULL,
  `process_id` bigint NOT NULL,
  `run_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CoreApp_batchprocess_process_id_2ee5900a_fk_CoreApp_b` (`process_id`),
  KEY `CoreApp_batchprocesslog_run_by_id_91083467_fk_auth_user_id` (`run_by_id`),
  CONSTRAINT `CoreApp_batchprocess_process_id_2ee5900a_fk_CoreApp_b` FOREIGN KEY (`process_id`) REFERENCES `coreapp_batchprocess` (`id`),
  CONSTRAINT `CoreApp_batchprocesslog_run_by_id_91083467_fk_auth_user_id` FOREIGN KEY (`run_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coreapp_batchprocesslog`
--

LOCK TABLES `coreapp_batchprocesslog` WRITE;
/*!40000 ALTER TABLE `coreapp_batchprocesslog` DISABLE KEYS */;
/*!40000 ALTER TABLE `coreapp_batchprocesslog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coreapp_databasebackup`
--

DROP TABLE IF EXISTS `coreapp_databasebackup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coreapp_databasebackup` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `backup_name` varchar(200) NOT NULL,
  `backup_file` varchar(100) DEFAULT NULL,
  `file_size` bigint NOT NULL,
  `status` varchar(20) NOT NULL,
  `tables_backup` longtext NOT NULL,
  `backup_started` datetime(6) NOT NULL,
  `backup_completed` datetime(6) DEFAULT NULL,
  `notes` longtext NOT NULL,
  `created_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `CoreApp_databasebackup_created_by_id_26bfbad8_fk_auth_user_id` (`created_by_id`),
  CONSTRAINT `CoreApp_databasebackup_created_by_id_26bfbad8_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coreapp_databasebackup`
--

LOCK TABLES `coreapp_databasebackup` WRITE;
/*!40000 ALTER TABLE `coreapp_databasebackup` DISABLE KEYS */;
/*!40000 ALTER TABLE `coreapp_databasebackup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customreports_savedreport`
--

DROP TABLE IF EXISTS `customreports_savedreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customreports_savedreport` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `table_name` varchar(50) NOT NULL,
  `selected_fields` longtext NOT NULL,
  `filters` longtext,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customreports_savedreport`
--

LOCK TABLES `customreports_savedreport` WRITE;
/*!40000 ALTER TABLE `customreports_savedreport` DISABLE KEYS */;
/*!40000 ALTER TABLE `customreports_savedreport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (30,'accounting','account'),(29,'accounting','journalentry'),(28,'accounting','journalline'),(26,'accounting','ledger'),(27,'accounting','transaction'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(50,'BackupRestore','backuplog'),(51,'BackupRestore','restorejob'),(34,'coa','accountvisibilitypreference'),(31,'coa','branch'),(11,'coa','chartofaccounts'),(10,'coa','ledger'),(32,'CoaApp','chartofaccounts'),(33,'CoaApp','ledger'),(5,'contenttypes','contenttype'),(41,'CoreApp','batchprocess'),(42,'CoreApp','batchprocesslog'),(43,'CoreApp','databasebackup'),(40,'CustomReports','savedreport'),(18,'FinanceApp','generalledger'),(19,'FinanceApp','journalentry'),(17,'FinanceApp','journalline'),(23,'help_module','helparticle'),(24,'help_module','helpcategory'),(20,'help_module','helpfeedback'),(21,'help_module','helpsearch'),(25,'help_module','helptopic'),(22,'help_module','userguide'),(15,'InvestApp','bank'),(16,'InvestApp','investment'),(14,'LoanApp','guarantor'),(13,'LoanApp','loan'),(38,'LoanApp','loanrepayment'),(39,'LoanApp','loanschedule'),(46,'LoanApp','loantransaction'),(45,'LoginApp','adminloginhistory'),(44,'LoginApp','memberloginhistory'),(9,'MembersApp','master'),(47,'MembersApp','sav_int_table'),(12,'RecPayApp','trans'),(49,'services','statetrans'),(48,'services','stateupdate'),(6,'sessions','session'),(35,'SysSetup','auditlog'),(36,'SysSetup','fiscalperiod'),(37,'SysSetup','systempreference'),(7,'SysSetup','systemsettings'),(8,'UserAuth','userprofile');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-03-28 00:53:08.141110'),(2,'auth','0001_initial','2026-03-28 00:53:24.599615'),(3,'admin','0001_initial','2026-03-28 00:53:28.242137'),(4,'admin','0002_logentry_remove_auto_add','2026-03-28 00:53:28.335933'),(5,'admin','0003_logentry_add_action_flag_choices','2026-03-28 00:53:28.444898'),(6,'contenttypes','0002_remove_content_type_name','2026-03-28 00:53:30.433870'),(7,'auth','0002_alter_permission_name_max_length','2026-03-28 00:53:32.019123'),(8,'auth','0003_alter_user_email_max_length','2026-03-28 00:53:32.377562'),(9,'auth','0004_alter_user_username_opts','2026-03-28 00:53:32.492941'),(10,'auth','0005_alter_user_last_login_null','2026-03-28 00:53:34.168944'),(11,'auth','0006_require_contenttypes_0002','2026-03-28 00:53:34.215816'),(12,'auth','0007_alter_validators_add_error_messages','2026-03-28 00:53:34.311210'),(13,'auth','0008_alter_user_username_max_length','2026-03-28 00:53:35.970547'),(14,'auth','0009_alter_user_last_name_max_length','2026-03-28 00:53:37.820717'),(15,'auth','0010_alter_group_name_max_length','2026-03-28 00:53:38.021108'),(16,'auth','0011_update_proxy_permissions','2026-03-28 00:53:38.082760'),(17,'auth','0012_alter_user_first_name_max_length','2026-03-28 00:53:40.078407'),(18,'sessions','0001_initial','2026-03-28 00:53:41.016612'),(19,'SysSetup','0001_initial','2026-03-28 03:00:13.137807'),(20,'UserAuth','0001_initial','2026-03-28 03:00:16.067375'),(22,'coa','0001_initial','2026-03-28 04:16:38.082778'),(25,'InvestApp','0001_initial','2026-03-31 19:01:35.186021'),(26,'MembersApp','0001_initial','2026-04-01 06:02:06.756974'),(27,'RecPayApp','0001_initial','2026-04-01 06:02:22.984280'),(28,'FinanceApp','0001_initial','2026-04-01 06:02:46.737124'),(29,'LoanApp','0001_initial','2026-04-01 06:02:55.269651'),(30,'help_module','0001_initial','2026-04-01 06:03:27.044128'),(31,'accounting','0001_initial','2026-04-01 17:47:39.221550'),(32,'coa','0002_branch_alter_chartofaccounts_options_and_more','2026-04-02 19:41:02.303994'),(33,'CoaApp','0001_initial','2026-04-03 01:30:46.561748'),(34,'CoaApp','0002_chartofaccounts_line_order_no','2026-04-03 01:30:47.032245'),(35,'coa','0003_remove_chartofaccounts_branch_delete_ledger_and_more','2026-04-03 02:23:14.770260'),(36,'coa','0004_alter_chartofaccounts_accountno','2026-04-03 03:10:19.361522'),(37,'coa','0005_chartofaccounts_is_data_entry_and_more','2026-04-03 03:17:55.079097'),(38,'coa','0006_alter_chartofaccounts_accountno','2026-04-03 03:38:52.889391'),(39,'coa','0007_alter_chartofaccounts_options','2026-04-03 04:50:33.377392'),(40,'coa','0008_alter_chartofaccounts_options_and_more','2026-04-03 04:54:39.732605'),(41,'coa','0009_alter_chartofaccounts_options_and_more','2026-04-03 05:18:42.665640'),(42,'coa','0010_alter_chartofaccounts_options_and_more','2026-04-03 05:18:43.161934'),(43,'coa','0011_alter_chartofaccounts_options_and_more','2026-04-03 05:21:04.746105'),(44,'coa','0012_alter_chartofaccounts_options_and_more','2026-04-03 05:22:18.612136'),(45,'coa','0013_alter_chartofaccounts_account_type_and_more','2026-04-03 05:43:21.170784'),(46,'coa','0014_alter_chartofaccounts_account_type_and_more','2026-04-04 22:03:24.866006'),(47,'coa','0015_alter_chartofaccounts_accountno','2026-04-05 01:09:22.424490'),(48,'coa','0016_alter_chartofaccounts_accountno_and_more','2026-04-05 03:06:36.519699'),(49,'coa','0017_alter_chartofaccounts_options','2026-04-05 05:34:05.524037'),(50,'coa','0018_alter_chartofaccounts_options','2026-04-05 17:58:11.374545'),(51,'coa','0019_accountvisibilitypreference','2026-04-05 23:36:14.554417'),(52,'RecPayApp','0002_trans_loan_id','2026-04-06 07:15:28.493437'),(53,'RecPayApp','0003_remove_trans_loan_id_trans_loan','2026-04-06 07:26:17.570578'),(54,'RecPayApp','0004_alter_trans_ledger_code_alter_trans_ledger_id_and_more','2026-04-06 07:28:29.245682'),(55,'SysSetup','0002_systemsettings_bank_account_name1_and_more','2026-04-11 01:37:24.818318'),(56,'SysSetup','0003_systemsettings_savings_interest_application','2026-04-11 01:58:18.727629'),(57,'SysSetup','0004_systemsettings_stop_savings_interest_calculation','2026-04-11 02:00:57.722394'),(58,'SysSetup','0005_remove_systempreference_date_format','2026-04-11 02:03:18.712402'),(59,'LoanApp','0002_loanrepayment_loanschedule','2026-04-11 17:03:49.746391'),(60,'CustomReports','0001_initial','2026-04-11 17:20:40.652551'),(61,'MembersApp','0002_master_defer_accr_int_application','2026-04-17 22:59:26.261506'),(62,'MembersApp','0003_master_loan_int_rate_master_savings_int_rate','2026-04-18 01:27:59.356393'),(63,'MembersApp','0004_master_tot_sav_int_deferred','2026-04-18 15:42:02.436646'),(64,'MembersApp','0005_rename_savings_int_rate_master_sav_int_rate','2026-04-18 16:24:29.574786'),(65,'MembersApp','0006_rename_defer_accr_int_application_master_sav_defer_int_appl','2026-04-18 16:26:30.822508'),(66,'MembersApp','0007_master_is_deleted_date_master_is_deleted_user_and_more','2026-04-18 16:47:23.683137'),(67,'MembersApp','0008_master_last_sav_int_accrual_date_and_more','2026-04-18 23:40:09.056064'),(68,'SysSetup','0006_systemsettings_last_interest_accrual_date','2026-04-19 02:32:07.900216'),(69,'MembersApp','0009_master_sav_int_accrued','2026-04-19 02:34:01.642386'),(70,'SysSetup','0007_systemsettings_loan_interest_rate','2026-04-19 04:14:08.219341'),(71,'LoanApp','0003_loan_interest_overdue_and_more','2026-04-19 15:59:37.555687'),(72,'MembersApp','0010_alter_master_loan_int_rate','2026-04-19 15:59:40.288165'),(73,'CoreApp','0001_initial','2026-04-19 18:35:21.690058'),(74,'CoreApp','0002_databasebackup','2026-04-19 20:02:15.691279'),(75,'MembersApp','0011_master_ghana_card_no','2026-04-19 23:23:37.557311'),(76,'MembersApp','0012_master_id_card_back_master_id_card_front_and_more','2026-04-20 00:08:27.346387'),(77,'MembersApp','0013_master_delete_history_master_delete_users_and_more','2026-04-20 15:20:09.180378'),(78,'MembersApp','0014_master_last_deleted_date','2026-04-20 16:29:02.255248'),(79,'LoginApp','0001_initial','2026-04-20 17:35:48.276645'),(80,'LoanApp','0004_loantransaction','2026-04-21 17:54:52.042532'),(81,'LoanApp','0005_alter_loan_status','2026-04-30 03:52:29.040293'),(82,'LoanApp','0006_loan_expiry_date','2026-04-30 04:07:05.811904'),(83,'LoanApp','0007_remove_loan_new_ded_calc_remove_loan_new_int_calc','2026-04-30 05:05:51.639484'),(84,'MembersApp','0015_alter_master_role','2026-05-01 22:07:06.190909'),(85,'SysSetup','0008_systemsettings_min_savings_balance_days','2026-05-03 02:16:03.852365'),(86,'MembersApp','0016_sav_int_table','2026-05-03 03:21:44.302628'),(87,'SysSetup','0009_systemsettings_last_savings_min_proc_date','2026-05-03 03:29:45.500389'),(88,'MembersApp','0017_master_sav_min_bal','2026-05-03 03:50:47.689653'),(89,'MembersApp','0018_master_sav_min_bal_days','2026-05-03 03:58:38.863875'),(90,'SysSetup','0010_systemsettings_first_quarter_end_and_more','2026-05-03 19:17:54.061062'),(91,'SysSetup','0011_remove_systemsettings_first_quarter_end_and_more','2026-05-03 19:19:21.177923'),(92,'services','0001_initial','2026-05-04 12:43:50.355146'),(93,'MembersApp','0019_master_enrollment_fees','2026-05-04 18:42:52.202855'),(94,'services','0002_alter_statetrans_amount','2026-05-04 18:42:52.507087'),(95,'services','0003_remove_stateupdate_ledger_id_remove_stateupdate_loan_and_more','2026-05-04 19:51:56.609937'),(96,'services','0004_remove_stateupdate_state_type','2026-05-04 19:53:15.141421'),(97,'services','0005_stateupdate_trans_amount_alter_stateupdate_amount','2026-05-04 19:55:31.969986'),(98,'services','0006_stateupdate_state_update_date','2026-05-04 20:24:55.057312'),(99,'services','0007_statetrans_state_date','2026-05-06 14:06:02.394823'),(100,'services','0008_stateupdate_new_enrollment_fees_and_more','2026-05-06 14:11:53.262302'),(101,'BackupRestore','0001_initial','2026-05-07 20:22:46.562251'),(102,'BackupRestore','0002_restorejob','2026-05-10 17:21:30.626532');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('031d519cf4ccv23pmwji948v9upk4qaw','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDU1t:6izd8Ou1SKFcULBBpQHsTMyQdyWdK8YfTcWOWDasasM','2026-04-16 22:13:41.318639'),('0gsorgj9ekd74ws7kvi5dy30dgbu9ydo','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFMn0:QCI2LOB8QDQMQuxYsijbuJs_lrEf-lMGgAsz6OqJZlY','2026-04-22 02:54:06.888896'),('0sy3512bitmnvxp0fn66b6cpzvqig9jj','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJeO6:IRIA1z-SGENORJZryj5TIsGU2wPN81E9UMKW7DcwLuQ','2026-05-03 22:30:06.720396'),('0t4u0i308m1ced524djgy4o49am53mca','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHucZ:arcSLbponkpnm6jV-SESlqYAgDUWzNsCScal7LIeGI8','2026-04-29 03:25:51.294184'),('0u3y7iqb13x33alt240an6vl3155oh3y','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFR35:nEw6Ib0-rMGWaHLzGLUwv3MQxwvIMQtubN7lT-DMDAA','2026-04-22 07:26:59.117593'),('0yojw17wnyj6rtz649qrlupajtfi26o3','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKbo4:iEAEz9_G2MZUHEdt1EqcIHuO8ogAKr9LY_m5AP0PT38','2026-05-06 13:56:52.337107'),('14hlajc7a0oqi8dl7op7unwg9o4osekp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFR77:2m2V33r5ka-XLkI2QQxRBky8zTIB__DcvCasU8Caaak','2026-04-22 07:31:09.371648'),('19f8v5yphwps3y2y59gqeoqubhhgq2yc','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFZBy:3wFQI1RK-9ORjs46C3SiHqZkPJ-n8j54nH-RN92FXHA','2026-04-22 16:08:42.072565'),('1lvynu1zk78pjv6x7vepcwqpoqf9am1z','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFKBR:Ui7PB2HgZwv1EMq-Jf9sq9d3_6zydX_TVjimcQr8a_8','2026-04-22 00:07:09.069954'),('2bvbre83yshmrd7p4zt5yj758eamzxco','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMeWO:SzEBlUKrOcfJSHSlRKs7rEU1KB4cm9mJLI0sqCmhq6U','2026-05-12 06:15:04.908940'),('306howvar2eng1x1dz25qq437af9g91j','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wECGY:oTcCE7lPwlp8gsiOEcYg2hk_ieau23CehCGph-n-kDk','2026-04-18 21:27:46.634073'),('33eppqaa75clzh14fe8026bg058u9l0g','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKeTD:u5teS87LScaxmEzqJScWrUqO09Cvi67MqFLQXQ7ldnM','2026-05-06 16:47:31.701781'),('3cp1n5z3fnv0furmuf2czkov2d07kud3','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wECfe:BoCIcRyFcaBVjUpOhrudTmsQuYuU_aDzeocQkMtJQa0','2026-04-18 21:53:42.026505'),('3ov98js2logtkupv72xui4cougpd7mb7','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqiK:t0vuze1OnnKILRmpZyMIoeb6drrnwUMhAwbTanuaNC0','2026-04-17 22:27:00.213848'),('3yfcv6tnentb3efqyc6y8qrpuj0fvkcg','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5C3:DEa4BqqJ7pH8PjQQVWX1JFo7fa8tfRzx7y4iQHbG-jk','2026-04-15 19:42:31.028664'),('4kdyvtkoknpqj74tslgqz291zey68rku','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEhPt:Mm9Rbf_HdZw9VfrtwpgrgqrQAXAg5UjUhSLI5PIYDKA','2026-04-20 06:43:29.347534'),('4kjpfsakgn7hk8zn8ryslewlfq2o8z25','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJe5N:3Kc2oAK1F7W4BpN8_Beet9G_S2xgkBajx2K1HPjWK5s','2026-05-03 22:10:45.734162'),('4lbl4enxtivjycby3wxp9rytsmoy9d7q','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKhLF:_L7y9YjTI41P1ZT11lZMBHpBo0qOU2XlYjqdqFlRVAY','2026-05-06 19:51:29.206344'),('4ls00c7zeqzigva6n02qp7u4yu7lzfc7','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEXwp:zJURs_Ydbxvq6AEwrFoBJizzrienS-_Q03wRgUR9-k0','2026-04-19 20:36:51.033059'),('4p0v9fmi3jm9uxk2ibcxxmfjz6c7zuga','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIAyZ:VwSoEb2j9FVW-2rB271Y4mYzE3aqtVQeo0k-b_s_q4Y','2026-04-29 20:53:39.549880'),('4pbl4j7m8vg3ex3zha8igdy4t6ajit6z','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wI9f5:qw9HJY8-NQbfCxOmHzB_U0-mOBJOJmwYHzeoiwDNErM','2026-04-29 19:29:27.520527'),('4pepe12j3se2ya2hpf9179p3i4yq033x','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wErQm:uYUe15dcN-BW1IU7M85pp3nrSkObqllhosKjs4crLK0','2026-04-20 17:25:04.658313'),('538rpxdk365azjhj9a9miyljkq648n73','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEAIE:SAyc5yYXYAhI2hu5GEL5wSZu7SPwQo1BSz9D7FHn8a4','2026-04-18 19:21:22.502653'),('5b0ga41hymc0beeyq79fbf800rb7q0ou','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFMNQ:6m8WRQfkQQ8r2OWOaOWXSDOAic1SsmB8isbDXyvCA7Q','2026-04-22 02:27:40.113528'),('5bo4p6rjmwlisarybmshutck0tfc3aou','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJszl:NeB0aVLv_6jtV8Rp_R-CHyxGA1Y8qPoKjUVBniw4aOQ','2026-05-04 14:05:57.735541'),('5ut5ze10lwpsr355cx2b6t06l5hr7lrn','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEj7E:v86qbRq-6R2k_DII-OleBnlzFh4vCmEZJjaErlw38WI','2026-04-20 08:32:20.798911'),('5wqkcevd9l24mr9mu7f5szzoldy66tf7','.eJxVjrsOwiAUht-FVSXngPQAo7ubmzHNgVJbL60pOBnf3TZx0PX__ttL1PwsXf3Maar7RniBYv2rBY7XNCygufBwHmUchzL1QS4W-aVZ7scm3XZf719Bx7lb0miJEEk3VeQArU7aKpvaGNQWK0dM0RlMitAqdq2LYJgtoiFlSVs3lwYusasfYy7z0yz8UaAWpz-99Pc0jylQ1QbMBtQBrTfktyDBATlcAXgA8f4A88FMYQ:1wJFXZ:5nXjFPGDEaD7oYSpwXlu-UtN-8tGBW6bCD9Hr8NtJWw','2026-05-02 19:58:13.906319'),('6cdfpemyu005qlnh8n33ex2fl2v754zu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFOB4:oPAkgPU8G0gWAi_SYbcJvlDlMZoJPIu31elly5Y6Xgw','2026-04-22 04:23:02.813172'),('6f0i22blrx8ijjyzjm30383f1ut4ok2n','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD7aN:m6M_D5xo5O7DwXRvWXQ9EVar18Dn0r_FZ9xuMakkwi0','2026-04-15 22:15:47.120839'),('6i8gyiz9x8x4kn2k0twr1fqklf8vvi10','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJdQM:Dn-gEc61ZcqJEkRVOPF2434Y1Ii5LazdevgtcYHs6KM','2026-05-03 21:28:22.771653'),('6k6v0lavoebld54d6163paai0nmm6qcj','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEDzY:wddOVRHFLe2AlXD5NGSalbBk-PKJPDBbdl0rIK9ZmUk','2026-04-18 23:18:20.469640'),('6plc2mn3qwm7c64cr32ray9oktv0mndz','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJi0u:6jWcjZ-Ggpc7lUW6hBHrR3ROI64qcEbjwpJgWxsAZSs','2026-05-04 02:22:24.907450'),('6u6n6263anfrcwpfy4htukn7wcjkdjvo','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD7OZ:DJWKZ2oAtsaeiyyMTAyV59pujnOdFk3mUaIrhiv1kSc','2026-04-15 22:03:35.443943'),('6w3dgdrmjzhjqs8yljrunkzx1p014mj1','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMfi4:GC6YtuCQ6qL158R7v64yXzLl8WkMyz30094bnTM5TL8','2026-05-12 07:31:12.928235'),('6y4u3hd1s7auyl8xzie59i681f1v6ru8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKciC:LUvl7GWsqDr_Eoifa9AavyDoSwgDq65qAH0FL4YYBog','2026-05-06 14:54:52.103617'),('72kt62kc37t414vmrz157b3dcdcovsv2','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wErm4:950T4bHRTGVkngCEPtGwTGkrWqgliEMdTOC5vzp6dTQ','2026-04-20 17:47:04.131804'),('75owzg62gud6owwozhwzeuvmb6ae9d2y','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEYDN:YvfQ3U6TSFluCoVRh4_0HshXOvO8kmZ8jXuUMcqcYA8','2026-04-19 20:53:57.985936'),('76zis4kvxm2hf5uxc35tfrhp2992bsb2','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5rc:u1wc16thaucN6OX36DX4Q5WwIhKYXh9kzBH4R4E-OBI','2026-04-15 20:25:28.852575'),('7f6yjllho3qsm2ahmcqprg1lx1bzr2sj','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJQqK:vVFnUBCeJYsRN4bm3RPTCFPpImbUQrSnQ_WiitYk2u4','2026-05-03 08:02:20.898350'),('7iw1r26kxsmke89nu0fuodk9sjillux0','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKi8w:ur1RqpdNJcgKh-m5rPy55vn5xUGV3X2Bb6mQd-kTdd8','2026-05-06 20:42:50.139898'),('7t8t9kr4i3mftyryzp8beprbvldomfh9','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIITa:ugvqValRpcB-HjJ0VMU4E-RnqHVofap0SW3ZNVRyQH8','2026-04-30 04:54:10.855722'),('84lcxtqfv03w4e58ax49dt7hrvbvq0lb','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEyW3:3fRvGjh8hwkwKrPLXrMFIQNNkjCftRiyEEe9x1IeLSk','2026-04-21 00:58:59.976756'),('86ypdi9ahf9hppgwia1nca0qtttsqayy','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDWn7:0pMrszfh_MeSd-dNoNVio_iGwmQPvmqPYAe46FCmzLI','2026-04-17 01:10:37.493286'),('87546gp21jffbtrztxgvnkzs17pc27ax','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKcwc:9Qi3mAIDUJRbkNPeThcC9Xaxvbd94lbSaIUFeSbwYkY','2026-05-06 15:09:46.545689'),('8gpkceqnd3xxkpqto1tlrb3qp2vommje','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJjIg:6BowDo0bf4nS6kE3k_TcIqF6VpgieoBfxiM3UQ2ufjQ','2026-05-04 03:44:50.146517'),('8nqk6byhnrr06ixllrs9euw3c9osv9ov','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5ts:QJuityzrIDJovQZSM7bDJcLYMbZNOWGKRO0hoOmCCNk','2026-04-15 20:27:48.510556'),('95401nf4qqpbob39t6lwy4x0f7m96e0q','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wI95T:Kj9BwITate9Z7U-ZqEhGR-CJ7w9963suKMo7GYmxHWk','2026-04-29 18:52:39.980039'),('9iw4xw19pr5slwgg4t5ikt84vibyp0bn','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKwJ9:6-nYy6EaONTZ2PXBnChtpPfkx6NE-LLpgptyRjmp9Uo','2026-05-07 11:50:19.703783'),('9ncjcoeolyltow9bryzbapgepepdktry','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wE89H:XqgV7Gm4IPNdtpQ7cMjkpr6HX1lgXLD3PU6ywgS0MRk','2026-04-18 17:03:59.586792'),('9xfckjdzybv9hc97rz95cepse955l5jp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD4vO:sIdpSJQyJU7jNL8XnC_YPKHn59nu1cxYnjOzZ3uDg-8','2026-04-15 19:25:18.287970'),('a17w97lx9hxkvuz9aq6lxxpnwkws7gs4','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wErSz:0YElTK1tZjZlxhSShPyEXRbEeXZT_ay7DK7k9q_55x8','2026-04-20 17:27:21.859393'),('b0aayoyr0afydfiw7t8fnagqznea3yst','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMUGe:BN4cSUuDQbCNyWt_P_cZaTrSG954UohQCFKeer0Xub0','2026-05-11 19:18:08.462256'),('c6dbehnvtv6r0aunshz7rb9ttxjn12nu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqeE:5du8-6UZ4t09T_P1DVK1ieGteRrchuuvmYrqlO6-s7Q','2026-04-17 22:22:46.138738'),('cxmnghv37wgjc9boxjb3t4udjfyyl4pu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wF55d:81h9mYShWt1zjBbtqW-yhGGzlX64CmuoxjKaOwlYQGc','2026-04-21 08:00:09.634846'),('d539kppzh9wvojq73cdp2bpoa2xabzvt','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMdpj:gaE6nC8krSyQNyKTxlannswXgRagIhQdTb4TE8U6J6M','2026-05-12 05:30:59.692549'),('dqgywxgi0brpyzde7nco1fnomj0og3yo','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJdx9:lSrXAuJuEODkdpym7EnysupporPL2ybmKWjRk1VoKZE','2026-05-03 22:02:15.085665'),('drdrdvedgpapxkp6rz9xebwim7v7p1pa','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDrso:beDXJZds2TJqYdt7lyWekj1WZTvifDPH4iFxiilyDGk','2026-04-17 23:41:54.773226'),('dsn5izjos7ve5lixlljd7pzo5hcvogad','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wErV3:U0egTyYy3xWuQRd-XLFrTOpFoH4W7gxUocBkpoe_cKg','2026-04-20 17:29:29.604434'),('ducrpj8b33vu313eksadh746fooj6zvp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJFE6:tS3306WXib4pxuxkR8cw2yVG49YY8ZznC83qJFKCHFc','2026-05-02 19:38:06.678001'),('eo0cglj4jxrl2738f6f9tgli1py2eggq','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDW4A:2mj8voeFrqotgGAr8WgDkP5Xifi9twktmAph0E-7gbM','2026-04-17 00:24:10.483048'),('evw2ddjj2u2ttusmzwzvr4jw0fhnku46','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wErq0:IJf0sEnoiWyzBqMXbLqwVOvAZ577SZTOGjh38faC4ZY','2026-04-20 17:51:08.419898'),('ewjd1zsvx5y9sn97oqroeduf8ngkrvx7','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJccn:qvzEq5gNFA449JXBFrkR5_yEmnsOlD_ORvlfqhFBXf4','2026-05-03 20:37:09.417261'),('f0u00n0kgxf6e2xsuv8jyhwv80ela5gx','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5HF:a6Z3e1Iy0574dP9-cKR1gI9qu2aIRWOFR7VkIet2xx4','2026-04-15 19:47:53.076644'),('f3ne9uss4fjyhw0m611whqhvdo9331v8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIXrw:0el5VY3nZ781VfCHGzZ0MtF1K3VnzcOA7mFU5VpcW4g','2026-04-30 21:20:20.497199'),('f81z5cfexgf73inh4dvcf2t9u5zhf1vj','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIYw0:ZNStJ43xhzTuf74vFR-nPZv0nnOXZY8BBWhteaV9j5g','2026-04-30 22:28:36.075248'),('f8tdgx0rwmpulc5hknr1nzjoyesx3yi4','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHu6U:9c4EtpbKIElZPcaEkvxK51rDlThlEw97-hgx8qiDMEY','2026-04-29 02:52:42.492484'),('fb2ctklcx8qlxogxb54xx1no415l7k1c','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDrF9:LU5TzeCLgyC_UA-OtJMM4pBxnhkCBDwJkSw1_nKMRAU','2026-04-17 23:00:55.134855'),('fi4kr8op45vuxi7g9qqh643lr1lugnko','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wL5RM:fjsaGCRzPH2pyZQlje3YxzJ01IJM5HdeGLhhDN5izZE','2026-05-07 21:35:24.970498'),('fperg3ponpb0aj83cz51scmbuh5hndzp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIvuD:jb--QvhlQIAhu1P16q4F6a3XS95crk2TGareKXxHkLg','2026-05-01 23:00:17.763018'),('fsvlasaq7mogq7dut3lyizdnn6fxvp87','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMd82:DG60Fwae7w1bxu6H3CIEMVtmL2FCJCwm5kIa-spszec','2026-05-12 04:45:50.840436'),('g13e70e2nikbwipwf27i21vp2xyejrf7','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJgrS:EfvvG1S85zFqXegUcGw3h89XLMuLNU4ewsLkqAtQTFQ','2026-05-04 01:08:34.259192'),('g43p30afcn7b835ouop2vwge8enna3yi','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEjC3:P0hRdHkB0o43hl761mn0D4ET84wak8B0WF_a6sj5mxY','2026-04-20 08:37:19.101441'),('g61fj6hsbhktt9bzxplo2pnpan98ad71','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIKUN:pOTezwmGeCBFWlpSlU_tybIVqAg82n6tUNoUyLTpXEc','2026-04-30 07:03:07.553226'),('g9dpniga2jmtdiw5dpzqxjja35pxf3rd','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqXU:0MrI2Hg8TuoJpbh_pqr5bFmuOfquhxUa1nrit-W2HBM','2026-04-17 22:15:48.006962'),('g9j2ecvc1zvp4pl9pkukd2vm0i8xi5rm','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEh5U:TFt_jsyTvKsIXinYRBZqb-j4sQePs8Zj5hRbqPebFqI','2026-04-20 06:22:24.983451'),('gagjkbn7qxz9jdt8o38i0unwgsqm1ems','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIDIK:Mig2szBFDJwTD7KMemw_hgmY6F4B6f5sWPZUOfGEQfM','2026-04-29 23:22:12.439890'),('gjknp7buwikco7x4jui159ht34vrpyo0','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFRIJ:z7JGNoUOM_n6l46Y76AxRywifWtCF5Ef4Fm-IYEqPu0','2026-04-22 07:42:43.410567'),('gn8l0etsv5oegcoayq7r91394w1sh7yr','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5Dn:OQDZL7McfFr4heK_Y6lGGapUHbSP9tlLaSoPlBae6Do','2026-04-15 19:44:19.255297'),('h0ptdyei54a8yzm6jvlc6ntoynokcso1','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKi4o:OZWutjUS26OsF5dZb1yu5du7TCOF2FMa9ALht_7HIZk','2026-05-06 20:38:34.079122'),('hawrtdwye4xxzippf4vc6pzex079hic3','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMQBt:Md1Q30HgVgW0ylARQjMiUBmqQ4qfkYkxW9oDuk4dR-Q','2026-05-11 14:56:57.550001'),('hbl0k4h309bglsuagswq4y6qcecnssl8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDWkH:EoqBOLjS6iylOY3n5taGA8v8eDpcTFcpk1t2loN9AgQ','2026-04-17 01:07:41.084623'),('herur771kvph1emb6yss5y0785pn6qqu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEbgx:b_2orcgtGW_draWJ6TNGa3I3PRFGsjUF4oFCaPLz2QU','2026-04-20 00:36:43.147408'),('hos3oe46speaysxzmn3i3347i19idm1z','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5Ho:j9ob4Zj2I9CnCTRYbktqoZiSNjf2PX-NtxQi1jaaYqI','2026-04-15 19:48:28.380170'),('hr2da1jxszm2edu36a6o4dj9suo7evy8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHufL:9ItNSEaFEaRJiyLdhlz3Z9yRoE8vy5NYXt7PcFeic68','2026-04-29 03:28:43.771056'),('hsrdbe8cxdolzy4fag8xem6cgkyljlao','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFFuD:eSNWJ4wwqD8jfZ7rsXmfLEQvzNXYcmpJrk1oUEFPllk','2026-04-21 19:33:05.091370'),('hwtn7e7d7rko41ickdj4o2jj7hzxyekm','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wE9qz:IUvMFJAuwsRS9ZhhZDLEmu6JqwMfwciPywEOKyejxcE','2026-04-18 18:53:13.668474'),('hx3a8nmzbqtix846bqgk7s8orgtwhw1k','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJaun:o8FTpwOoe823nX6cSd9K7tZKzOQRZeZpw7bYdDv_m6c','2026-05-03 18:47:37.868710'),('ic33n6cg2twfoo4ugbp7cyqcord8ljvs','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKzZt:mWwSPV1tqsP9hrgD3LNObsDhILzpKIgK7Dt2eiOqp1w','2026-05-07 15:19:49.222663'),('ig6la4xkqyjdftaga6j3g44aerektzav','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKd2M:R-vMKqyecSFpcK3svbAxb41kas9aTK9VgomvEIyojFI','2026-05-06 15:15:42.012702'),('illnjbw5sxn3dy5p25c793exfx5bodxi','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDSvo:lbsp2o3dRcjvc35-9vwzadIkEi1M5fVSWQMp7NUok_c','2026-04-16 21:03:20.198454'),('iq3qi7rtpfhsziexzjts7ralyzuvfcwt','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEFk4:9IPr-G_hX7v1y9LhMzwZ-CRtIAAki-YFqdd-_mge8AM','2026-04-19 01:10:28.882260'),('ivjiit8ekixbh7iyo6b6s5xr5plg16df','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqNF:j-KkuRZ_Nz2zhIoypfcbOWZtt5x4FE0sH_UXFLYclG4','2026-04-17 22:05:13.251675'),('iznmnmqqrdqemfq359vyphkjwi9co95p','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIK0Q:AQolXjlwebwnioUY2zLxvVPPEiHrsf8C4049HfERs2A','2026-04-30 06:32:10.898648'),('jhupqzj40y7f23e1llwrw9h49h4fztv9','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFNqT:_HvBVzWIuv_XU6jROWUKI32m60-lxSCeT4sJ5squSpY','2026-04-22 04:01:45.947171'),('jl7qt2iazju09wrjh8ommjfxicp1ngis','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKaWh:sem-DNBlVHxSLQYKDSMo8Isl0YeVo-ygaX-eL5-eGAw','2026-05-06 12:34:51.868738'),('jpbyfma0r4t50u3r2pcxzjhc5xjotgm7','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5nJ:atFV21gfzfbeJX2IibZjZZYOjMfHoOqtBgCaDUB1xtY','2026-04-15 20:21:01.631611'),('jpxev8dwrod8vzoyr1ywjynoyyjtlegz','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEhkR:rbVIy2FdItQmatZN0buJRL2drp8wE83IMrs4RO_zxps','2026-04-20 07:04:43.799859'),('jutcffupwf9y5a5vinctu3rmzb0d2cbo','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIWfC:DCQbYCikvqZb0ewMmp8NsVYQdJapOabLep8GjByTJI0','2026-04-30 20:03:06.533472'),('ktf5melifduani7alvcurpm3picoow4p','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wF4vD:_T3bx-1eWQhFNATnf2bE8Pp9E_zwSTMwA-PAg8s3ngI','2026-04-21 07:49:23.218831'),('kx8c5aol95je9y4gtgv4578h94hakxbo','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFZtV:FAlcKRSAbDgwH4eIhVD2raYhB9jahewNZwqFcwzf4xQ','2026-04-22 16:53:41.590425'),('l2xcnzvg36nhpge4skofoer7siej5n9a','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKiKb:p3CaiLXs_fMMZv49IMZFrSFd8DlLiArdp_ttYi-C9LU','2026-05-06 20:54:53.056424'),('l8rqnoqxih1u0eb8dwgp6qpw0v9c6hui','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHtwv:iXt8rBirntjwF7ZqjU0pmCjQ6FBpvNz1HMF-INriymo','2026-04-29 02:42:49.413836'),('ld8b9s048j463cs6re9bfnmj9u1cdy67','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqS5:TOo9A8_UW0R4uxygBel9JC2NimzXIaWrLqtBtxx1sjE','2026-04-17 22:10:13.283301'),('ldpkyajhwcuok0h0c2mz75ll1m2forwu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMOks:7emUAYq-_woPyJuTzMoyR8yeYrx7hoJPweuFZMjsHJE','2026-05-11 13:24:58.188789'),('ltkcqszelhsxba07ba379u2x5e57ggti','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMUG1:-3FOcSyY1ILu1sQ8jdHmAM2eDcWp1LvYWAFCbO4bl58','2026-05-11 19:17:29.644596'),('lvc09u9z2p1gimhdnmdils33iietcajb','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJcqW:win84lvp16mvj4FsbLb0DYqHbW2ZoCeRWAsCsp2G4ys','2026-05-03 20:51:20.464495'),('m1vgar9uxkk96f7hjd32j5iskix5gwey','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHr50:42Vpu0Q6U5i6_FBGMDsYsNK85OW0un93YxymuMfxa7M','2026-04-28 23:38:58.484195'),('m2y1q5ag8v0dpnh1a6dhgyboyi5nyvv7','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEjQD:moo1sFmJ7vmqUvVGqxZxtXwTFpGC-lvIC9NuZXnxLGE','2026-04-20 08:51:57.188104'),('m3azpzqeq5nw6p9436mbz7tar84ef7i2','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEbOL:E_w3slSG6WCXRnObfSFH0FCFt1JH8FczmzxNI_TuPHM','2026-04-20 00:17:29.190670'),('m3j1ypkvwdn5d9109nzv37y74ixctyhi','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wST5i:5M5Dme34RWVfE9pE3m05Njmd_CgX7QcrmRAqQ39LoF4','2026-05-28 06:15:34.322748'),('m3nhy9cuzoggnewe8kn9051f57bgeemi','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJbAv:x0WhpU2zmNgpvo0mpK4NcMYUVlcz4lg3WK73hD68VFU','2026-05-03 19:04:17.776884'),('m3wbfeemb2h7qd0veqsprlwhwvz487l8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEIxt:9KaZQTYr6TH1A5uesgdSn8tMcG4AIc0zDOX1U2waYgk','2026-04-19 04:36:57.532225'),('mdbiug3rf9r9vb59ulgbww98h9kssj0u','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFK0h:ELq-3y4ba--1EM4kzg74ZB_KEH0DwVckPZZIXM_SHkM','2026-04-21 23:56:03.758952'),('meg9x84anc3sad2d4l0jgkzemkx26j18','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqlD:RjKym06E1OCyj1hJmWr--RhLuogpU9JNiLdGqTPKhdk','2026-04-17 22:29:59.181916'),('ml0lyu6eajvh8h8z3fif2hyny56tzyoc','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFIB4:J7iJ76uCiGLZc9xgZOiGoe0JsZ8TFiDd1BuRjQQ7yG4','2026-04-21 21:58:38.272829'),('mn9y29qi5lbvceug43ksdn3dvg21brjg','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHpdc:f90P2ZZFgyJ_tz6aAh4x5VM3kAqchN7gGNrpy3h2Ia8','2026-04-28 22:06:36.448916'),('mnez8tfbwf7tvf8nwk4iyzak7879ffrp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wECCr:597tStvsni5vN0yI533JEK_P0eZgqSBb-36v58Tiu-Y','2026-04-18 21:23:57.541533'),('mtj466y0d6ps4nuv0disaf7mqnhes3tt','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJdl9:yTu9BMI-9pxhaT9-AhJ4LUrSp_i31p0qJGzwnE58Qu8','2026-05-03 21:49:51.395714'),('mv2k24pwwv0fsy23igfes85evjqgze7n','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD53E:h9QpyxW_KawgSi9dHst1t32aCOEgdrqAhrRTHB5IJDU','2026-04-15 19:33:24.753170'),('mv3euer4b3jp0723bjlz0gj6iy2kq3ts','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFG7r:7HBQs0a94m0g1fW7nKsBqH0ZWltbZ81AxhsK9uSMvqI','2026-04-21 19:47:11.192152'),('n5s9cmc5h7l863xixd3a60zzm8burllm','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFJsw:lW9rjEn3_MT82ByLxiiGhMNTmCr7o5ie4wE7E2P1p5M','2026-04-21 23:48:02.952862'),('nd4so29ulk1fwlyun0tgoi8y81t64u0r','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEs2w:EOZbvCoay7YQIKzMyUJVnopax1IPRc37fR0XkMPn5rk','2026-04-20 18:04:30.942476'),('ngv8fgbu0gbwysorom888d7ud5lin9k1','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMd4w:ik3q6w6X9XKzuNSpTVInkPCmBcTpl4fn_K2fey48o_Y','2026-05-12 04:42:38.995693'),('nhnn13i07nzl5txoqucvwls99sh75hp9','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDs4m:0PluJsEIHIAInAEdAzJ2FhFfYwaZ0qEof0M9KC3YyiY','2026-04-17 23:54:16.295329'),('npg3ait5o3nl781vda6e2hd418u0d7ib','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJhPR:b7fLyqJOUjpopwYieSGJagQnOzeixsuzwTY7aJE2o0w','2026-05-04 01:43:41.229547'),('npv0b0s3kil96kjqw9egv41iy099pv1i','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wLCuz:dKfqBVrEemseRw5DuNL5oueF-0V-OR1ejLLd8ASbei4','2026-05-08 05:34:29.686130'),('nv9s4r18az1022ytse8nqlsdkvr3swir','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEhdz:9zTChyvoJgfY4Rij6Wqv6Gd5zoX9cfRc6POreIvLZYk','2026-04-20 06:58:03.652042'),('o54dmropgs5unshmt7fwws83ptu9alvu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEu4X:MucLLxOajxeu146w7xrLmEG46bnQBj97d4aR2aIJ2fI','2026-04-20 20:14:17.420882'),('o6qq19cie930304jjlvuq473tkg3lwlp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFHLB:kUT4Xh3Jmqd_CQkuzLkmy_Sp1va-1j5ljz-mtl99nD4','2026-04-21 21:05:01.600851'),('oaew4k4ybonkjk9r5i91p28j2owgpfie','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFHb8:5msCH2r0ViiVBzNGSKg9MLgxFj1EpxSzfvybCh3jqiE','2026-04-21 21:21:30.491623'),('oevsp9207kritpglofgwl5ulzwf47jjy','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKdBV:i_8j1S6sknv5FbJe2VQPK5mK6CWEeHE75GOq6jX1Ffg','2026-05-06 15:25:09.867970'),('okxmhzkjtjtb7ud74f7evuohwo3go0fv','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHudV:V8M6BGlv9L95j-kolWyu6dZvXWH-sHQN85gsHVAoK4A','2026-04-29 03:26:49.732454'),('oofcwi8zrnh8bkzj53ctn9fki5jigvl5','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFQoa:_SbQMeXKk7TzkIaG9ZRQEAfz5Ig8kOjZZ219hrGD_6I','2026-04-22 07:12:00.897524'),('optgqkhxzrx9d0f8rs9ts7qo9d5b35fs','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIIcw:fXP_OJa54AhIH_qNmdH4SK8J1wHUe2pdBdvLr7xoloI','2026-04-30 05:03:50.196953'),('os25x3fnsd9xt2g90axvd6izarbpaeyg','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKxmL:DXeqtyDorNxXZGYMJ-QuytuCoDC6pS9OXceczqVpfn4','2026-05-07 13:24:33.683326'),('oxkjxvzfycs4thn2yuco0x8i5exklcur','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD9GM:k6Bcj2-IfSpyKwiwo20xOCKIKItkMpB-rL2TjTaGmeQ','2026-04-16 00:03:14.987976'),('oywt0kufcmuzmx74kdn5br7qrpedgkbq','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJop9:7rHtP-VFWbnVxPjr0QXMPdVuqo2RlCqkLXBQu-rqELg','2026-05-04 09:38:43.876795'),('oyymbqer85c3wmkgpxa9hv3fdp2xgubc','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDv47:ZrPM6whQxygDEJSjK6nm3pDaoMoctwz7Lsby9sW5q2g','2026-04-18 03:05:47.626781'),('p25rgaot9o39u3s1cs4sa21zmujm7mcu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEzrI:2b015cMT1s03I6q5BURf3e4yk1bSeBINzIP_LIXTmCs','2026-04-21 02:25:00.170830'),('p5etewj8mrtti4orv1hw7j0x6850gjl8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEim5:ZFVBGXTPIFRriKO6logH9US7phFy60XbOIP4HGSh1CY','2026-04-20 08:10:29.227629'),('p6z9pz43m8uy43jw3ugf7lf9srl7eh16','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIBGk:Zs6h6NmKcwd7JhbwvS_cErrGInPjBpvCW5_zDyUMl1g','2026-04-29 21:12:26.953239'),('p817270g50uxka2jrco7yr58zy3bqt6n','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD5xE:lvrJvyNus03pvm2sTOkgVf6BsPLQNMaFrTPY_T4CcnI','2026-04-15 20:31:16.289698'),('pocng4m12w9cpubdn1fr5yaubdlgsmax','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEB9T:bYHD5KdISQvT_IQ7-JLsYYhp2DYNtiXWKgs-nTNut2w','2026-04-18 20:16:23.152066'),('px1biakqmo4t30kvsgsfm8k955yyzhc5','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHuav:Vl2KN3iI1Lw0jVLJEMTF58Met9KlPzxx3w39XnySxzY','2026-04-29 03:24:09.310276'),('pz785z3xhttgxwedfrqrqp8ls5tbmkfh','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wErlF:AWNGbzn66t4ECAu5xd5U35-i-OPSBbZsgj40sugFfkY','2026-04-20 17:46:13.302016'),('qbl5i7nnj6qy0r6rzax2wwala21t6kfc','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqIR:aY59crtO6xkLmN0-K17hXuJyQNpIEMXzeuQQ5cBJxrg','2026-04-17 22:00:15.184049'),('qn7y82tru72w6gds3h56ogdleicvt2zo','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD81i:ivjPFwEYuxeHjLKuP7trfybJC0jYAMXPSHoAqD6MhTA','2026-04-15 22:44:02.494721'),('r5bi24yvbphdr0uw9o0p3rpqfr6l1lym','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEhwC:mBRXMcIrCf39h0qkExdc9XFV9mIvP70nVRUZOzRXHpE','2026-04-20 07:16:52.218214'),('r9ive54wy3hi1tj60ei717oecm6g3yd8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFJay:9wT8QbReOTgCZ1tnaLxnsj1-NZ56rmRdDvLz5o3I_Lo','2026-04-21 23:29:28.078908'),('rayee5z02g4bfugfs6tnp7b6aphrlhdd','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wSSY1:WahagXg02Ae_VAzVQ_xKt7hL2BdFZosD2nQnj_0x8hw','2026-05-28 05:40:45.959902'),('rrxd1j0yii82b5pl2ld83l3n5sdmi2vu','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEXbs:-veZNqmebiHghb5swWJ29tC5Uq9_27X6HZeuSk0F9ek','2026-04-19 20:15:12.360084'),('rsg2z1uhbcw5hc90t26n8d9anpxrnugx','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFa11:RrznYI08RezAU0UDw26mWViKwgGBCZwlAJfU77-8m3Y','2026-04-22 17:01:27.845711'),('rvjuvdesef412f0xerunm3o7m0jor0qc','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wL5Ld:f4Xd0xflwfxuj4Alo7dho9E0k4x4zU2hq957Xu8fXLM','2026-05-07 21:29:29.756698'),('rxhjgwhftc29rpskfkmufpg4cdvp2sjv','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wD54F:-uV1mnsiMuB6QUpkWmlI9EzlcTWIKnqstSu45uH7y5M','2026-04-15 19:34:27.639767'),('s5j6sus72etsqnf8r2hmvme1txn5poy2','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEqIL:pxNhvxyfmToE1c8BnIUgVvG-9qn7cY-5qITG8CbpV5I','2026-04-20 16:12:17.813841'),('sa25q8ndstezs6qwv8f30qx9ui92dv5n','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wICgD:adlUa8yyOtuzREeKsZy3CAa9SrRQLlVzmwzn0x0FhV8','2026-04-29 22:42:49.599426'),('sb3njky5iei7yp08sb7qnsgkwa1xdimm','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqc9:Nl4JjBzsNt3j633gPfxMF9wfWcoFaGjRU1TPQlGwgUc','2026-04-17 22:20:37.376194'),('sbmml5afobl0otz96lw0iwc6o1t1iloe','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIWIv:tD05WimyipZJonY7hcSY-UMYLyoUf6J6d7e8vkqWCdI','2026-04-30 19:40:05.669487'),('skzn7z40aise1l6gqxs12mncnrn73z8o','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDWlD:w0wo0CdPK8xhfnFSwsUObkw9JcFPUGF_ty_DXyowlI4','2026-04-17 01:08:39.178228'),('snjp4v7flaniplh9ai8uoa5vnkr4bxcx','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFLO1:YT2rcXVKLrwRKWOgwDoGXJ4LQ-Pz39A1SrSlpIr6Ils','2026-04-22 01:24:13.722239'),('svs505pv28kxvjgwjshkpupa8jnfzmaz','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFNh3:WKYlB2MnUlnmHyJ0o9PhA8kcfl3pgb-RrXXurmJrwNk','2026-04-22 03:52:01.796341'),('sx9l2j4jy3num9shgsg6ctkqe8i6azgy','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEe1D:BmQRRfPxeBmV-qFrYFXC9JPJ81iSWH81heAgIkWch4g','2026-04-20 03:05:47.046467'),('syn813ehkyn6tcgncpv4z3ryo68rasbq','.eJxVTj1vwyAQ_S-sTdDdEfuAsXu2blVlHRjHTlI7CmSq-t8LUoZmeG94X3o_apBHmYdHTvdhGZVXqHb_tSDxktZmjGdZT5uO21ruS9Atop9u1sdtTNf3Z_ZlYJY8tzZaZkQ2Yx8lwGSSsWTTFAMdsHcsHF2HiRgtiZtchE7EInZMlo11dTRIifNw23KpT7PynwpNlZEatdsIlVrSVnBFr75eamX5TvULAfV76PZAH-g8Gm9IG0cHw28AHkD9_gHcOlFx:1wJFn1:s0tj7FTwgh_UmwToxQoSgkOQ6KcqXbKTcnng3JqXOSU','2026-05-02 20:14:11.685106'),('t4huwfphaguhg8bq731jq8lsj4pmsk02','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJcm0:8hy2Ih0PFVbwSVGvwAKT6ZXZQDbWLORwNiBvXNzzs80','2026-05-03 20:46:40.102771'),('tyrfrkymot0rp2sivlmm7rg6s44ky2p3','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDqhX:GINz53APeueTMEJHf1lEy_f4_LdHmcTqyT-2NM3WK9I','2026-04-17 22:26:11.138772'),('u1k3aq4fcka7dnjqmrdx08nh4sf7i6ui','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFLiu:YBsI1c5yiTYEq9G9I9L7knMem-2DXeeFxzzzOyrUtKw','2026-04-22 01:45:48.340180'),('u5d21kcohvvizajdjrxjmmvf5w99tnhp','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKiJr:K4OeZcHVUyOrqv_B_5t2mIgiDew1Wqt_qyJuJ4F7D44','2026-05-06 20:54:07.309102'),('upf70n99gi5l2k6lsqhoqvavbe3s04zy','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKhHO:eC8jn7mkaylIuWfAAzz5x1K_qv8z2Dt-oP-7V9Rzm7w','2026-05-06 19:47:30.117375'),('ur26ex4s1c8v282eypaiqcc5n7sn4crx','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJjCZ:9F7AOrn3Hg1KC6MayE6YvQqrpsJtbMJ9UYJChOmRQPc','2026-05-04 03:38:31.960237'),('uycufsgn3nurqttkrtndoezesl0auicq','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wHpNr:_pfCgYtrdDedZpeqL0IwBMI92reYYQpoJBFsGZmoyfI','2026-04-28 21:50:19.928573'),('v5hs9x47b9o3cz161g1z1vsuucbv83a8','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFMVr:IF51Epg6ZWnmACRSekacih59H8j8BTLD_T8EiCbrHTs','2026-04-22 02:36:23.356200'),('vzydzebk58mx6p4uag43ws2x00j35x8c','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJhbg:gKcaTl4dAIDiN9E44F5C7euXt_4bTXUXy-MDoVXjeFU','2026-05-04 01:56:20.112314'),('wiye5rfi666xfr9dyrl0tzre85kgzhhr','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wJhfD:R0LpYiKyPWdvovqkrvV6_qXOVdD0D8MZMIGhcZlXEz8','2026-05-04 01:59:59.270167'),('wow2s2sjlp5cmykn6gvepmvjnm9qpgd2','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIB6j:la9zACBxVrFJetCzgAp9lyLjnXuSbj-YxDwdpWIC7rs','2026-04-29 21:02:05.024721'),('wudwue8vuqb97v0b4rfh2v8bfeldcisz','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEXf3:d1EKgcEXLODDgqIPKPfmMvlMZUyODpDI4tAc9oyEwbU','2026-04-19 20:18:29.607163'),('wwtdk06p4cfdwuud5axicfm4ilmo8yx4','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFGWG:KmpG8mSAu-AFmcXP1NcxBbGTeiFQz7ucIKelYQ215Dk','2026-04-21 20:12:24.015619'),('xcuzcz9vfa3v964tl7fok70u2pdu27lg','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMfUq:Ut88JhLgMhK4FIQF8Y9sO4WeRf9zL5Ej-xaDWPKJgG0','2026-05-12 07:17:32.775819'),('xk8dd37e2mx5fekwwi01nmdt9r0vp3ns','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIJkL:9Jr50u8ra_sA0WGiVcEmR79bZh6jyS4AGhFHNA_JtPQ','2026-04-30 06:15:33.200260'),('xnyxudr8gi8mqaw8qvrye2uxgegmt5p0','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMfRd:BH4cMFVF4Y3HnZSDfRsNdAG9pIqwbhPWqbYQFpcH9dE','2026-05-12 07:14:13.912064'),('xu52zrim2dy5vd8pxwdmz4spfgrc0t5b','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEiSe:rJc_Y6CtmPnanewDJG08PJ2SwvS4UZKA8doRTErRnHM','2026-04-20 07:50:24.162798'),('yfzyebq9ohijx8cq64c9c1wrf2bydd96','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMdHe:tX9dLoVGnEiaTd4beDKN6zG-eu40vnyug83gwGC5KbY','2026-05-12 04:55:46.461673'),('yhvdwr78xuv3b8uxy7yt09kmuk472f1g','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKx4x:qntUDtEOXsL9y5yKXfB4tbY_qC2d_mZNhzWag8bU6yU','2026-05-07 12:39:43.021832'),('yrf6gnvt5y3kujxnada9693fmkggilhl','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wGQp7:vLxfhzr9C1eZ2TQkj3ae7eCBN786AzgUgNzGh-Jqw-o','2026-04-25 01:24:41.417380'),('ysgz6uavuotlenqqq2i64pnngjk7b9pd','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wKao1:Rdfy49X_xUzcQyCwbHMVwSarYWTc7eGQkCF9-ye6Duc','2026-05-06 12:52:45.268882'),('z374hyna2te0kabjrgzypu4497pau28u','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wEina:N0v8Ou8sQhMNWbgzjY0fJtbXL959TA9SEfc8nFN1_FU','2026-04-20 08:12:02.000852'),('z7i3in6963cbjpu0w7lo3i68sb8eu3og','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wMSwh:dxcyKjOdLtJL2cCJCJUnEKokYq4Q694SDd6BZwLJuSU','2026-05-11 17:53:27.110844'),('zk5fkt848c1rzf6xsuxb4m84a3aucigj','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wFZDN:KBPPZdXPGtbfwBgMoh347r8KFslhOfSmjvoa3dD8jlI','2026-04-22 16:10:09.670689'),('zp5sco9i2r8xbwzkijtyqtqsr9ddwf62','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wDWeD:9FA1LlziWpDJWiQzj1T9wHy_YOiBDYaEw1LXuKLas5E','2026-04-17 01:01:25.949201'),('zvnr6qtwlcgxwkiymmd2z2gpgo01g0ep','.eJxVjMsOwiAQRf-FtSEdkM7g0r3fQIaXVA0kpV0Z_92QdKHbe865b-F434rbe1rdEsVFgDj9bp7DM9UB4oPrvcnQ6rYuXg5FHrTLW4vpdT3cv4PCvYwaCBEAdZwD-ynrpElRysGrM8wWGYM1kBQCKbbZhskwE4BBRajJis8X0Z429Q:1wIYVN:kSx2kcl_VZt7q3-4UpB14dvtror-isS2GLy4AcqxcZk','2026-04-30 22:01:05.986360');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `financeapp_generalledger`
--

DROP TABLE IF EXISTS `financeapp_generalledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `financeapp_generalledger` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `opening_balance` decimal(15,2) NOT NULL,
  `current_balance` decimal(15,2) NOT NULL,
  `period_balance` decimal(15,2) NOT NULL,
  `year_to_date` decimal(15,2) NOT NULL,
  `last_updated` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `last_journal_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_id` (`account_id`),
  KEY `FinanceApp_generalle_last_journal_id_fb434dac_fk_FinanceAp` (`last_journal_id`),
  CONSTRAINT `FinanceApp_generalle_account_id_eb213bee_fk_coa_chart` FOREIGN KEY (`account_id`) REFERENCES `coa_07052026` (`id`),
  CONSTRAINT `FinanceApp_generalle_last_journal_id_fb434dac_fk_FinanceAp` FOREIGN KEY (`last_journal_id`) REFERENCES `financeapp_journalentry` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `financeapp_generalledger`
--

LOCK TABLES `financeapp_generalledger` WRITE;
/*!40000 ALTER TABLE `financeapp_generalledger` DISABLE KEYS */;
INSERT INTO `financeapp_generalledger` VALUES (21,0.00,23730.00,0.00,0.00,'2026-05-06 15:36:02.433854',11,NULL),(22,0.00,25000.00,0.00,0.00,'2026-04-06 22:28:00.255106',19,NULL),(32,0.00,4000.00,0.00,0.00,'2026-05-06 14:09:45.053003',37,NULL),(33,0.00,-4000.00,0.00,0.00,'2026-05-06 14:09:45.059994',13,NULL),(62,0.00,-960.00,0.00,0.00,'2026-05-06 15:36:00.032123',24,NULL),(63,0.00,780.00,0.00,0.00,'2026-05-06 15:36:00.250414',20,NULL),(64,0.00,-500.00,0.00,0.00,'2026-05-06 15:36:00.925430',40,NULL),(65,0.00,2000.00,0.00,0.00,'2026-05-06 15:36:01.592503',39,NULL),(66,0.00,1890.00,0.00,0.00,'2026-05-06 15:36:01.874330',23,NULL),(67,0.00,80.00,0.00,0.00,'2026-05-06 15:36:02.436853',32,NULL);
/*!40000 ALTER TABLE `financeapp_generalledger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `financeapp_journalentry`
--

DROP TABLE IF EXISTS `financeapp_journalentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `financeapp_journalentry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `entry_number` varchar(20) NOT NULL,
  `entry_date` date NOT NULL,
  `description` varchar(200) NOT NULL,
  `status` varchar(10) NOT NULL,
  `posted` tinyint(1) NOT NULL,
  `posted_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `posted_by_id` int DEFAULT NULL,
  `source_trans_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entry_number` (`entry_number`),
  KEY `FinanceApp_journalentry_created_by_id_ebf429b5_fk_auth_user_id` (`created_by_id`),
  KEY `FinanceApp_journalentry_posted_by_id_c64adfc8_fk_auth_user_id` (`posted_by_id`),
  KEY `FinanceApp_journalen_source_trans_id_f758f138_fk_RecPayApp` (`source_trans_id`),
  CONSTRAINT `FinanceApp_journalen_source_trans_id_f758f138_fk_RecPayApp` FOREIGN KEY (`source_trans_id`) REFERENCES `recpayapp_trans` (`id`),
  CONSTRAINT `FinanceApp_journalentry_created_by_id_ebf429b5_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `FinanceApp_journalentry_posted_by_id_c64adfc8_fk_auth_user_id` FOREIGN KEY (`posted_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `financeapp_journalentry`
--

LOCK TABLES `financeapp_journalentry` WRITE;
/*!40000 ALTER TABLE `financeapp_journalentry` DISABLE KEYS */;
INSERT INTO `financeapp_journalentry` VALUES (11,'JV-20260406-0001','2026-04-06','Receipts: Savings Deposit','POSTED',1,'2026-04-06 22:27:59.995299','2026-04-06 22:27:59.996068',NULL,1,4),(12,'JV-20260406-0002','2026-04-06','Receipts: Savings Deposit','POSTED',1,'2026-04-06 22:28:00.235747','2026-04-06 22:28:00.235747',NULL,1,5),(21,'JV-20260506-0001','2026-04-30','Payments: Repairs','POSTED',1,'2026-05-06 14:09:45.040005','2026-05-06 14:09:45.040005',NULL,1,13),(50,'JV-20260506-0002','2026-04-21','Payments: Shares Withdrawal','POSTED',1,'2026-05-06 15:36:00.012129','2026-05-06 15:36:00.012129',NULL,1,12),(51,'JV-20260506-0003','2026-04-21','Payments: Deposit Withdrawal','POSTED',1,'2026-05-06 15:36:00.240420','2026-05-06 15:36:00.241421',NULL,1,11),(52,'JV-20260506-0004','2026-04-21','Receipts: Loan Repayment For June 2026','POSTED',1,'2026-05-06 15:36:00.592863','2026-05-06 15:36:00.593872',NULL,1,10),(53,'JV-20260506-0005','2026-04-21','Payments: Loan Disbursements','POSTED',1,'2026-05-06 15:36:01.568548','2026-05-06 15:36:01.569547',NULL,1,9),(54,'JV-20260506-0006','2026-04-20','Receipts: Shares','POSTED',1,'2026-05-06 15:36:01.842680','2026-05-06 15:36:01.843643',NULL,1,8),(55,'JV-20260506-0007','2026-04-20','Receipts: Enrollment Fees','POSTED',1,'2026-05-06 15:36:02.217353','2026-05-06 15:36:02.217353',NULL,1,7),(56,'JV-20260506-0008','2026-04-20','Receipts: Enrollment Fees','POSTED',1,'2026-05-06 15:36:02.424841','2026-05-06 15:36:02.425841',NULL,1,6);
/*!40000 ALTER TABLE `financeapp_journalentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `financeapp_journalline`
--

DROP TABLE IF EXISTS `financeapp_journalline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `financeapp_journalline` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `debit` decimal(15,2) NOT NULL,
  `credit` decimal(15,2) NOT NULL,
  `line_description` varchar(200) NOT NULL,
  `ledger_updated` tinyint(1) NOT NULL,
  `member_updated` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `journal_id` bigint NOT NULL,
  `member_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FinanceApp_journalli_account_id_e321e874_fk_coa_chart` (`account_id`),
  KEY `FinanceApp_journalli_journal_id_2af2d42f_fk_FinanceAp` (`journal_id`),
  KEY `FinanceApp_journalli_member_id_fcf96e00_fk_MembersAp` (`member_id`),
  CONSTRAINT `FinanceApp_journalli_account_id_e321e874_fk_coa_chart` FOREIGN KEY (`account_id`) REFERENCES `coa_07052026` (`id`),
  CONSTRAINT `FinanceApp_journalli_journal_id_2af2d42f_fk_FinanceAp` FOREIGN KEY (`journal_id`) REFERENCES `financeapp_journalentry` (`id`),
  CONSTRAINT `FinanceApp_journalli_member_id_fcf96e00_fk_MembersAp` FOREIGN KEY (`member_id`) REFERENCES `membersapp_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `financeapp_journalline`
--

LOCK TABLES `financeapp_journalline` WRITE;
/*!40000 ALTER TABLE `financeapp_journalline` DISABLE KEYS */;
INSERT INTO `financeapp_journalline` VALUES (21,5000.00,0.00,'Cash received from Gyimah Daniel Jack',0,0,'2026-04-06 22:28:00.000543',11,11,2),(22,0.00,5000.00,'Credit to Savings Deposit',0,0,'2026-04-06 22:28:00.002939',19,11,2),(23,20000.00,0.00,'Cash received from Lassey Jane Esi Adongo',0,0,'2026-04-06 22:28:00.250331',11,12,3),(24,0.00,20000.00,'Credit to Savings Deposit',0,0,'2026-04-06 22:28:00.251458',19,12,3),(41,4000.00,0.00,'Payment for Salaries and Allowances',0,0,'2026-05-06 14:09:45.042005',37,21,NULL),(42,0.00,4000.00,'Cash paid to Ebow Frimpong',0,0,'2026-05-06 14:09:45.043003',13,21,NULL),(99,960.00,0.00,'Payment for Share Withdrawal',0,0,'2026-05-06 15:36:00.017131',24,50,1),(100,0.00,960.00,'Cash paid to Quaye Isaac Ayitey Reginald',0,0,'2026-05-06 15:36:00.019131',11,50,1),(101,780.00,0.00,'Payment for Savings Withdrawal',0,0,'2026-05-06 15:36:00.244419',20,51,2),(102,0.00,780.00,'Cash paid to Gyimah Daniel Jack',0,0,'2026-05-06 15:36:00.245428',11,51,2),(103,500.00,0.00,'Cash received from Quaye Isaac Ayitey Reginald',0,0,'2026-05-06 15:36:00.603891',11,52,1),(104,0.00,500.00,'Credit to Loan Repayments ',0,0,'2026-05-06 15:36:00.667964',40,52,1),(105,2000.00,0.00,'Payment for Loan Disbursements',0,0,'2026-05-06 15:36:01.579542',39,53,1),(106,0.00,2000.00,'Cash paid to Quaye Isaac Ayitey Reginald',0,0,'2026-05-06 15:36:01.581541',11,53,1),(107,1890.00,0.00,'Cash received from Daniels Nicole Ama Denu',0,0,'2026-05-06 15:36:01.853673',11,54,5),(108,0.00,1890.00,'Credit to Share Capital',0,0,'2026-05-06 15:36:01.855672',23,54,5),(109,40.00,0.00,'Cash received from Crabbe Sarah Dorothy Naa Adjeley',0,0,'2026-05-06 15:36:02.221368',11,55,4),(110,0.00,40.00,'Credit to Enrollment Fees',0,0,'2026-05-06 15:36:02.221368',32,55,4),(111,40.00,0.00,'Cash received from Daniels Nicole Ama Denu',0,0,'2026-05-06 15:36:02.428853',11,56,5),(112,0.00,40.00,'Credit to Enrollment Fees',0,0,'2026-05-06 15:36:02.429849',32,56,5);
/*!40000 ALTER TABLE `financeapp_journalline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_module_helparticle`
--

DROP TABLE IF EXISTS `help_module_helparticle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_module_helparticle` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `content` longtext NOT NULL,
  `order` int unsigned NOT NULL,
  `topic_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `help_module_helparti_topic_id_164519b3_fk_help_modu` (`topic_id`),
  CONSTRAINT `help_module_helparti_topic_id_164519b3_fk_help_modu` FOREIGN KEY (`topic_id`) REFERENCES `help_module_helptopic` (`id`),
  CONSTRAINT `help_module_helparticle_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_module_helparticle`
--

LOCK TABLES `help_module_helparticle` WRITE;
/*!40000 ALTER TABLE `help_module_helparticle` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_module_helparticle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_module_helpcategory`
--

DROP TABLE IF EXISTS `help_module_helpcategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_module_helpcategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `icon` varchar(50) NOT NULL,
  `order` int unsigned NOT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  CONSTRAINT `help_module_helpcategory_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_module_helpcategory`
--

LOCK TABLES `help_module_helpcategory` WRITE;
/*!40000 ALTER TABLE `help_module_helpcategory` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_module_helpcategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_module_helpfeedback`
--

DROP TABLE IF EXISTS `help_module_helpfeedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_module_helpfeedback` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `was_helpful` tinyint(1) DEFAULT NULL,
  `comment` longtext NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  `help_topic_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `help_module_helpfeedback_user_id_adbed9d5_fk_auth_user_id` (`user_id`),
  KEY `help_module_helpfeed_help_topic_id_ad26e449_fk_help_modu` (`help_topic_id`),
  CONSTRAINT `help_module_helpfeed_help_topic_id_ad26e449_fk_help_modu` FOREIGN KEY (`help_topic_id`) REFERENCES `help_module_helptopic` (`id`),
  CONSTRAINT `help_module_helpfeedback_user_id_adbed9d5_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_module_helpfeedback`
--

LOCK TABLES `help_module_helpfeedback` WRITE;
/*!40000 ALTER TABLE `help_module_helpfeedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_module_helpfeedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_module_helpsearch`
--

DROP TABLE IF EXISTS `help_module_helpsearch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_module_helpsearch` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `search_term` varchar(200) NOT NULL,
  `results_count` int unsigned NOT NULL,
  `search_date` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `help_module_helpsearch_user_id_a0e74c9c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `help_module_helpsearch_user_id_a0e74c9c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `help_module_helpsearch_chk_1` CHECK ((`results_count` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_module_helpsearch`
--

LOCK TABLES `help_module_helpsearch` WRITE;
/*!40000 ALTER TABLE `help_module_helpsearch` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_module_helpsearch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_module_helptopic`
--

DROP TABLE IF EXISTS `help_module_helptopic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_module_helptopic` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `content` longtext NOT NULL,
  `help_type` varchar(20) NOT NULL,
  `module_name` varchar(50) NOT NULL,
  `keywords` varchar(500) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `views_count` int unsigned NOT NULL,
  `helpful_count` int unsigned NOT NULL,
  `not_helpful_count` int unsigned NOT NULL,
  `is_featured` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `category_id` bigint NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `updated_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `help_module_helptopi_category_id_5217024e_fk_help_modu` (`category_id`),
  KEY `help_module_helptopic_created_by_id_7c7641ee_fk_auth_user_id` (`created_by_id`),
  KEY `help_module_helptopic_updated_by_id_9cf1813e_fk_auth_user_id` (`updated_by_id`),
  CONSTRAINT `help_module_helptopi_category_id_5217024e_fk_help_modu` FOREIGN KEY (`category_id`) REFERENCES `help_module_helpcategory` (`id`),
  CONSTRAINT `help_module_helptopic_created_by_id_7c7641ee_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `help_module_helptopic_updated_by_id_9cf1813e_fk_auth_user_id` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `help_module_helptopic_chk_1` CHECK ((`views_count` >= 0)),
  CONSTRAINT `help_module_helptopic_chk_2` CHECK ((`helpful_count` >= 0)),
  CONSTRAINT `help_module_helptopic_chk_3` CHECK ((`not_helpful_count` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_module_helptopic`
--

LOCK TABLES `help_module_helptopic` WRITE;
/*!40000 ALTER TABLE `help_module_helptopic` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_module_helptopic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_module_userguide`
--

DROP TABLE IF EXISTS `help_module_userguide`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_module_userguide` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `description` longtext NOT NULL,
  `content` longtext NOT NULL,
  `pdf_file` varchar(100) DEFAULT NULL,
  `cover_image` varchar(100) DEFAULT NULL,
  `module_name` varchar(50) NOT NULL,
  `version` varchar(20) NOT NULL,
  `is_published` tinyint(1) NOT NULL,
  `published_date` datetime(6) DEFAULT NULL,
  `created_date` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `help_module_userguide_created_by_id_960c31a4_fk_auth_user_id` (`created_by_id`),
  CONSTRAINT `help_module_userguide_created_by_id_960c31a4_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_module_userguide`
--

LOCK TABLES `help_module_userguide` WRITE;
/*!40000 ALTER TABLE `help_module_userguide` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_module_userguide` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `investapp_bank`
--

DROP TABLE IF EXISTS `investapp_bank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investapp_bank` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `branch` varchar(100) NOT NULL,
  `sort_code` varchar(20) DEFAULT NULL,
  `bic_code` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investapp_bank`
--

LOCK TABLES `investapp_bank` WRITE;
/*!40000 ALTER TABLE `investapp_bank` DISABLE KEYS */;
INSERT INTO `investapp_bank` VALUES (1,'NIB PLC','Accra','102456','125631'),(2,'GCB PLC','Kokomlemle','2563214','789456');
/*!40000 ALTER TABLE `investapp_bank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `investapp_investment`
--

DROP TABLE IF EXISTS `investapp_investment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investapp_investment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `certificate_no` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `account_no` varchar(50) NOT NULL,
  `other_company` varchar(100) DEFAULT NULL,
  `branch` varchar(100) DEFAULT NULL,
  `term_days` int DEFAULT NULL,
  `maturity_date` date DEFAULT NULL,
  `investment_type` varchar(20) NOT NULL,
  `other_investment_type` varchar(100) DEFAULT NULL,
  `rate` decimal(5,2) NOT NULL,
  `rollover` varchar(3) NOT NULL,
  `processed_date` date DEFAULT NULL,
  `period` varchar(20) NOT NULL,
  `other_period` varchar(100) DEFAULT NULL,
  `interest_expected` decimal(15,2) NOT NULL,
  `interest_earned` decimal(15,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bank_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `InvestApp_investment_bank_id_04f19551_fk_InvestApp_bank_id` (`bank_id`),
  CONSTRAINT `InvestApp_investment_bank_id_04f19551_fk_InvestApp_bank_id` FOREIGN KEY (`bank_id`) REFERENCES `investapp_bank` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investapp_investment`
--

LOCK TABLES `investapp_investment` WRITE;
/*!40000 ALTER TABLE `investapp_investment` DISABLE KEYS */;
INSERT INTO `investapp_investment` VALUES (1,'2569687','2026-05-02',5000.00,'7896541',NULL,'Kokomlemle',90,'2026-06-06','Sweep Calls',NULL,15.00,'Yes','2026-04-02','180 day',NULL,184.93,4254.00,'2026-04-02 17:10:27.685567','2026-04-02 17:10:27.685567',1),(2,'2569687','2026-05-02',5000.00,'7896541',NULL,'Kokomlemle',90,'2026-06-06','Sweep Calls',NULL,15.00,'Yes','2026-04-02','180 day',NULL,184.93,4254.00,'2026-04-02 17:13:26.645464','2026-04-02 17:13:26.645464',1),(3,'2569687','2026-05-02',5000.00,'7896541',NULL,'Kokomlemle',90,'2026-06-06','Sweep Calls',NULL,15.00,'Yes','2026-04-02','180 day',NULL,184.93,4254.00,'2026-04-02 17:13:55.742911','2026-04-02 17:13:55.742911',1);
/*!40000 ALTER TABLE `investapp_investment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loanapp_guarantor`
--

DROP TABLE IF EXISTS `loanapp_guarantor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loanapp_guarantor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `guarantor_name` varchar(150) DEFAULT NULL,
  `guaranteed_amount` decimal(15,2) NOT NULL,
  `guaranteed_date` date NOT NULL,
  `redeemed_amount` decimal(15,2) DEFAULT NULL,
  `redeemed_status` varchar(15) DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  `master_id` bigint NOT NULL,
  `loan_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LoanApp_guarantor_master_id_e7f369b5_fk_MembersApp_master_id` (`master_id`),
  KEY `LoanApp_guarantor_loan_id_8f2d944f_fk_LoanApp_loan_id` (`loan_id`),
  CONSTRAINT `LoanApp_guarantor_loan_id_8f2d944f_fk_LoanApp_loan_id` FOREIGN KEY (`loan_id`) REFERENCES `loanapp_loan` (`id`),
  CONSTRAINT `LoanApp_guarantor_master_id_e7f369b5_fk_MembersApp_master_id` FOREIGN KEY (`master_id`) REFERENCES `membersapp_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loanapp_guarantor`
--

LOCK TABLES `loanapp_guarantor` WRITE;
/*!40000 ALTER TABLE `loanapp_guarantor` DISABLE KEYS */;
INSERT INTO `loanapp_guarantor` VALUES (1,'Quaye Isaac Ayitey Reginald',1000.00,'2026-04-29',0.00,'','ACTIVE',1,4);
/*!40000 ALTER TABLE `loanapp_guarantor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loanapp_loan`
--

DROP TABLE IF EXISTS `loanapp_loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loanapp_loan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `master_name` varchar(60) DEFAULT NULL,
  `date_applied` date NOT NULL,
  `principal` decimal(15,2) NOT NULL,
  `purpose` varchar(500) NOT NULL,
  `voucher_no` varchar(12) DEFAULT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `loan_term` int unsigned NOT NULL,
  `moratorium` int unsigned NOT NULL,
  `disbursement_date` date NOT NULL,
  `date_approved` date NOT NULL,
  `approved_by` varchar(200) NOT NULL,
  `monthly_repayment` decimal(15,2) NOT NULL,
  `next_repayment_date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `guarantor_data` json DEFAULT NULL,
  `master_avail_bal` decimal(15,2) DEFAULT NULL,
  `loan_class_calc` varchar(15) NOT NULL,
  `tot_int` decimal(15,2) DEFAULT NULL,
  `tot_ded` decimal(15,2) DEFAULT NULL,
  `months_remain` int NOT NULL,
  `payment_status` varchar(10) DEFAULT NULL,
  `new_payment_date` date NOT NULL,
  `loan_balance` decimal(15,2) DEFAULT NULL,
  `due_days` int DEFAULT NULL,
  `due_interest` decimal(15,2) DEFAULT NULL,
  `due_repayment` decimal(15,2) DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `overdue_days` int DEFAULT NULL,
  `master_id` bigint NOT NULL,
  `interest_overdue` decimal(15,2) NOT NULL,
  `last_interest_calculation_date` date DEFAULT NULL,
  `last_payment_date` date DEFAULT NULL,
  `last_penalty_calculation_date` date DEFAULT NULL,
  `next_payment_due_date` date DEFAULT NULL,
  `penalty_accrued` decimal(15,2) NOT NULL,
  `repayment_overdue` decimal(15,2) NOT NULL,
  `expiry_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `LoanApp_loan_master_id_6dce3a21_fk_MembersApp_master_id` (`master_id`),
  CONSTRAINT `LoanApp_loan_master_id_6dce3a21_fk_MembersApp_master_id` FOREIGN KEY (`master_id`) REFERENCES `membersapp_master` (`id`),
  CONSTRAINT `loanapp_loan_chk_1` CHECK ((`loan_term` >= 0)),
  CONSTRAINT `loanapp_loan_chk_2` CHECK ((`moratorium` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loanapp_loan`
--

LOCK TABLES `loanapp_loan` WRITE;
/*!40000 ALTER TABLE `loanapp_loan` DISABLE KEYS */;
INSERT INTO `loanapp_loan` VALUES (1,'Quaye Isaac Ayitey Reginald','2026-04-01',2000.00,'Building Materials','123456',4.00,12,0,'2026-04-01','2026-04-01','Gyimah Daniel Jack',213.10,'2026-05-01','New Loan','2026-04-02 00:24:50.746149','2026-04-02 00:24:50.746149','{\"guarantors\": [], \"guarantor_count\": 0, \"total_guaranteed\": 0}',5000.00,'',0.00,0.00,12,'Active','2026-04-02',2000.00,30,80.00,213.10,'2026-05-01',NULL,1,0.00,NULL,NULL,NULL,NULL,0.00,0.00,NULL),(2,'Quaye Isaac Ayitey Reginald','2026-04-21',1000.00,'Testing No Guarantee','1025',3.00,12,0,'2026-04-21','2026-04-21','Gyimah Daniel Jack',100.46,'2026-05-21','New Loan','2026-04-21 18:06:30.454207','2026-04-21 18:06:30.454207','{\"guarantors\": [], \"guarantor_count\": 0, \"total_guaranteed\": 0}',3000.00,'',0.00,0.00,12,'Active','2026-04-21',1000.00,30,30.00,100.46,'2026-05-21',NULL,1,0.00,NULL,NULL,NULL,NULL,0.00,0.00,NULL),(3,'Gyimah Daniel Jack','2026-04-21',4000.00,'Testing 1 Guarantor','2589',3.00,12,0,'2026-04-21','2026-04-21','Gyimah Daniel Jack',401.85,'2026-05-21','New Loan','2026-04-21 18:10:06.463524','2026-04-21 18:10:06.463524','{\"guarantors\": [], \"guarantor_count\": 0, \"total_guaranteed\": 0}',5000.00,'',0.00,0.00,12,'Active','2026-04-21',4000.00,30,120.00,401.85,'2026-05-21',NULL,2,0.00,NULL,NULL,NULL,NULL,0.00,0.00,NULL),(4,'Crabbe Sarah Dorothy Naa Adjeley','2026-04-29',1000.00,'Testing Expiry Date','8974',3.00,12,0,'2026-04-29','2026-04-29','Gyimah Daniel Jack',100.46,'2026-05-29','New Loan','2026-04-30 04:09:13.659440','2026-04-30 04:09:13.659440','{\"guarantors\": [{\"id\": 1, \"date\": \"29/04/2026\", \"name\": \"Quaye Isaac Ayitey Reginald\", \"amount\": \"1000\", \"member_id\": 1, \"available_balance\": \"2000.00\"}], \"guarantor_count\": 1, \"total_guaranteed\": 1000.0}',0.00,'',0.00,0.00,12,'Active','2026-04-30',1000.00,30,30.00,100.46,'2026-05-29',NULL,4,0.00,NULL,NULL,NULL,NULL,0.00,0.00,'2027-04-29');
/*!40000 ALTER TABLE `loanapp_loan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loanapp_loanrepayment`
--

DROP TABLE IF EXISTS `loanapp_loanrepayment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loanapp_loanrepayment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(15,2) NOT NULL,
  `principal_paid` decimal(15,2) NOT NULL,
  `interest_paid` decimal(15,2) NOT NULL,
  `payment_date` date NOT NULL,
  `balance_after` decimal(15,2) NOT NULL,
  `reference` varchar(50) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `loan_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LoanApp_loanrepayment_created_by_id_35ef15d4_fk_auth_user_id` (`created_by_id`),
  KEY `LoanApp_loanrepayment_loan_id_ead1feae_fk_LoanApp_loan_id` (`loan_id`),
  CONSTRAINT `LoanApp_loanrepayment_created_by_id_35ef15d4_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `LoanApp_loanrepayment_loan_id_ead1feae_fk_LoanApp_loan_id` FOREIGN KEY (`loan_id`) REFERENCES `loanapp_loan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loanapp_loanrepayment`
--

LOCK TABLES `loanapp_loanrepayment` WRITE;
/*!40000 ALTER TABLE `loanapp_loanrepayment` DISABLE KEYS */;
/*!40000 ALTER TABLE `loanapp_loanrepayment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loanapp_loantransaction`
--

DROP TABLE IF EXISTS `loanapp_loantransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loanapp_loantransaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_type` varchar(20) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `transaction_date` date NOT NULL,
  `reference` varchar(100) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `loan_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LoanApp_loantransaction_created_by_id_19a0c934_fk_auth_user_id` (`created_by_id`),
  KEY `LoanApp_loantransaction_loan_id_9f57fce1_fk_LoanApp_loan_id` (`loan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loanapp_loantransaction`
--

LOCK TABLES `loanapp_loantransaction` WRITE;
/*!40000 ALTER TABLE `loanapp_loantransaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `loanapp_loantransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loginapp_adminloginhistory`
--

DROP TABLE IF EXISTS `loginapp_adminloginhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loginapp_adminloginhistory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `login_time` datetime(6) NOT NULL,
  `logout_time` datetime(6) DEFAULT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `device_type` varchar(50) NOT NULL,
  `browser` varchar(100) NOT NULL,
  `operating_system` varchar(100) NOT NULL,
  `login_status` varchar(20) NOT NULL,
  `failure_reason` longtext NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LoginApp_adminloginhistory_user_id_8158c3d8_fk_auth_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginapp_adminloginhistory`
--

LOCK TABLES `loginapp_adminloginhistory` WRITE;
/*!40000 ALTER TABLE `loginapp_adminloginhistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `loginapp_adminloginhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loginapp_memberloginhistory`
--

DROP TABLE IF EXISTS `loginapp_memberloginhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loginapp_memberloginhistory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `login_time` datetime(6) NOT NULL,
  `logout_time` datetime(6) DEFAULT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `device_type` varchar(50) NOT NULL,
  `browser` varchar(100) NOT NULL,
  `operating_system` varchar(100) NOT NULL,
  `session_key` varchar(40) NOT NULL,
  `login_status` varchar(20) NOT NULL,
  `failure_reason` longtext NOT NULL,
  `location` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `member_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LoginApp_memberlogin_member_id_9f5fde8f_fk_MembersAp` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loginapp_memberloginhistory`
--

LOCK TABLES `loginapp_memberloginhistory` WRITE;
/*!40000 ALTER TABLE `loginapp_memberloginhistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `loginapp_memberloginhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `membersapp_master`
--

DROP TABLE IF EXISTS `membersapp_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membersapp_master` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(10) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `other_names` varchar(200) NOT NULL,
  `full_name` varchar(150) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `date_enrolled` date DEFAULT NULL,
  `gender` varchar(10) NOT NULL,
  `marital_status` varchar(10) NOT NULL,
  `church_member` varchar(3) NOT NULL,
  `mem_status` varchar(10) DEFAULT NULL,
  `postal_address` longtext NOT NULL,
  `residential_address` longtext NOT NULL,
  `city` varchar(100) NOT NULL,
  `near_landmark` varchar(150) NOT NULL,
  `street_name` varchar(200) NOT NULL,
  `gps` varchar(100) NOT NULL,
  `telephone1` varchar(20) NOT NULL,
  `telephone2` varchar(20) NOT NULL,
  `email_address` varchar(254) NOT NULL,
  `profession` varchar(120) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `enroll_fees_paid` varchar(4) NOT NULL,
  `min_shares_purchased` varchar(4) NOT NULL,
  `nok_name1` varchar(100) NOT NULL,
  `nok_address1` varchar(100) NOT NULL,
  `nok_telephone1` varchar(12) NOT NULL,
  `nok_relation1` varchar(30) NOT NULL,
  `nok_percent1` decimal(5,2) DEFAULT NULL,
  `nok_gps1` varchar(20) NOT NULL,
  `nok_email1` varchar(100) NOT NULL,
  `nok_name2` varchar(100) NOT NULL,
  `nok_address2` varchar(100) NOT NULL,
  `nok_telephone2` varchar(12) NOT NULL,
  `nok_relation2` varchar(30) NOT NULL,
  `nok_percent2` decimal(5,2) DEFAULT NULL,
  `nok_gps2` varchar(20) NOT NULL,
  `nok_email2` varchar(100) NOT NULL,
  `nok_name3` varchar(100) NOT NULL,
  `nok_address3` varchar(100) NOT NULL,
  `nok_telephone3` varchar(12) NOT NULL,
  `nok_relation3` varchar(30) NOT NULL,
  `nok_percent3` decimal(5,2) DEFAULT NULL,
  `nok_gps3` varchar(20) NOT NULL,
  `nok_email3` varchar(100) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `del_rec` varchar(5) DEFAULT NULL,
  `open_balance` decimal(15,2) DEFAULT NULL,
  `tot_deposits` decimal(15,2) DEFAULT NULL,
  `tot_deposit_withdrawal` decimal(15,2) DEFAULT NULL,
  `tot_shares` decimal(15,2) DEFAULT NULL,
  `tot_shares_withdrawal` decimal(15,2) DEFAULT NULL,
  `tot_interest_accrued` decimal(15,2) DEFAULT NULL,
  `tot_dividend` decimal(15,2) DEFAULT NULL,
  `tot_dividend_withdrawal` decimal(15,2) DEFAULT NULL,
  `del_date_time` datetime(6) DEFAULT NULL,
  `del_username` varchar(20) DEFAULT NULL,
  `del_by_name` varchar(150) DEFAULT NULL,
  `date_created` datetime(6) NOT NULL,
  `date_updated` datetime(6) NOT NULL,
  `approved_by_chairman_id` bigint DEFAULT NULL,
  `approved_by_manager_id` bigint DEFAULT NULL,
  `del_user_id` int DEFAULT NULL,
  `sav_defer_int_appl` tinyint(1) NOT NULL,
  `loan_int_rate` decimal(6,4) DEFAULT NULL,
  `sav_int_rate` decimal(6,4) NOT NULL,
  `tot_sav_int_deferred` decimal(15,2) DEFAULT NULL,
  `is_deleted_date` datetime(6) DEFAULT NULL,
  `is_deleted_user_id` int DEFAULT NULL,
  `loan_int_rate_date` datetime(6) DEFAULT NULL,
  `loan_int_rate_user_id` int DEFAULT NULL,
  `sav_defer_int_appl_date` datetime(6) DEFAULT NULL,
  `sav_defer_int_appl_user_id` int DEFAULT NULL,
  `sav_int_rate_date` datetime(6) DEFAULT NULL,
  `sav_int_rate_user_id` int DEFAULT NULL,
  `last_sav_int_accrual_date` date DEFAULT NULL,
  `last_sav_int_accrual_run` datetime(6) DEFAULT NULL,
  `sav_int_accrued` decimal(15,2) DEFAULT NULL,
  `ghana_card_no` varchar(15) DEFAULT NULL,
  `id_card_back` varchar(100) DEFAULT NULL,
  `id_card_front` varchar(100) DEFAULT NULL,
  `profile_image` varchar(100) DEFAULT NULL,
  `signature` varchar(100) DEFAULT NULL,
  `delete_history` json NOT NULL DEFAULT (_utf8mb4'[]'),
  `delete_users` json NOT NULL DEFAULT (_utf8mb4'[]'),
  `restore_history` json NOT NULL DEFAULT (_utf8mb4'[]'),
  `restore_users` json NOT NULL DEFAULT (_utf8mb4'[]'),
  `last_deleted_date` datetime(6) DEFAULT NULL,
  `sav_min_bal` decimal(15,2) DEFAULT NULL,
  `sav_min_bal_days` int DEFAULT NULL,
  `enrollment_fees` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `MembersApp_master_approved_by_chairman_45d1c0da_fk_MembersAp` (`approved_by_chairman_id`),
  KEY `MembersApp_master_approved_by_manager__e64608ba_fk_MembersAp` (`approved_by_manager_id`),
  KEY `MembersApp_master_del_user_id_d1d8e269_fk_auth_user_id` (`del_user_id`),
  KEY `MembersApp_master_is_deleted_user_id_f2b5a1c3_fk_auth_user_id` (`is_deleted_user_id`),
  KEY `MembersApp_master_loan_int_rate_user_id_8770edd2_fk_auth_user_id` (`loan_int_rate_user_id`),
  KEY `MembersApp_master_sav_defer_int_appl_u_4329193d_fk_auth_user` (`sav_defer_int_appl_user_id`),
  KEY `MembersApp_master_sav_int_rate_user_id_337eb519_fk_auth_user_id` (`sav_int_rate_user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membersapp_master`
--

LOCK TABLES `membersapp_master` WRITE;
/*!40000 ALTER TABLE `membersapp_master` DISABLE KEYS */;
INSERT INTO `membersapp_master` VALUES (1,'Mr.','Isaac','Quaye','Ayitey Reginald','Quaye Isaac Ayitey Reginald','1958-06-15','2012-01-01','Male','Married','Yes','Active','P.O. Box Mp, 2371, Mamprobi','Mataheko Near Zoozoo','Accra','Near ZooZoo Restaurant','Oko Adotey Street','GA-437-1245','0244660068','050121212','isaac_quaye@yahoo.com','IT Professional','Member','Yes','Yes','Sarah Crabbe','P.O. Box Mp 2371, Mamprobi','0201982805','Wife',40.00,'GA-426-1234','isaac_quaye@yahoo.com','Priscy Quaye','P.O. Box Mp, 2371, Oninase','0242848180','Daughter',30.00,'GA-222-2222','Priscy@gmail.com','Nii Ayi Quaye','P.O. Box All Saints Anglican Church','0271773779','Son',30.00,'GA-999-9999','NiiAyi@gmail.com',0,'No',0.00,5000.00,0.00,0.00,0.00,0.00,0.00,0.00,NULL,'','','2026-04-01 06:12:50.213267','2026-05-06 15:36:01.598494',NULL,NULL,NULL,0,0.0000,0.0000,0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1.35,'GHA-145-2564-1','','','','member_signatures/2026/04/28/11465.jpg','[]','[]','[]','[]',NULL,5000.00,26,0.00),(2,'Mr.','Daniel','Gyimah','Jack','Gyimah Daniel Jack','1952-03-22','2012-01-01','Male','Married','Yes','Active','P.O. Box 720, Gyaator Street','Oblogo','Accra','Near Total Filling Station','Danny Street','GA-437-1245','22222222201','2222222202','Gymah@gmail.com','Managing Director','Chairman','No','No','','','','',0.00,'','','','','','',0.00,'','','','','','',0.00,'','',0,'No',0.00,5000.00,780.00,0.00,0.00,0.00,0.00,0.00,'2026-04-20 06:16:20.179245','Admin','Admin','2026-04-01 06:19:10.980767','2026-05-06 15:36:00.308381',NULL,NULL,1,1,12.0000,12.5000,0.00,'2026-04-20 07:35:34.130438',1,'2026-04-18 18:26:37.807467',1,'2026-04-18 18:26:37.807467',1,'2026-04-18 18:26:37.807467',1,NULL,NULL,1.71,'GHA-748-2595-2','','','member_photos/2026/04/28/15057.jpg','','[]','[]','[{\"date\": \"2026-04-20T17:02:29.399381+00:00\", \"datetime\": \"2026-04-20 17:02:29.399381+00:00\"}]','[{\"date\": \"2026-04-20T17:02:29.399381+00:00\", \"user_id\": 1, \"username\": \"Admin\"}]',NULL,5000.00,26,0.00),(3,'Mrs.','Jane','Lassey','Esi Adongo','Lassey Jane Esi Adongo','1924-06-15','2012-01-01','Female','Widowed','Yes','Active','','Near Ogbodzo beach','Accra','','','GA-4785-256','333333333301','333333333302','Lassey@gmail.com','HouseWife','Finance','Yes','Yes','','','','',0.00,'','','','','','',0.00,'','','','','','',0.00,'','',0,'No',0.00,20000.00,0.00,0.00,0.00,0.00,0.00,0.00,NULL,'','','2026-04-01 06:21:37.323735','2026-05-28 04:40:43.760120',2,NULL,NULL,0,0.0000,0.0000,0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,5.50,'GHA-526-4152-1','member_ids/2026/04/19/6904.jpg','member_ids/2026/04/19/25238.jpg','','member_signatures/2026/04/19/15057.jpg','[{\"date\": \"2026-04-20T17:03:09.837378+00:00\", \"datetime\": \"2026-04-20 17:03:09.837378+00:00\"}, {\"date\": \"2026-04-20T17:03:51.847006+00:00\", \"datetime\": \"2026-04-20 17:03:51.847006+00:00\"}]','[{\"date\": \"2026-04-20T17:03:09.837378+00:00\", \"user_id\": 1, \"username\": \"Admin\"}, {\"date\": \"2026-04-20T17:03:51.848005+00:00\", \"user_id\": 1, \"username\": \"Admin\"}]','[{\"date\": \"2026-04-20T17:03:18.540087+00:00\", \"datetime\": \"2026-04-20 17:03:18.540087+00:00\"}, {\"date\": \"2026-04-20T17:03:56.780368+00:00\", \"datetime\": \"2026-04-20 17:03:56.780368+00:00\"}]','[{\"date\": \"2026-04-20T17:03:18.540087+00:00\", \"user_id\": 1, \"username\": \"Admin\"}, {\"date\": \"2026-04-20T17:03:56.780368+00:00\", \"user_id\": 1, \"username\": \"Admin\"}]',NULL,20000.00,26,0.00),(4,'Mr.','Sarah','Crabbe','Dorothy Naa Adjeley','Crabbe Sarah Dorothy Naa Adjeley','1962-09-10','2026-04-20','Female','Married','Yes','Active','P.O. Box 45896 Accra','Awoshie','Accra','Odorgonno SHS','Kaadew','GA-7895-1256','0201928956','025639856','Sarah@danMail.ocm','Trader','Member','No','No','Esi Crabbe','P.O. Box 6754, Tema','020639652','Daughter',40.00,'GA-426-1234','Esi@mail.com','Dan Saviour','P.O. Box 4589, Tamale','0205697894','Son',30.00,'GA-222-2222','dan@Saviour.com','Blessing Chuku','P. O. Box 25631, Oduman','0245698741','Nephew',30.00,'GA-789-25896','Blessing@chuku.com',0,'No',0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,NULL,'','','2026-04-20 18:56:25.635926','2026-05-06 15:36:02.232102',2,NULL,NULL,0,0.0000,0.0000,0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0.00,'GHA-415-5623','','','','','[]','[]','[]','[]',NULL,0.00,20,40.00),(5,'Miss','Nicole','Daniels','Ama Denu','Daniels Nicole Ama Denu','2021-06-15','2026-04-20','Female','Single','Yes','Active','P. O. Box 12458, Tema','Korle Gonno','Accra','Near Korle Bu','Adwawu Street','','03021562341','024658974','Nicole@daniels.com','Business Woman','Member','No','No','Sampson','P.O. Box 45789, Accra','0244695895','Daughter',100.00,'GA-426-1234','Samson@anymail.com','Ekow Bona','','','Son',0.00,'','','','','','',0.00,'','',0,'No',0.00,1500.00,900.00,0.00,0.00,0.00,0.00,0.00,NULL,'','','2026-04-20 19:10:59.616222','2026-05-06 15:36:02.438833',2,NULL,NULL,0,0.0000,0.0000,0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0.00,'GHA-415-5623','','','','','[]','[]','[]','[]',NULL,0.00,20,40.00),(6,'Miss','Esther','Addo','Akwele','Addo Esther Akwele','1956-05-14','2026-01-05','Female','Single','Yes','Active','P.O. Box Mp 775, Mamprobi','Dzaator Street Mamprobi','Accra','Near Sempe Schools','Dzaator Street','GA-256321','0244569878','0245968784','EstherAddo@gmail.com','Secretary','Finance','Yes','Yes','Sammy Addo','P.O.','0244660059','Son',30.00,'GA-426-1234','SammyAddo@anymail.com','Nii Adu','Primary School','025674556','Son',60.00,'GA-222-2222','Nii@gmail','Adotey Allotey','P.O. Box 78956, Kumasi','02556987','Nephew',10.00,'GA-999-9999','isaac_quaye@yahoo.com',0,'No',0.00,1500.00,300.00,0.00,0.00,0.00,0.00,0.00,NULL,'','','2026-05-01 22:00:10.204052','2026-05-28 04:40:39.782342',2,NULL,NULL,0,0.0000,0.0000,0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0.00,'GHA-416-8526','','','','','[]','[]','[]','[]',NULL,200.00,24,0.00);
/*!40000 ALTER TABLE `membersapp_master` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `MembersApp_sav_int_t_master_id_301dfa31_fk_MembersAp` (`master_id`)
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

--
-- Table structure for table `recpayapp_trans`
--

DROP TABLE IF EXISTS `recpayapp_trans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recpayapp_trans` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rec_vou_no` varchar(15) DEFAULT NULL,
  `trans_no` varchar(15) DEFAULT NULL,
  `date` date NOT NULL,
  `trans_type` varchar(10) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `pay_mode` varchar(10) NOT NULL,
  `member_no` int DEFAULT NULL,
  `member_name` varchar(40) DEFAULT NULL,
  `non_member_name` varchar(40) DEFAULT NULL,
  `non_member_contact` varchar(50) DEFAULT NULL,
  `bank_date` date DEFAULT NULL,
  `bank` varchar(100) NOT NULL,
  `bank_no` varchar(50) NOT NULL,
  `bank_branch` varchar(100) NOT NULL,
  `cheque_date` date DEFAULT NULL,
  `cheque_no` varchar(15) DEFAULT NULL,
  `momo_no` varchar(50) NOT NULL,
  `momo_name` varchar(100) NOT NULL,
  `ledger_id` varchar(10) DEFAULT NULL,
  `ledger_code` varchar(10) DEFAULT NULL,
  `ledger_name` varchar(100) DEFAULT NULL,
  `purpose` varchar(50) DEFAULT NULL,
  `other_purpose` varchar(50) DEFAULT NULL,
  `details` varchar(50) DEFAULT NULL,
  `loan_name` varchar(50) DEFAULT NULL,
  `batch_number` varchar(20) DEFAULT NULL,
  `posted_at` datetime(6) DEFAULT NULL,
  `status` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `member_id` bigint DEFAULT NULL,
  `updated_by_id` int DEFAULT NULL,
  `loan_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rec_vou_no` (`rec_vou_no`),
  KEY `RecPayApp_trans_created_by_id_44a4815d_fk_auth_user_id` (`created_by_id`),
  KEY `RecPayApp_trans_updated_by_id_051c7938_fk_auth_user_id` (`updated_by_id`),
  KEY `RecPayApp_t_rec_vou_745446_idx` (`rec_vou_no`),
  KEY `RecPayApp_t_trans_n_ec5007_idx` (`trans_no`),
  KEY `RecPayApp_t_date_565aa6_idx` (`date`),
  KEY `RecPayApp_t_trans_t_4c1c3d_idx` (`trans_type`),
  KEY `RecPayApp_t_status_031f76_idx` (`status`),
  KEY `RecPayApp_t_member__65daf3_idx` (`member_id`),
  KEY `RecPayApp_t_batch_n_cf1602_idx` (`batch_number`),
  KEY `RecPayApp_trans_loan_id_1c86f5d9_fk_LoanApp_loan_id` (`loan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recpayapp_trans`
--

LOCK TABLES `recpayapp_trans` WRITE;
/*!40000 ALTER TABLE `recpayapp_trans` DISABLE KEYS */;
INSERT INTO `recpayapp_trans` VALUES (4,'REC:15628','15628','2026-04-06','Receipts',5000.00,'Cash',2,'Gyimah Daniel Jack','','',NULL,'','','',NULL,'','','','19','20101001','Savings Deposit','Savings Deposit','','','','','2026-04-06 22:28:00.023943','POSTED','2026-04-06 20:19:33.099458','2026-04-06 22:28:00.023943',NULL,2,NULL,NULL),(5,'REC:123456','123456','2026-04-06','Receipts',20000.00,'Cash',3,'Lassey Jane Esi Adongo','','',NULL,'','','',NULL,'','','','19','20101001','Savings Deposit','Savings Deposit','','Savings Deposit','','','2026-04-06 22:28:00.263571','POSTED','2026-04-06 20:20:31.652719','2026-04-06 22:28:00.263571',NULL,3,NULL,NULL),(6,'REC:124','124','2026-04-20','Receipts',40.00,'Cash',5,'Daniels Nicole Ama Denu','','',NULL,'','','',NULL,'','','','32','40102001','Enrollment Fees','Enrollment Fees','','Enrollment Fees','','','2026-05-06 15:36:02.443830','POSTED','2026-04-20 19:13:28.023975','2026-05-06 15:36:02.443830',NULL,5,NULL,NULL),(7,'REC:125','125','2026-04-20','Receipts',40.00,'Cash',4,'Crabbe Sarah Dorothy Naa Adjeley','','',NULL,'','','',NULL,'','','','32','40102001','Enrollment Fees','Enrollment Fees','','Enrollment Fees','','','2026-05-06 15:36:02.237090','POSTED','2026-04-20 19:14:17.012044','2026-05-06 15:36:02.237090',NULL,4,NULL,NULL),(8,'REC:12','12','2026-04-20','Receipts',1890.00,'Cash',5,'Daniels Nicole Ama Denu','','',NULL,'','','',NULL,'','','','23','20102001','Share Capital','Share Capital','','Shares','','','2026-05-06 15:36:01.886331','POSTED','2026-04-21 05:28:05.471071','2026-05-06 15:36:01.886331',NULL,5,NULL,NULL),(9,'VOU:2589','2589','2026-04-21','Payments',2000.00,'Cash',1,'Quaye Isaac Ayitey Reginald','','',NULL,'','','',NULL,'','','','39','10105001','Loan Disbursements','Loan Disbursements','','Loan Disbursements','Loan #1 - Quaye Isaac Ayitey Reginald - ₵2000.00','','2026-05-06 15:36:01.608489','POSTED','2026-04-21 23:05:07.401386','2026-05-06 15:36:01.613508',NULL,1,NULL,1),(10,'REC:256','256','2026-04-21','Receipts',500.00,'Cash',1,'Quaye Isaac Ayitey Reginald','','',NULL,'','','',NULL,'','','','40','10105002','Loan Repayments ','Loan Repayments','','Loan Repayment For June 2026','Loan #1 - Quaye Isaac Ayitey Reginald - ₵2000.00','','2026-05-06 15:36:01.358087','POSTED','2026-04-21 23:07:08.759314','2026-05-06 15:36:01.365112',NULL,1,NULL,1),(11,'VOU:4789','4789','2026-04-21','Payments',780.00,'Cash',2,'Gyimah Daniel Jack','','',NULL,'','','',NULL,'','','','20','20101002','Savings Withdrawal','Savings Withdrawal','','Deposit Withdrawal','','','2026-05-06 15:36:00.315377','POSTED','2026-04-22 03:21:57.146606','2026-05-06 15:36:00.315377',NULL,2,NULL,NULL),(12,'VOU:2533','2533','2026-04-21','Payments',960.00,'Cash',1,'Quaye Isaac Ayitey Reginald','','',NULL,'','','',NULL,'','','','24','20102002','Share Withdrawal','Share Withdrawal','','Shares Withdrawal','','','2026-05-06 15:36:00.045113','POSTED','2026-04-22 03:22:44.661287','2026-05-06 15:36:00.046126',NULL,1,NULL,NULL),(13,'VOU:25896','25896','2026-04-30','Payments',4000.00,'Cheque',0,'','Ebow Frimpong','General Medical Practitioneer, Accra',NULL,'Co-Operative Bank','101010','Korle BU','2026-03-13','14562','','','37','50101001','Salaries and Allowances','Salaries and Allowances','','Repairs','','','2026-05-06 14:09:45.063991','POSTED','2026-04-30 19:59:36.965100','2026-05-06 14:09:45.063991',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `recpayapp_trans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services_statetrans`
--

DROP TABLE IF EXISTS `services_statetrans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services_statetrans` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `state_type` varchar(15) DEFAULT NULL,
  `rec_vou_no` varchar(15) DEFAULT NULL,
  `trans_no` varchar(15) DEFAULT NULL,
  `date` date NOT NULL,
  `trans_type` varchar(10) DEFAULT NULL,
  `amount` decimal(15,2) NOT NULL,
  `pay_mode` varchar(10) DEFAULT NULL,
  `loan_name` varchar(50) DEFAULT NULL,
  `master_name` varchar(40) DEFAULT NULL,
  `non_member_name` varchar(40) DEFAULT NULL,
  `non_member_contact` varchar(50) DEFAULT NULL,
  `bank_date` date DEFAULT NULL,
  `bank` varchar(100) NOT NULL,
  `bank_no` varchar(50) NOT NULL,
  `bank_branch` varchar(100) NOT NULL,
  `cheque_date` date DEFAULT NULL,
  `cheque_no` varchar(15) DEFAULT NULL,
  `momo_no` varchar(50) NOT NULL,
  `momo_name` varchar(100) NOT NULL,
  `ledger_id` varchar(10) DEFAULT NULL,
  `ledger_code` varchar(10) DEFAULT NULL,
  `ledger_name` varchar(100) DEFAULT NULL,
  `purpose` varchar(50) DEFAULT NULL,
  `details` varchar(50) DEFAULT NULL,
  `posted_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `loan_id` bigint DEFAULT NULL,
  `master_id` bigint DEFAULT NULL,
  `updated_by_id` int DEFAULT NULL,
  `state_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rec_vou_no` (`rec_vou_no`),
  KEY `services_statetrans_created_by_id_db1b3989_fk_auth_user_id` (`created_by_id`),
  KEY `services_statetrans_loan_id_36f95c38_fk_LoanApp_loan_id` (`loan_id`),
  KEY `services_statetrans_master_id_369e1592_fk_MembersApp_master_id` (`master_id`),
  KEY `services_statetrans_updated_by_id_f1510a5f_fk_auth_user_id` (`updated_by_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services_statetrans`
--

LOCK TABLES `services_statetrans` WRITE;
/*!40000 ALTER TABLE `services_statetrans` DISABLE KEYS */;
/*!40000 ALTER TABLE `services_statetrans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services_stateupdate`
--

DROP TABLE IF EXISTS `services_stateupdate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services_stateupdate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rec_vou_no` varchar(15) DEFAULT NULL,
  `trans_no` varchar(15) DEFAULT NULL,
  `date` date NOT NULL,
  `trans_type` varchar(10) DEFAULT NULL,
  `amount` decimal(15,2) NOT NULL,
  `old_shares` decimal(15,2) DEFAULT NULL,
  `new_shares` decimal(15,2) DEFAULT NULL,
  `old_shares_withdrawal` decimal(15,2) DEFAULT NULL,
  `new_shares_withdrawal` decimal(15,2) DEFAULT NULL,
  `old_deposit` decimal(15,2) DEFAULT NULL,
  `new_deposit` decimal(15,2) DEFAULT NULL,
  `old_deposit_withdrawal` decimal(15,2) DEFAULT NULL,
  `new_deposit_withdrawal` decimal(15,2) DEFAULT NULL,
  `old_dividend` decimal(15,2) DEFAULT NULL,
  `new_dividend` decimal(15,2) DEFAULT NULL,
  `old_dividend_withdrawal` decimal(15,2) DEFAULT NULL,
  `new_dividend_withdrawal` decimal(15,2) DEFAULT NULL,
  `old_int_accrued` decimal(15,2) DEFAULT NULL,
  `new_int_accrued` decimal(15,2) DEFAULT NULL,
  `old_available_balance` decimal(15,2) DEFAULT NULL,
  `new_available_balance` decimal(15,2) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `updated_by_id` int DEFAULT NULL,
  `trans_amount` decimal(15,2) DEFAULT NULL,
  `state_update_date` date DEFAULT NULL,
  `new_enrollment_fees` decimal(15,2) DEFAULT NULL,
  `old_enrollment_fees` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rec_vou_no` (`rec_vou_no`),
  KEY `services_stateupdate_created_by_id_d6206d48_fk_auth_user_id` (`created_by_id`),
  KEY `services_stateupdate_updated_by_id_e636c672_fk_auth_user_id` (`updated_by_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services_stateupdate`
--

LOCK TABLES `services_stateupdate` WRITE;
/*!40000 ALTER TABLE `services_stateupdate` DISABLE KEYS */;
INSERT INTO `services_stateupdate` VALUES (1,'VOU:2533','2533','2026-04-21','Payments',960.00,0.00,0.00,0.00,0.00,5000.00,5000.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,5000.00,5000.00,'2026-05-06 15:36:00.043115','2026-05-06 15:36:00.043115',1,1,960.00,'2026-05-06',0.00,0.00),(2,'VOU:4789','4789','2026-04-21','Payments',780.00,0.00,0.00,0.00,0.00,5000.00,5000.00,0.00,780.00,0.00,0.00,0.00,0.00,0.00,0.00,5000.00,4220.00,'2026-05-06 15:36:00.314378','2026-05-06 15:36:00.314378',1,1,780.00,'2026-05-06',0.00,0.00),(3,'REC:256','256','2026-04-21','Receipts',500.00,0.00,0.00,0.00,0.00,5000.00,5000.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,5000.00,5000.00,'2026-05-06 15:36:00.957386','2026-05-06 15:36:00.957386',1,1,500.00,'2026-05-06',0.00,0.00),(4,'VOU:2589','2589','2026-04-21','Payments',2000.00,0.00,0.00,0.00,0.00,5000.00,5000.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,5000.00,5000.00,'2026-05-06 15:36:01.607493','2026-05-06 15:36:01.607493',1,1,2000.00,'2026-05-06',0.00,0.00),(5,'REC:12','12','2026-04-20','Receipts',1890.00,0.00,0.00,0.00,0.00,1500.00,1500.00,900.00,900.00,0.00,0.00,0.00,0.00,0.00,0.00,600.00,600.00,'2026-05-06 15:36:01.885321','2026-05-06 15:36:01.885321',1,1,1890.00,'2026-05-06',0.00,0.00),(6,'REC:125','125','2026-04-20','Receipts',40.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,'2026-05-06 15:36:02.236087','2026-05-06 15:36:02.236087',1,1,40.00,'2026-05-06',40.00,0.00),(7,'REC:124','124','2026-04-20','Receipts',40.00,0.00,0.00,0.00,0.00,1500.00,1500.00,900.00,900.00,0.00,0.00,0.00,0.00,0.00,0.00,600.00,600.00,'2026-05-06 15:36:02.442846','2026-05-06 15:36:02.442846',1,1,40.00,'2026-05-06',40.00,0.00);
/*!40000 ALTER TABLE `services_stateupdate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `syssetup_auditlog`
--

DROP TABLE IF EXISTS `syssetup_auditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `syssetup_auditlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) NOT NULL,
  `model_name` varchar(100) NOT NULL,
  `record_id` int DEFAULT NULL,
  `description` longtext NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `SysSetup_auditlog_user_id_b420ba96_fk_auth_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `syssetup_auditlog`
--

LOCK TABLES `syssetup_auditlog` WRITE;
/*!40000 ALTER TABLE `syssetup_auditlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `syssetup_auditlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `syssetup_fiscalperiod`
--

DROP TABLE IF EXISTS `syssetup_fiscalperiod`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `syssetup_fiscalperiod` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `period_type` varchar(20) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` varchar(10) NOT NULL,
  `is_current` tinyint(1) NOT NULL,
  `closed_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `closed_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `SysSetup_fiscalperiod_closed_by_id_e8adfb11_fk_auth_user_id` (`closed_by_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `syssetup_fiscalperiod`
--

LOCK TABLES `syssetup_fiscalperiod` WRITE;
/*!40000 ALTER TABLE `syssetup_fiscalperiod` DISABLE KEYS */;
/*!40000 ALTER TABLE `syssetup_fiscalperiod` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `syssetup_systempreference`
--

DROP TABLE IF EXISTS `syssetup_systempreference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `syssetup_systempreference` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `theme` varchar(10) NOT NULL,
  `items_per_page` int NOT NULL,
  `email_notifications` tinyint(1) NOT NULL,
  `sms_notifications` tinyint(1) NOT NULL,
  `show_dashboard_widgets` tinyint(1) NOT NULL,
  `default_dashboard` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `syssetup_systempreference`
--

LOCK TABLES `syssetup_systempreference` WRITE;
/*!40000 ALTER TABLE `syssetup_systempreference` DISABLE KEYS */;
/*!40000 ALTER TABLE `syssetup_systempreference` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `syssetup_systemsettings`
--

DROP TABLE IF EXISTS `syssetup_systemsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `syssetup_systemsettings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `company_name` varchar(200) NOT NULL,
  `company_short_name` varchar(50) NOT NULL,
  `company_registration` varchar(50) NOT NULL,
  `company_tax_id` varchar(50) NOT NULL,
  `company_address` longtext NOT NULL,
  `company_city` varchar(100) NOT NULL,
  `company_region` varchar(100) NOT NULL,
  `company_country` varchar(100) NOT NULL,
  `company_phone` varchar(50) NOT NULL,
  `company_email` varchar(254) NOT NULL,
  `company_website` varchar(200) NOT NULL,
  `company_logo` varchar(100) DEFAULT NULL,
  `currency` varchar(3) NOT NULL,
  `currency_symbol` varchar(5) NOT NULL,
  `date_format` varchar(20) NOT NULL,
  `fiscal_year_start` int NOT NULL,
  `accounting_method` varchar(20) NOT NULL,
  `default_interest_rate` decimal(5,2) NOT NULL,
  `default_loan_term` int NOT NULL,
  `max_loan_amount` decimal(15,2) NOT NULL,
  `min_loan_amount` decimal(15,2) NOT NULL,
  `moratorium_period` int NOT NULL,
  `late_payment_penalty` decimal(5,2) NOT NULL,
  `min_savings_balance` decimal(15,2) NOT NULL,
  `savings_interest_rate` decimal(5,2) NOT NULL,
  `max_login_attempts` int NOT NULL,
  `session_timeout` int NOT NULL,
  `password_expiry_days` int NOT NULL,
  `require_strong_password` tinyint(1) NOT NULL,
  `email_notifications` tinyint(1) NOT NULL,
  `sms_notifications` tinyint(1) NOT NULL,
  `admin_email` varchar(254) NOT NULL,
  `report_footer` longtext NOT NULL,
  `show_audit_trail` tinyint(1) NOT NULL,
  `default_items_per_page` int NOT NULL,
  `system_name` varchar(100) NOT NULL,
  `system_version` varchar(20) NOT NULL,
  `maintenance_mode` tinyint(1) NOT NULL,
  `debug_mode` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by_id` int DEFAULT NULL,
  `bank_account_name1` varchar(200) NOT NULL,
  `bank_account_name2` varchar(200) NOT NULL,
  `bank_account_number1` varchar(100) NOT NULL,
  `bank_account_number2` varchar(100) NOT NULL,
  `bank_branch1` varchar(200) NOT NULL,
  `bank_branch2` varchar(200) NOT NULL,
  `bank_name1` varchar(200) NOT NULL,
  `bank_name2` varchar(200) NOT NULL,
  `company_favicon` varchar(100) DEFAULT NULL,
  `savings_interest_application` varchar(13) NOT NULL,
  `stop_savings_interest_calculation` tinyint(1) NOT NULL,
  `last_interest_accrual_date` datetime(6) DEFAULT NULL,
  `loan_interest_rate` decimal(5,2) NOT NULL,
  `min_savings_balance_days` int DEFAULT NULL,
  `last_savings_min_proc_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `SysSetup_systemsettings_updated_by_id_0ddd206a_fk_auth_user_id` (`updated_by_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `syssetup_systemsettings`
--

LOCK TABLES `syssetup_systemsettings` WRITE;
/*!40000 ALTER TABLE `syssetup_systemsettings` DISABLE KEYS */;
INSERT INTO `syssetup_systemsettings` VALUES (1,'St. Andrews Co-Operative Credit Union','St. Andrews Credit Union','','','','','','Ghana','','','','','GHS','₵','dd/mm/yyyy',1,'accrual',3.00,12,50000.00,100.00,0,5.00,50.00,10.00,5,30,90,1,1,0,'','Thank you for banking with us',1,50,'Loan Management System','1.0',0,0,'2026-05-28 04:40:44.791014',NULL,'','','','','','','','','','',0,'2026-04-19 00:00:00.000000',3.00,90,'2026-05-27');
/*!40000 ALTER TABLE `syssetup_systemsettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userauth_userprofile`
--

DROP TABLE IF EXISTS `userauth_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userauth_userprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) NOT NULL,
  `department` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  `employee_id` varchar(20) DEFAULT NULL,
  `last_login_ip` char(39) DEFAULT NULL,
  `login_attempts` int NOT NULL,
  `account_locked` tinyint(1) NOT NULL,
  `theme` varchar(20) NOT NULL,
  `items_per_page` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `employee_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userauth_userprofile`
--

LOCK TABLES `userauth_userprofile` WRITE;
/*!40000 ALTER TABLE `userauth_userprofile` DISABLE KEYS */;
INSERT INTO `userauth_userprofile` VALUES (1,'','','VIEWER',NULL,NULL,0,0,'light',50,'2026-03-28 04:23:34.005935','2026-05-12 05:30:48.629863',1),(2,'','','VIEWER',NULL,NULL,0,0,'light',50,'2026-04-02 00:22:53.577450','2026-04-02 17:05:10.234632',2);
/*!40000 ALTER TABLE `userauth_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'CredDb'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-11 21:32:44
