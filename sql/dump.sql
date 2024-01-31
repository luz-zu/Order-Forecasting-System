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
CREATE DATABASE IF NOT EXISTS `ofs` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `ofs`;

-- Dumping structure for table ofs.app_ofs_category
CREATE TABLE IF NOT EXISTS `app_ofs_category` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_id` varchar(100) NOT NULL,
  `category` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.app_ofs_category: ~0 rows (approximately)

-- Dumping structure for table ofs.app_ofs_customuser
CREATE TABLE IF NOT EXISTS `app_ofs_customuser` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `company_id` bigint(20) NOT NULL DEFAULT 0,
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
  `added_by` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `company_id` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.app_ofs_customuser: ~14 rows (approximately)
INSERT INTO `app_ofs_customuser` (`id`, `company_id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `dob`, `phone_number`, `otp`, `otp_created_at`, `otp_verified`, `userrole`, `first_login`, `added_by`) VALUES
	(28, 0, 'pbkdf2_sha256$720000$dy2M0njk4zokEXLpPL2baA$1KM75lXwqRmOA7293sRzM3AIVasTGaIhlFpR57b1AfI=', '2024-01-31 04:55:46.099645', 0, 'lbaj', 'Lujana', 'Bajracharya', 'lujanabajra@gmail.com', 1, 1, '2024-01-30 07:31:58.871307', NULL, '', '797715', '2024-01-31 04:55:12.785669', NULL, 'admin', 1, 28),
	(29, 0, 'pbkdf2_sha256$720000$V9qsYbAxD7Z0WPYbvDdZCc$zFwzsrQc+Fw4lvSxnv7eyruU7voxF3C/Z07LRjcVHIY=', NULL, 0, 'anki', 'Ankita', 'Bajracharya', 'bajraanki@gmail.com', 0, 1, '2024-01-30 07:34:22.102729', NULL, '', NULL, NULL, NULL, '', 1, NULL),
	(30, 0, 'pbkdf2_sha256$720000$FNWD3mxyX3JKi51FrhZrYr$Z85aXRJAhk/V4B5UpfV6b92z1ffelYjj69DcDrLp3ZQ=', NULL, 0, 'lujana', 'Lujana', 'Bajracharya', 'lujanabajra@gmail.com', 0, 1, '2024-01-30 07:43:15.575427', NULL, '', NULL, NULL, NULL, '', 1, NULL),
	(31, 0, 'pbkdf2_sha256$720000$NGW6bgmGcxfVeyk5lV53zz$4QMcYVzQ+qg0K3svOteITcdBVbsS3r2MKY9Te15NALI=', NULL, 0, 'gadha', 'Prashay', 'Shrestha', 'prashayshrestha@gmail.com', 0, 1, '2024-01-30 08:28:09.353906', NULL, '', NULL, NULL, NULL, 'admin', 1, NULL),
	(32, 0, 'pbkdf2_sha256$720000$mxe0Xh0bzkxMDPfH0eJWID$OtcNwAuQDGiT1ulQSIlK3wosxBmdwH3qKb31UJOCGCA=', NULL, 0, 'lujana_175', 'Lujana', 'Bajracharya', 'lujanabajra@gmail.com', 0, 1, NULL, NULL, '9989', NULL, NULL, NULL, 'staff', 1, NULL),
	(33, 0, 'pbkdf2_sha256$720000$mxe0Xh0bzkxMDPfH0eJWID$OtcNwAuQDGiT1ulQSIlK3wosxBmdwH3qKb31UJOCGCA=', NULL, 0, 'lujana_429', 'Lujana', 'Bajracharya', 'lujanabajra@gmail.com', 0, 1, NULL, NULL, '9989', NULL, NULL, NULL, 'staff', 1, NULL),
	(34, 0, 'pbkdf2_sha256$720000$0ZgBgMxdiXVu1fAgnH3bPx$DN3lP7aMiQKFvbsGNS+EVtdS/vqRss2FtQZS9OEnUPA=', NULL, 0, 'lujana_357', 'Lujana', 'Bajracharya', 'lujanabajra@gmail.com', 0, 1, NULL, NULL, '1234512345', NULL, NULL, NULL, 'staff', 1, NULL),
	(35, 0, 'pbkdf2_sha256$720000$dy2M0njk4zokEXLpPL2baA$1KM75lXwqRmOA7293sRzM3AIVasTGaIhlFpR57b1AfI=', '2024-01-30 16:49:48.721266', 0, 'manoj_183', 'Manoj', 'Karki', 'manojgamer99@gmail.com', 0, 1, NULL, NULL, '9841147588', '596404', '2024-01-30 16:45:07.305783', NULL, 'staff', 1, NULL),
	(36, 0, 'pbkdf2_sha256$720000$dy2M0njk4zokEXLpPL2baA$1KM75lXwqRmOA7293sRzM3AIVasTGaIhlFpR57b1AfI=', '2024-01-30 17:19:52.687015', 0, 'manoj_375', 'Manoj', 'Khanal', 'manoj.karki695@gmail.com', 0, 1, NULL, NULL, '9841147588', NULL, NULL, NULL, 'staff', 1, 28),
	(37, 0, 'pbkdf2_sha256$720000$q3cHKpgACwdCfAkSVxk3Hy$IM2aOB/IVKk+ENmKgKmQLkR5hxoG3ns0CXrGaKMSjzY=', NULL, 0, 'nimi', 'Nimisha', 'Pradhan', '', 0, 1, '2024-01-30 17:26:37.892816', NULL, '', NULL, NULL, NULL, 'admin', 1, NULL),
	(38, 0, 'pbkdf2_sha256$720000$Whafx8OqW6Z4BLqxdiBQ07$HPn20iGic09SHoRVrpowC/XZ2eaPt6BG/nGhfiOOARY=', NULL, 0, 'nimisha', 'Nimisha', 'Pradhan', 'nimisha@gmail.com', 0, 1, '2024-01-30 17:27:46.836822', NULL, '', NULL, NULL, NULL, 'admin', 1, NULL),
	(39, 122, 'pbkdf2_sha256$720000$qNP0Mn0J96lQDkjAzAGRC8$y+ZJPxcZCNAMVzOmCsnjvM3/szDiMPEBXi3bsww/vv8=', '2024-01-31 04:04:39.468455', 0, 'nimiP', 'Nimisha', 'Pradhan', 'nimiP@gmail.com', 0, 1, '2024-01-30 17:32:44.825994', NULL, '', NULL, NULL, NULL, 'admin', 1, 39),
	(40, 122, 'pbkdf2_sha256$720000$dy2M0njk4zokEXLpPL2baA$1KM75lXwqRmOA7293sRzM3AIVasTGaIhlFpR57b1AfI=', '2024-01-30 17:49:04.168935', 0, 'lujana_313', 'Lujana', 'Bajracharya', 'lujana@gmail.com', 0, 1, NULL, NULL, '1234512345', NULL, NULL, NULL, 'staff', 1, 39),
	(41, 0, 'pbkdf2_sha256$720000$Gc810K5WGUMnhUwb4EbxCH$gqfgpNJ0dnFxW16MN2WX9P6C70BLbqK4wrdPwaaHOVM=', NULL, 0, 'dhiraj', 'Dhiraj', 'Shah', 'dhiraj@gmail.com', 0, 1, '2024-01-31 04:54:37.741725', NULL, '', NULL, NULL, NULL, 'admin', 1, NULL);

