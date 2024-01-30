-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.6.16-MariaDB-0ubuntu0.22.04.1 - Ubuntu 22.04
-- Server OS:                    debian-linux-gnu
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for ofs
DROP DATABASE IF EXISTS `ofs`;
CREATE DATABASE IF NOT EXISTS `ofs` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `ofs`;

-- Dumping structure for table ofs.app_ofs_category
DROP TABLE IF EXISTS `app_ofs_category`;
CREATE TABLE IF NOT EXISTS `app_ofs_category` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_id` varchar(100) NOT NULL,
  `category` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.app_ofs_customuser
DROP TABLE IF EXISTS `app_ofs_customuser`;
CREATE TABLE IF NOT EXISTS `app_ofs_customuser` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) DEFAULT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) DEFAULT 0,
  `username` varchar(150) DEFAULT NULL,
  `first_name` varchar(150) DEFAULT NULL,
  `last_name` varchar(150) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `is_staff` tinyint(1) DEFAULT 0,
  `is_active` tinyint(1) DEFAULT 1,
  `date_joined` datetime(6) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `otp` varchar(50) DEFAULT NULL,
  `otp_created_at` varchar(50) DEFAULT NULL,
  `otp_verified` varchar(50) DEFAULT NULL,
  `userrole` varchar(50) DEFAULT 'user',
  `first_login` int(11) DEFAULT 1,
  `otp_sent` varchar(50) DEFAULT NULL,
  `otp_inserted` varchar(50) DEFAULT NULL,
  `user_verfied` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.app_ofs_customuser_groups
DROP TABLE IF EXISTS `app_ofs_customuser_groups`;
CREATE TABLE IF NOT EXISTS `app_ofs_customuser_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_ofs_customuser_groups_customuser_id_group_id_beb8cd83_uniq` (`customuser_id`,`group_id`),
  KEY `app_ofs_customuser_groups_group_id_29e967e1_fk_auth_group_id` (`group_id`),
  CONSTRAINT `app_ofs_customuser_g_customuser_id_bb9f16d8_fk_app_ofs_c` FOREIGN KEY (`customuser_id`) REFERENCES `app_ofs_customuser` (`id`),
  CONSTRAINT `app_ofs_customuser_groups_group_id_29e967e1_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.app_ofs_customuser_user_permissions
DROP TABLE IF EXISTS `app_ofs_customuser_user_permissions`;
CREATE TABLE IF NOT EXISTS `app_ofs_customuser_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_ofs_customuser_user__customuser_id_permission_7ee8f71f_uniq` (`customuser_id`,`permission_id`),
  KEY `app_ofs_customuser_u_permission_id_de5e7f26_fk_auth_perm` (`permission_id`),
  CONSTRAINT `app_ofs_customuser_u_customuser_id_27d1bb7d_fk_app_ofs_c` FOREIGN KEY (`customuser_id`) REFERENCES `app_ofs_customuser` (`id`),
  CONSTRAINT `app_ofs_customuser_u_permission_id_de5e7f26_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.app_ofs_products
DROP TABLE IF EXISTS `app_ofs_products`;
CREATE TABLE IF NOT EXISTS `app_ofs_products` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `product_id` varchar(50) NOT NULL,
  `product_name` varchar(50) NOT NULL,
  `product_description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.app_ofs_salesdata
DROP TABLE IF EXISTS `app_ofs_salesdata`;
CREATE TABLE IF NOT EXISTS `app_ofs_salesdata` (
  `month` varchar(100) DEFAULT NULL,
  `sales` varchar(100) DEFAULT NULL,
  `id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.auth_group
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.auth_group_permissions
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.auth_permission
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.category_info
DROP TABLE IF EXISTS `category_info`;
CREATE TABLE IF NOT EXISTS `category_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `updated_on` datetime DEFAULT current_timestamp(),
  `userid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `category_id` (`category_id`),
  KEY `fk_userid` (`userid`),
  CONSTRAINT `fk_userid` FOREIGN KEY (`userid`) REFERENCES `app_ofs_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.django_admin_log
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_app_ofs_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_app_ofs_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `app_ofs_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.django_content_type
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.django_migrations
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.django_session
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.inventorydetails_date
DROP TABLE IF EXISTS `inventorydetails_date`;
CREATE TABLE IF NOT EXISTS `inventorydetails_date` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `quantity` varchar(100) DEFAULT NULL,
  `product_id` varchar(100) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_inventorydetails_date_product_info` (`product_id`),
  KEY `FK_inventorydetails_date_app_ofs_customuser` (`user_id`),
  CONSTRAINT `FK_inventorydetails_date_app_ofs_customuser` FOREIGN KEY (`user_id`) REFERENCES `app_ofs_customuser` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_inventorydetails_date_product_info` FOREIGN KEY (`product_id`) REFERENCES `product_info` (`product_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.inventory_details
DROP TABLE IF EXISTS `inventory_details`;
CREATE TABLE IF NOT EXISTS `inventory_details` (
  `inventory_id` int(11) NOT NULL AUTO_INCREMENT,
  `quantity` varchar(50) DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  `productid` varchar(50) DEFAULT NULL,
  `categoryid` varchar(50) DEFAULT NULL,
  `userid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`inventory_id`),
  KEY `product_id` (`productid`),
  KEY `category_id` (`categoryid`),
  CONSTRAINT `category_id` FOREIGN KEY (`categoryid`) REFERENCES `category_info` (`category_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `product_id` FOREIGN KEY (`productid`) REFERENCES `product_info` (`product_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.logs
DROP TABLE IF EXISTS `logs`;
CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `description` varchar(50) DEFAULT NULL,
  `logged_on` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=218 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.order_info
DROP TABLE IF EXISTS `order_info`;
CREATE TABLE IF NOT EXISTS `order_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` varchar(50) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `ordered_date` date DEFAULT NULL,
  `delivery_date` date DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `productid` varchar(50) DEFAULT NULL,
  `userid` bigint(20) DEFAULT NULL,
  `total_price` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT curdate(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `productid` (`productid`),
  KEY `user_id` (`userid`),
  CONSTRAINT `productid` FOREIGN KEY (`productid`) REFERENCES `product_info` (`product_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `user_id` FOREIGN KEY (`userid`) REFERENCES `app_ofs_customuser` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.product_info
DROP TABLE IF EXISTS `product_info`;
CREATE TABLE IF NOT EXISTS `product_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` varchar(50) DEFAULT NULL,
  `product_name` varchar(50) DEFAULT NULL,
  `product_description` varchar(200) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `userid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_id` (`product_id`),
  KEY `userid` (`userid`),
  KEY `categoryid` (`category`),
  KEY `product_name` (`product_name`),
  CONSTRAINT `userid` FOREIGN KEY (`userid`) REFERENCES `app_ofs_customuser` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table ofs.user_verify
DROP TABLE IF EXISTS `user_verify`;
CREATE TABLE IF NOT EXISTS `user_verify` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email` varchar(50) NOT NULL,
  `otp_sent` varchar(50) NOT NULL,
  `otp_inserted` varchar(50) NOT NULL,
  `otp_verified` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
