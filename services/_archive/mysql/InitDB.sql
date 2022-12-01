-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: localhost    Database:
-- ------------------------------------------------------
-- Server version	8.0.27

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
-- Table structure for table `login_method`
--

DROP TABLE IF EXISTS `login_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_method` (
  `entity_id` varchar(32) NOT NULL,
  `version` varchar(32) NOT NULL,
  `previous_version` varchar(32) DEFAULT '00000000000000000000000000000000',
  `active` tinyint(1) DEFAULT '1',
  `latest` tinyint(1) DEFAULT '1',
  `changed_by_id` varchar(32) DEFAULT NULL,
  `changed_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `name` varchar(100) NOT NULL,
  `user_name` varchar(240) NULL DEFAULT NULL,
  `email` varchar(320) DEFAULT NULL,
  `person_id` varchar(32) DEFAULT NULL,
  `access_token` text NULL DEFAULT NULL,
  `refresh_token` varchar(255) NULL DEFAULT NULL,
  `expires_in` int(11) NULL DEFAULT NULL,
  `refresh_token_expires_in` int(11) NULL DEFAULT NULL,
  `scope` varchar(255) NULL DEFAULT NULL,
  `token_type` varchar(255) NULL DEFAULT NULL,
  `sub` varchar(255) NULL DEFAULT NULL,
  `data_access_expiration_time` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`entity_id`,`version`),
  INDEX latest_ind (`entity_id`,`latest`,`active`),
  INDEX person_latest_ind (`person_id`,`latest`,`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_method`
--

LOCK TABLES `login_method` WRITE;
/*!40000 ALTER TABLE `login_method` DISABLE KEYS */;
/*!40000 ALTER TABLE `login_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `entity_id` varchar(32) NOT NULL,
  `version` varchar(32) NOT NULL,
  `previous_version` varchar(32) DEFAULT '00000000000000000000000000000000',
  `active` tinyint(1) DEFAULT '1',
  `latest` tinyint(1) DEFAULT '1',
  `changed_by_id` varchar(32) DEFAULT NULL,
  `changed_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `first_name` varchar(120) DEFAULT NULL,
  `last_name` varchar(120) DEFAULT NULL,
  `email` varchar(320) DEFAULT NULL,
  `password` varchar(320) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT '0',
  `verified_on` int(11) NULL DEFAULT NULL,
  `access_token` varchar(255) NULL DEFAULT NULL,
  `expires_in` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`entity_id`,`version`),
  INDEX latest_ind (`entity_id`,`latest`,`active`),
  INDEX email_latest_ind (`email`,`latest`,`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `otp_method`
--
DROP TABLE IF EXISTS `otp_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_method` (
  `entity_id` varchar(32) NOT NULL,
  `version` varchar(32) NOT NULL,
  `previous_version` varchar(32) DEFAULT '00000000000000000000000000000000',
  `active` tinyint(1) DEFAULT '1',
  `latest` tinyint(1) DEFAULT '1',
  `changed_by_id` varchar(32) DEFAULT NULL,
  `changed_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `name` varchar(120) DEFAULT NULL,
  `person_id` varchar(32) NOT NULL,
  `secret` varchar(32) NOT NULL,
  `enabled` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`entity_id`,`version`),
  INDEX latest_ind (`entity_id`,`latest`,`active`),
  INDEX person_latest_ind (`person_id`,`latest`,`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `otp_method`
--

LOCK TABLES `otp_method` WRITE;
/*!40000 ALTER TABLE `otp_method` DISABLE KEYS */;
/*!40000 ALTER TABLE `otp_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recovery_code`
--
DROP TABLE IF EXISTS `recovery_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recovery_code` (
  `entity_id` varchar(32) NOT NULL,
  `version` varchar(32) NOT NULL,
  `previous_version` varchar(32) DEFAULT '00000000000000000000000000000000',
  `active` tinyint(1) DEFAULT '1',
  `latest` tinyint(1) DEFAULT '1',
  `changed_by_id` varchar(32) DEFAULT NULL,
  `changed_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `otp_method_id` varchar(32) NOT NULL,
  `token` varchar(32) NOT NULL,
  PRIMARY KEY (`entity_id`,`version`),
  INDEX latest_ind (`entity_id`,`latest`,`active`),
  INDEX otp_method_latest_ind (`otp_method_id`,`latest`,`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recovery_code`
--

LOCK TABLES `recovery_code` WRITE;
/*!40000 ALTER TABLE `recovery_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `recovery_code` ENABLE KEYS */;
UNLOCK TABLES;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-11-22 18:36:38