-- Dumping structure for table ofs.app_ofs_customuser_groups
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

-- Dumping data for table ofs.app_ofs_customuser_groups: ~0 rows (approximately)

-- Dumping structure for table ofs.app_ofs_customuser_user_permissions
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

-- Dumping data for table ofs.app_ofs_customuser_user_permissions: ~0 rows (approximately)

-- Dumping structure for table ofs.app_ofs_products
CREATE TABLE IF NOT EXISTS `app_ofs_products` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `product_id` varchar(50) NOT NULL,
  `product_name` varchar(50) NOT NULL,
  `product_description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.app_ofs_products: ~0 rows (approximately)

-- Dumping structure for table ofs.app_ofs_salesdata
CREATE TABLE IF NOT EXISTS `app_ofs_salesdata` (
  `month` varchar(100) DEFAULT NULL,
  `sales` varchar(100) DEFAULT NULL,
  `id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.app_ofs_salesdata: ~0 rows (approximately)

-- Dumping structure for table ofs.auth_group
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.auth_group: ~0 rows (approximately)

-- Dumping structure for table ofs.auth_group_permissions
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

-- Dumping data for table ofs.auth_group_permissions: ~0 rows (approximately)

-- Dumping structure for table ofs.auth_permission
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.auth_permission: ~32 rows (approximately)
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
	(1, 'Can add log entry', 1, 'add_logentry'),
	(2, 'Can change log entry', 1, 'change_logentry'),
	(3, 'Can delete log entry', 1, 'delete_logentry'),
	(4, 'Can view log entry', 1, 'view_logentry'),
	(5, 'Can add permission', 2, 'add_permission'),
	(6, 'Can change permission', 2, 'change_permission'),
	(7, 'Can delete permission', 2, 'delete_permission'),
	(8, 'Can view permission', 2, 'view_permission'),
	(9, 'Can add group', 3, 'add_group'),
	(10, 'Can change group', 3, 'change_group'),
	(11, 'Can delete group', 3, 'delete_group'),
	(12, 'Can view group', 3, 'view_group'),
	(13, 'Can add content type', 4, 'add_contenttype'),
	(14, 'Can change content type', 4, 'change_contenttype'),
	(15, 'Can delete content type', 4, 'delete_contenttype'),
	(16, 'Can view content type', 4, 'view_contenttype'),
	(17, 'Can add session', 5, 'add_session'),
	(18, 'Can change session', 5, 'change_session'),
	(19, 'Can delete session', 5, 'delete_session'),
	(20, 'Can view session', 5, 'view_session'),
	(21, 'Can add user', 6, 'add_customuser'),
	(22, 'Can change user', 6, 'change_customuser'),
	(23, 'Can delete user', 6, 'delete_customuser'),
	(24, 'Can view user', 6, 'view_customuser'),
	(25, 'Can add category', 7, 'add_category'),
	(26, 'Can change category', 7, 'change_category'),
	(27, 'Can delete category', 7, 'delete_category'),
	(28, 'Can view category', 7, 'view_category'),
	(29, 'Can add products', 8, 'add_products'),
	(30, 'Can change products', 8, 'change_products'),
	(31, 'Can delete products', 8, 'delete_products'),
	(32, 'Can view products', 8, 'view_products');

