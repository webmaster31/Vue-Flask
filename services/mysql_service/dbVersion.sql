--
-- Table structure for table `db_version`
--
DROP TABLE IF EXISTS `db_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `db_version` (
  `version` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `db_version`
--
LOCK TABLES `db_version` WRITE;
INSERT INTO `db_version` (version) VALUES (0000000000);
/*!40000 ALTER TABLE `db_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `db_version` ENABLE KEYS */;
UNLOCK TABLES;