-- Dumping structure for table ofs.category_info
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
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.category_info: ~9 rows (approximately)
INSERT INTO `category_info` (`id`, `category_id`, `category`, `updated_on`, `userid`) VALUES
	(31, '1776', 'Cards', '2024-01-30 14:17:09', 28),
	(32, '8794', 'Box', '2024-01-30 14:17:26', 28),
	(33, '2715', 'Banner', '2024-01-30 14:19:53', 28),
	(34, '7676', 'Bags', '2024-01-30 14:20:04', 28),
	(35, '3581', 'Books', '2024-01-30 14:54:52', 28),
	(36, '3630', 'tape', '2024-01-30 23:27:11', 39),
	(37, '6045', 'Copy', '2024-01-30 23:58:13', 39),
	(38, '9919', 'Pen', '2024-01-31 10:15:35', 28),
	(39, '1367', 'test', '2024-01-31 10:42:04', 28);

-- Dumping structure for table ofs.django_admin_log
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

-- Dumping data for table ofs.django_admin_log: ~0 rows (approximately)

-- Dumping structure for table ofs.django_content_type
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.django_content_type: ~8 rows (approximately)
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
	(1, 'admin', 'logentry'),
	(7, 'app_ofs', 'category'),
	(6, 'app_ofs', 'customuser'),
	(8, 'app_ofs', 'products'),
	(3, 'auth', 'group'),
	(2, 'auth', 'permission'),
	(4, 'contenttypes', 'contenttype'),
	(5, 'sessions', 'session');

-- Dumping structure for table ofs.django_migrations
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.django_migrations: ~20 rows (approximately)
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
	(1, 'contenttypes', '0001_initial', '2023-10-02 05:14:53.371035'),
	(2, 'contenttypes', '0002_remove_content_type_name', '2023-10-02 05:14:53.423686'),
	(3, 'auth', '0001_initial', '2023-10-02 05:14:53.580286'),
	(4, 'auth', '0002_alter_permission_name_max_length', '2023-10-02 05:14:53.614464'),
	(5, 'auth', '0003_alter_user_email_max_length', '2023-10-02 05:14:53.619424'),
	(6, 'auth', '0004_alter_user_username_opts', '2023-10-02 05:14:53.624666'),
	(7, 'auth', '0005_alter_user_last_login_null', '2023-10-02 05:14:53.629667'),
	(8, 'auth', '0006_require_contenttypes_0002', '2023-10-02 05:14:53.632792'),
	(9, 'auth', '0007_alter_validators_add_error_messages', '2023-10-02 05:14:53.639412'),
	(10, 'auth', '0008_alter_user_username_max_length', '2023-10-02 05:14:53.644433'),
	(11, 'auth', '0009_alter_user_last_name_max_length', '2023-10-02 05:14:53.650691'),
	(12, 'auth', '0010_alter_group_name_max_length', '2023-10-02 05:14:53.674384'),
	(13, 'auth', '0011_update_proxy_permissions', '2023-10-02 05:14:53.680363'),
	(14, 'auth', '0012_alter_user_first_name_max_length', '2023-10-02 05:14:53.688318'),
	(15, 'app_ofs', '0001_initial', '2023-10-02 05:14:53.880777'),
	(16, 'admin', '0001_initial', '2023-10-02 05:14:53.960827'),
	(17, 'admin', '0002_logentry_remove_auto_add', '2023-10-02 05:14:53.966690'),
	(18, 'admin', '0003_logentry_add_action_flag_choices', '2023-10-02 05:14:53.974078'),
	(19, 'sessions', '0001_initial', '2023-10-02 05:14:54.014377'),
	(20, 'app_ofs', '0002_category_products', '2023-10-12 09:57:52.989625');

-- Dumping structure for table ofs.django_session
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.django_session: ~17 rows (approximately)
INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
	('274fagsplp2fcm62ug92g8kkif8z0h1q', '.eJxVjEEOwiAQRe_C2hA6IDAu3fcMZIBBqoYmpV0Z765NutDtf-_9lwi0rTVsnZcwZXERGsXpd4yUHtx2ku_UbrNMc1uXKcpdkQftcpwzP6-H-3dQqddvPQBnjAkJvcrWgonGko6D0cRACpwrCiMWgrNnLgwGnNeWTUZlmEG8Pw0cOBE:1rUzmo:Cndh9z9uYQ_xWWaLJq95r_Gq_Qy9IqD_Hdki20PNTBo', '2024-02-14 01:53:10.907107'),
	('6zq89pu786kt6d9cohzu9sm9u1hdlalj', '.eJxVjEEOwiAQRe_C2hBAKNSle89ApjODVA0kpV0Z7y5NutDte-__t4iwrTlujZc4k7gI7cXpF06ATy67oQeUe5VYy7rMk9wTedgmb5X4dT3av4MMLfe1t6goUNCoNCM640YL5Iyx4I3zAycYA1pSwOjPXnNKPWbQCjvnQXy-D2U4mw:1rFchq:Go4e07Ey0Teeb2KhtiH2Ipol6WZcBPR_SEbIiRf124o', '2024-01-02 16:12:30.088037'),
	('9b443vdhs9r4ns1ylq44i6c4k6udctkf', '.eJxVjEsOAiEQBe_C2hBspAGX7j3DpKEbGTWQzGdlvLtOMgvdvqp6LzXQutRhnWUaRlZnBUEdfsdE-SFtI3yndus697ZMY9Kbonc662tneV529--g0ly_dTHAOVu0ACaKDwjuFCmZAOjFcTZMUaxEsj6xpVigRHQoR0B0xqJ6fwD-BTeG:1rV2dW:YZz8kJA9iQ3ox6rKNxoUff3lViGgXrc9t-dV3OFlmME', '2024-02-14 04:55:46.106223'),
	('9g4jkhfelfgm9jvcdjsw7vhq5xs9vnyz', '.eJxVjEsOAiEQBe_C2hBspAGX7j3DpKEbGTWQzGdlvLtOMgvdvqp6LzXQutRhnWUaRlZnBUEdfsdE-SFtI3yndus697ZMY9Kbonc662tneV529--g0ly_dTHAOVu0ACaKDwjuFCmZAOjFcTZMUaxEsj6xpVigRHQoR0B0xqJ6fwD-BTeG:1rV2BE:oiq8pHl50TCF3Myh8z3qC_imv47mLbAwqVnrZfLnlA0', '2024-02-14 04:26:32.245237'),
	('bnsq0c36hfvbm9zgv4erftvpbdlmpr2e', '.eJxVjDsOwyAQBe9CHSEWDJiU6X0GxGc3OIlAMnYV5e6xJRdJOzPvvZkP21r81nHxc2ZXBuzyy2JIT6yHyI9Q742nVtdljvxI-Gk7n1rG1-1s_w5K6GVfu5hMlDKRUINzEEgBOp0JQEuhR2VxEBl2bgWRiToQylGCwWSUNmTZ5wvaeTeg:1r4wcO:aFTIxqa686fVkZf3eWSf9vVa4mXSrmdpDoxFkHjCs_c', '2023-12-04 05:14:44.933104'),
	('fcckucwb9fwwzo7m2y4e1yktyslpydgk', '.eJxVjEsOwjAMBe-SNYrquElaluw5Q-TENimgVupnhbg7VOoCtm9m3ssk2taatkXmNLA5G4jm9DtmKg8Zd8J3Gm-TLdO4zkO2u2IPutjrxPK8HO7fQaWlfmtU1CY6JB-csPri2QWJgAgM0GTCSLEvKsigrrTic5tLHxrVDgJ35v0BC5A4YA:1rEViH:CI17TcuWR-myOWbeqRCFKA90BJh4-0g8NAtHRIvSr2c', '2023-12-30 14:32:21.999029'),
	('hiqdm2b95v72msx8gutvbxox4rp0zlg7', '.eJxVjEsOwjAMBe-SNYrquElaluw5Q-TENimgVupnhbg7VOoCtm9m3ssk2taatkXmNLA5G4jm9DtmKg8Zd8J3Gm-TLdO4zkO2u2IPutjrxPK8HO7fQaWlfmtU1CY6JB-csPri2QWJgAgM0GTCSLEvKsigrrTic5tLHxrVDgJ35v0BC5A4YA:1rD4GP:j9N_4O0CUEorBlu4DU4mJChRnm4uG0yE7Py5E9EvfZg', '2023-12-26 15:01:37.652954'),
	('hzlw8ixuj53bci77mq217vaemntc993u', '.eJxVjEEOwiAQRe_C2hA6IDAu3fcMZIBBqoYmpV0Z765NutDtf-_9lwi0rTVsnZcwZXERGsXpd4yUHtx2ku_UbrNMc1uXKcpdkQftcpwzP6-H-3dQqddvPQBnjAkJvcrWgonGko6D0cRACpwrCiMWgrNnLgwGnNeWTUZlmEG8Pw0cOBE:1rUsam:LkZHp5ApKWPi30czXllbIJZYYorT6yXT6183s_g9i2M', '2024-02-13 18:12:16.321391'),
	('keikphgkfgzqrydh0f8ub2603aa8y1zt', 'e30:1rFcWp:-8J28BtYzKmf6nHikkpqhMfbcjK0JtErbgIqZ1KyF1E', '2024-01-02 16:01:07.460288'),
	('o6j2mei04pxh8ymi1806o4cgx4pu1bbt', '.eJxVjEsOwjAMBe-SNYrquElaluw5Q-TENimgVupnhbg7VOoCtm9m3ssk2taatkXmNLA5G4jm9DtmKg8Zd8J3Gm-TLdO4zkO2u2IPutjrxPK8HO7fQaWlfmtU1CY6JB-csPri2QWJgAgM0GTCSLEvKsigrrTic5tLHxrVDgJ35v0BC5A4YA:1rCeBa:wRWrX6Gqu3Jw368E9SkCUIyMsrzcsayj3mMs71kKC9M', '2023-12-25 11:10:54.962076'),
	('p5xu0hvekmf2dx2b6bhyxtb7bclksjzh', '.eJxVjEEOwiAQRe_C2hBAKNSle89ApjODVA0kpV0Z7y5NutDte-__t4iwrTlujZc4k7gI7cXpF06ATy67oQeUe5VYy7rMk9wTedgmb5X4dT3av4MMLfe1t6goUNCoNCM640YL5Iyx4I3zAycYA1pSwOjPXnNKPWbQCjvnQXy-D2U4mw:1rFyDn:LdV2AD9DUvg2DhKsoymP06AEYrYO6trpO_LzUy-DGnQ', '2024-01-03 15:10:55.012619'),
	('prdm6zw2t4iwncshx8f7iqhaqcvtf38n', '.eJxVjDsOwjAQBe_iGlng364p6XMGa-21cQA5UpxUiLuTSCmgfTPz3iLQutSw9jyHkcVVXECcfsdI6ZnbTvhB7T7JNLVlHqPcFXnQLoeJ8-t2uH8HlXrdas8KCxhtzdZkx4YMKI3FRI_IrJICZJ0AVXbWAeoYqZB12sO5KO3F5wsIlzfO:1rGRH4:h_ZoDNQD-GQrowT7AIdtG_cSNOjCjMUBCdcl9pHkR7Q', '2024-01-04 22:12:14.495554'),
	('vzn2toyc48n60rpyx89hz1xi3m3u1skf', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1qpo7Z:6LsgfB9fL3FPCyxFxB31OmERhDfrjcSvpahbw20O6F8', '2023-10-23 11:08:21.389702'),
	('wxdwsnzk3eb8ferm2ys63nu2pmkit1uy', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1quSTF:onsWLaFr0u0OoXliouFPRmz6xQPLW5bSw_R1jybxXOo', '2023-11-05 07:01:57.910094'),
	('xpx6kae5ezbay9wjupxe41ke85s9o2it', '.eJxVjEEOwiAQRe_C2hA6IDAu3fcMZIBBqoYmpV0Z765NutDtf-_9lwi0rTVsnZcwZXERGsXpd4yUHtx2ku_UbrNMc1uXKcpdkQftcpwzP6-H-3dQqddvPQBnjAkJvcrWgonGko6D0cRACpwrCiMWgrNnLgwGnNeWTUZlmEG8Pw0cOBE:1rV1q3:Kg-oYaKZvO3GkDfrOzYoIy5gDi6Y2r1bEZcXDKxOnm0', '2024-02-14 04:04:39.471119'),
	('xzb13zmuzmat8ur4vxc50jllw1lq35ia', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1qpQpx:-R0TkGVjg1nycIvEAVYQK8LS1VF090bTiN3jSaUP-Sk', '2023-10-22 10:16:37.523625'),
	('yxepyc8xwpjtr9y4r2sfxaennq3wbtfs', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1qrVLj:dhdgS-vg6dEGpcleh7wszChmZ5NuA8CyZdi4bPr4jpU', '2023-10-28 03:29:59.319899'),
	('zjcb5e71xuf7dbiwdh4mp6tp9j0hf0eq', '.eJxVjEEOwiAQRe_C2hBAKNSle89ApjODVA0kpV0Z7y5NutDte-__t4iwrTlujZc4k7gI7cXpF06ATy67oQeUe5VYy7rMk9wTedgmb5X4dT3av4MMLfe1t6goUNCoNCM640YL5Iyx4I3zAycYA1pSwOjPXnNKPWbQCjvnQXy-D2U4mw:1rFGXe:YLdn7gGDIPZZW_wEYvL7vwdvY2tyMMJe1YQBKksWg3M', '2024-01-01 16:32:30.733053');

-- Dumping structure for table ofs.forecast_data
CREATE TABLE IF NOT EXISTS `forecast_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` varchar(50) NOT NULL DEFAULT '',
  `quantity` bigint(20) NOT NULL DEFAULT 0,
  `ordered_date` date NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.forecast_data: ~1 rows (approximately)
INSERT INTO `forecast_data` (`id`, `product_id`, `quantity`, `ordered_date`, `user_id`) VALUES
	(1, '123', 10, '2024-01-25', NULL),
	(2, '123', 12, '2024-01-26', NULL);

-- Dumping structure for table ofs.inventorydetails_date
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
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.inventorydetails_date: ~12 rows (approximately)
INSERT INTO `inventorydetails_date` (`id`, `date`, `quantity`, `product_id`, `user_id`, `price`) VALUES
	(21, '2024-01-25', '24', '18027', 28, '10'),
	(22, '2024-01-25', '12', '18760', 28, '30'),
	(23, '2024-01-25', '13', '19707', 28, '44'),
	(24, '2024-01-25', '23', '19714', 28, '22'),
	(25, '2024-01-25', '12', '13613', 28, '44'),
	(26, '2024-01-30', '36', '18027', 28, '44'),
	(27, '2024-01-30', '12', '18760', 28, '15'),
	(28, '2024-01-30', '12', '19707', 28, '44'),
	(29, '2024-01-30', '122', '19714', 28, '12'),
	(30, '2024-01-30', '200', '19437', 39, '1333'),
	(31, '2024-01-31', '24', '19437', 39, '44'),
	(32, '2024-01-31', '22', '18027', 28, '22');

-- Dumping structure for table ofs.inventory_details
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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.inventory_details: ~6 rows (approximately)
INSERT INTO `inventory_details` (`inventory_id`, `quantity`, `price`, `productid`, `categoryid`, `userid`) VALUES
	(45, '58', '22', '18027', NULL, 28),
	(46, '12', '30', '18760', NULL, 28),
	(47, '13', '44', '19707', NULL, 28),
	(48, '23', '22', '19714', NULL, 28),
	(49, '12', '44', '13613', NULL, 28),
	(50, '212', '44', '19437', NULL, 39);

-- Dumping structure for table ofs.logs
CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `description` varchar(50) DEFAULT NULL,
  `logged_on` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=248 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.logs: ~25 rows (approximately)
INSERT INTO `logs` (`id`, `username`, `ip`, `description`, `logged_on`) VALUES
	(216, 'lbaj', '127.0.0.1', 'logged in', '2024-01-30 14:08:46'),
	(217, 'lbaj', '127.0.0.1', 'logged in', '2024-01-30 14:16:34'),
	(218, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:28:37'),
	(219, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:29:01'),
	(220, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:30:49'),
	(221, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:31:04'),
	(222, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:31:22'),
	(223, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:31:27'),
	(224, 'manoj_183', '127.0.0.1', 'Incorrect username/password', '2024-01-30 22:33:50'),
	(225, 'manoj_183', '127.0.0.1', 'logged in', '2024-01-30 22:34:48'),
	(226, 'lbaj', '127.0.0.1', 'logged in', '2024-01-30 23:02:43'),
	(227, 'manoj_375', '127.0.0.1', 'Incorrect username/password', '2024-01-30 23:04:18'),
	(228, 'manoj_375', '127.0.0.1', 'Incorrect username/password', '2024-01-30 23:04:27'),
	(229, 'manoj_375', '127.0.0.1', 'logged in', '2024-01-30 23:04:52'),
	(230, 'nimiP', '127.0.0.1', 'logged in', '2024-01-30 23:18:42'),
	(231, 'lujana_313', '127.0.0.1', 'Incorrect username/password', '2024-01-30 23:28:14'),
	(232, 'lujana_313', '127.0.0.1', 'Incorrect username/password', '2024-01-30 23:28:38'),
	(233, 'lujana_313', '127.0.0.1', 'Incorrect username/password', '2024-01-30 23:28:57'),
	(234, 'lujana_313', '127.0.0.1', 'logged in', '2024-01-30 23:29:31'),
	(235, 'nimiP', '127.0.0.1', 'logged in', '2024-01-30 23:32:30'),
	(236, 'lujana_313', '127.0.0.1', 'logged in', '2024-01-30 23:32:48'),
	(237, 'nimiP', '127.0.0.1', 'logged in', '2024-01-30 23:32:56'),
	(238, 'lujana_313', '127.0.0.1', 'logged in', '2024-01-30 23:34:04'),
	(239, 'nimiP', '127.0.0.1', 'logged in', '2024-01-30 23:36:25'),
	(240, 'nimiP', '127.0.0.1', 'logged in', '2024-01-30 23:56:31'),
	(241, 'nimiP', '127.0.0.1', 'Incorrect username/password', '2024-01-30 23:57:10'),
	(242, 'nimiP', '127.0.0.1', 'logged in', '2024-01-30 23:57:16'),
	(243, 'nimiP', '127.0.0.1', 'logged in', '2024-01-31 01:21:56'),
	(244, 'nimiP', '127.0.0.1', 'logged in', '2024-01-31 07:38:10'),
	(245, 'nimiP', '127.0.0.1', 'logged in', '2024-01-31 09:49:39'),
	(246, 'lbaj', '127.0.0.1', 'logged in', '2024-01-31 10:11:32'),
	(247, 'lbaj', '127.0.0.1', 'logged in', '2024-01-31 10:40:46');

-- Dumping structure for table ofs.order_info
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
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.order_info: ~7 rows (approximately)
INSERT INTO `order_info` (`id`, `order_id`, `quantity`, `ordered_date`, `delivery_date`, `price`, `status`, `productid`, `userid`, `total_price`, `date`) VALUES
	(88, '1152', '12', '2024-01-30', '2024-01-31', '44', 'Ongoing', '18027', 28, '528', '2024-01-30 00:00:00'),
	(89, '1072', '12', '2024-01-31', '2024-02-01', '44', 'Ongoing', '19707', 28, '528', '2024-01-30 00:00:00'),
	(90, '1591', '23', '2024-01-25', '2024-01-30', '10', 'Pending', '18027', 28, '230', '2024-01-30 00:00:00'),
	(91, '1348', '12', '2024-01-27', '2024-01-31', '10', 'Ongoing', '18027', 28, '120', '2024-01-30 00:00:00'),
	(92, '1162', '12', '2024-01-18', '2024-01-31', '0', 'Ongoing', '19437', 39, '0', '2024-01-30 00:00:00'),
	(93, '1718', '12', '2024-01-31', '2024-02-01', '44', 'Ongoing', '19437', 39, '528', '2024-01-31 00:00:00'),
	(94, '1565', '12', '2024-01-29', '2024-01-30', '22', 'Pending', '18027', 28, '264', '2024-01-31 00:00:00');

-- Dumping structure for table ofs.product_info
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
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.product_info: ~17 rows (approximately)
INSERT INTO `product_info` (`id`, `product_id`, `product_name`, `product_description`, `category`, `userid`) VALUES
	(68, '18027', 'Wedding Card', 'Wedding Card', '1776', 28),
	(69, '18760', 'Visiting Cards', 'Visiting Card\r\n', '1776', 28),
	(70, '19707', 'Birthday Cards', 'Birthday Cards', '1776', 28),
	(71, '19714', 'Business Cards', 'Business Cards', '1776', 28),
	(72, '19236', 'White Box  (12cm *12cm)', 'White Box  (12cm *12cm)', '8794', 28),
	(73, '19018', 'White Box (20cm*20cm)', 'White Box (20cm*20cm)', '8794', 28),
	(74, '12207', 'Red Box (20cm*20cm)', 'Red Box (20cm*20cm)', '8794', 28),
	(75, '16540', 'Red Box (13cm*20cm)', 'Red Box (13cm*20cm)', '8794', 28),
	(76, '13613', 'Nepali Paper Cards', 'Nepali Paper Cards', '1776', 28),
	(77, '16111', 'HIgh Quality Flex Banner', 'HIgh Quality Flex Banner', '2715', 28),
	(78, '12084', 'Medium Quality Flex Banner', 'Medium Quality Flex Banner', '2715', 28),
	(79, '15061', 'Low Quality Flex Banner', 'Low Quality Flex Banner', '2715', 28),
	(80, '15597', 'Large Low Quality Bag', 'Large Low Quality Bag', '7676', 28),
	(82, '15965', 'Large High Quality Bags', 'Large High Quality Bags', '7676', 28),
	(84, '19437', 'testt', 'test', '3630', 39),
	(86, '16903', 'red copy', 'w', '3630', 39),
	(87, '15399', 'Red Pen', 'Red Pen\r\n', '9919', 28);

-- Dumping structure for table ofs.user_verify
CREATE TABLE IF NOT EXISTS `user_verify` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email` varchar(50) NOT NULL,
  `otp_sent` varchar(50) NOT NULL,
  `otp_inserted` varchar(50) NOT NULL,
  `otp_verified` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.user_verify: ~0 rows (approximately)

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
