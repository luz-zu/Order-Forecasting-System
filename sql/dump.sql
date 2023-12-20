-- --------------------------------------------------------
-- Host:                         182.93.85.68
-- Server version:               10.11.4-MariaDB-1~deb12u1 - Debian 12
-- Server OS:                    debian-linux-gnu
-- HeidiSQL Version:             12.6.0.6765
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.app_ofs_customuser: ~16 rows (approximately)
INSERT INTO `app_ofs_customuser` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `dob`, `phone_number`, `otp`, `otp_created_at`, `otp_verified`, `userrole`, `first_login`) VALUES
	(1, 'pbkdf2_sha256$600000$FvZ4s7uyhmbbGO548RVcA1$E1RQy6vxghpNNEI9OgFRuWWJ6T9ACcOnJZhVQASLALU=', '2023-11-30 23:03:55.592952', 0, 'lujana', 'Lujana', 'Bajracharya', 'lujanaba@gmail.com', 0, 1, '2023-10-02 05:16:26.819802', NULL, 'Bajracharya', '302056', '2023-12-09 07:45:24.028841', '1', 'admin', 1),
	(2, 'pbkdf2_sha256$600000$WthacnDhgIRp1k5ZiN5zy1$DahRT3urUlVMa42vp59CN02EtXsYfGEZKjVmD5nshB0=', '2023-11-23 08:18:30.112592', 0, 'sajna', 'Sajana', 'Bajra', 'sajanabaj31@gmail.com', 0, 1, '2023-10-03 03:35:40.204047', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(3, 'pbkdf2_sha256$600000$OCl7jH1sXA1dUwbHAYeVla$rANVxvEN1ai2LAjGOD5AUJXYeo0d9iPbFkYeW1eZXr4=', '2023-11-08 16:29:31.716838', 0, 'luzzu', 'Lujana', 'Bajracharya', 'manojgamer99@gmail.com', 0, 1, '2023-11-08 16:29:31.432950', NULL, '', '158847', '2023-11-20 05:41:47.449347', NULL, 'admin', 1),
	(4, 'pbkdf2_sha256$600000$aElDEon457bSye6Xgta4oG$p2s+szO3p5vhQe6c1EMiNzzuX6NTXpdlIWdKyFnXs60=', '2023-11-20 12:33:08.722779', 0, 'luniva', 'Luniva', 'Bajracharya', 'bajraluni@gmail.com', 0, 1, '2023-11-20 12:31:03.213386', NULL, '', '668955', '2023-11-20 12:55:22.564788', '1', 'admin', 1),
	(5, 'pbkdf2_sha256$600000$ZeDKmbMCrDN1tuDYKgB9kW$Eks7caUlfS6Ir2JFrKaNomrntiXMQbyeBEP74w0H68A=', '2023-11-23 17:24:30.706824', 0, 'manoj', 'manoj', 'karki', 'manojgamer99@gmail.com', 0, 1, '2023-11-23 17:24:30.463945', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(6, 'pbkdf2_sha256$600000$EiSxUx4EEpZLq4ZcFXjQdp$UuQzVFe8ZTkLIBbKTrJJqnK/q/PtcT/rFEdAldfaYCQ=', '2023-11-23 17:27:00.953791', 0, 'luni', 'Luniva', 'Bajra', 'bajraluni@gmail.com', 0, 1, '2023-11-23 17:27:00.726398', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(7, 'pbkdf2_sha256$600000$pdO6FdLkybXBhVSpBYmuQI$YnUlw47xmp87lqw128FCbL8AdAJ94eMOXhUvtE6a5Zg=', '2023-11-25 13:14:45.804773', 0, 'sagina', 'Sagina', 'Maharjan', 'mjnsagina@gmail.com', 0, 1, '2023-11-25 13:14:45.571702', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(8, 'pbkdf2_sha256$600000$XJDAazMlm5hAyVdLludFMu$xVGmrzcokvLEI2O/xDvGuxAymplg20RXueI0bbXz/KQ=', NULL, 0, 'sagimjn', 'Sagina', 'Maharjan', 'mjnsagina@gmail.com', 0, 1, '2023-11-25 13:16:49.143018', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(9, 'pbkdf2_sha256$600000$7bgitgAeXaeuY5OUDXek1M$Rm4tIVS8yg7Bc15AIk3jC0cBGUbxx9Rp9jRng3mTZhc=', NULL, 0, 'sagimaharjan', 'Sagina', 'Maharjan', 'mjnsagina@gmail.com', 0, 1, '2023-11-25 13:18:53.332290', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(10, 'pbkdf2_sha256$600000$lj8RfFp8mhkPLCBs1fre8G$u+BaRmrIkxHR68hxMJjgeuQw+QEJqTKZ7Rp/fmhdRlk=', NULL, 0, 'madan', 'Madan', 'Karki', 'madan@gmail.com', 0, 1, '2023-11-25 13:35:47.991633', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(11, 'pbkdf2_sha256$600000$wJtMuwTkiCuVThUyfifEnW$Ht0Qal08jAEXeKCHIl9IaNwuGdjcDrzCktA7rbCIQyg=', NULL, 0, 'test', 'test', 'test', 'test@gmail.com', 0, 1, '2023-11-25 13:37:50.761713', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(12, 'pbkdf2_sha256$600000$CI27BgEt0aYyVFMHfEDte8$qtcMMx9OGjAen79YWNJNsetTZ89/avowCCrxybnS/bg=', NULL, 0, 'testing', 'test', 'test', 'testing@gmail.com', 0, 1, '2023-11-25 13:38:48.242855', NULL, '', NULL, NULL, NULL, 'admin', 1),
	(15, 'pbkdf2_sha256$600000$roDFR4yWM4cOjnQVjOxYCE$lX+z8mAqblGWhWdPpVGORTxHXV/l7IrsL9Pu1LuRz7Q=', '2023-12-07 13:09:44.386201', 0, 'luzzubaj', 'Lujana', 'Bajracharya', 'kk', 0, 1, '2023-12-07 08:19:45.553208', NULL, 'Bajracharya', NULL, NULL, NULL, 'admin', 1),
	(16, 'pbkdf2_sha256$600000$PJKQATxslIetbQbT0v0sbI$GqnzgSPj/4AcgLgreOKOHyCAvoivmCJ+hXiaFJXB96g=', '2023-12-07 20:14:20.286546', 0, 'manoj99', 'manoj', 'karki', 'manojgamer@gmail.com', 0, 1, '2023-12-07 20:10:09.636001', NULL, '9841147588', NULL, NULL, NULL, 'staff', 1),
	(17, 'pbkdf2_sha256$720000$Xoi4dQ9hpLHvCMs03BQ9U2$nzf1lalUN53eV6wTUlSDcfzpPSJG/m7/EDcir/VjVLM=', '2023-12-20 15:10:55.008105', 0, 'lbaj', 'Lujana', 'Bajracharya', 'lujanabajra@gmail.com', 0, 1, '2023-12-09 07:47:25.938782', NULL, '', '180120', '2023-12-11 11:10:05.136200', NULL, 'staff', 1),
	(23, 'pbkdf2_sha256$720000$mxe0Xh0bzkxMDPfH0eJWID$OtcNwAuQDGiT1ulQSIlK3wosxBmdwH3qKb31UJOCGCA=', NULL, 0, 'test_448', 'test', 'test2', 'test3@gmail.com', 0, 1, NULL, NULL, '1234567890', NULL, NULL, NULL, 'staff', 1);

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

-- Dumping data for table ofs.auth_permission: ~19 rows (approximately)
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
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.category_info: ~7 rows (approximately)
INSERT INTO `category_info` (`id`, `category_id`, `category`, `updated_on`, `userid`) VALUES
	(17, '9512', 'Book', '2023-12-09 14:22:35', 7),
	(18, '2550', 'Pen', '2023-12-09 14:22:56', 7),
	(19, '9700', 'Copy', '2023-12-09 14:23:02', 17),
	(20, '8285', 'Box', '2023-12-09 16:43:11', 17),
	(21, '7299', 'Test', '2023-12-09 16:56:29', 17),
	(22, '7087', 'Pen', '2023-12-09 16:56:43', 17),
	(23, '9915', 'Sketch', '2023-12-09 22:15:51', 17);

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

-- Dumping data for table ofs.django_session: ~12 rows (approximately)
INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
	('6zq89pu786kt6d9cohzu9sm9u1hdlalj', '.eJxVjEEOwiAQRe_C2hBAKNSle89ApjODVA0kpV0Z7y5NutDte-__t4iwrTlujZc4k7gI7cXpF06ATy67oQeUe5VYy7rMk9wTedgmb5X4dT3av4MMLfe1t6goUNCoNCM640YL5Iyx4I3zAycYA1pSwOjPXnNKPWbQCjvnQXy-D2U4mw:1rFchq:Go4e07Ey0Teeb2KhtiH2Ipol6WZcBPR_SEbIiRf124o', '2024-01-02 16:12:30.088037'),
	('bnsq0c36hfvbm9zgv4erftvpbdlmpr2e', '.eJxVjDsOwyAQBe9CHSEWDJiU6X0GxGc3OIlAMnYV5e6xJRdJOzPvvZkP21r81nHxc2ZXBuzyy2JIT6yHyI9Q742nVtdljvxI-Gk7n1rG1-1s_w5K6GVfu5hMlDKRUINzEEgBOp0JQEuhR2VxEBl2bgWRiToQylGCwWSUNmTZ5wvaeTeg:1r4wcO:aFTIxqa686fVkZf3eWSf9vVa4mXSrmdpDoxFkHjCs_c', '2023-12-04 05:14:44.933104'),
	('fcckucwb9fwwzo7m2y4e1yktyslpydgk', '.eJxVjEsOwjAMBe-SNYrquElaluw5Q-TENimgVupnhbg7VOoCtm9m3ssk2taatkXmNLA5G4jm9DtmKg8Zd8J3Gm-TLdO4zkO2u2IPutjrxPK8HO7fQaWlfmtU1CY6JB-csPri2QWJgAgM0GTCSLEvKsigrrTic5tLHxrVDgJ35v0BC5A4YA:1rEViH:CI17TcuWR-myOWbeqRCFKA90BJh4-0g8NAtHRIvSr2c', '2023-12-30 14:32:21.999029'),
	('hiqdm2b95v72msx8gutvbxox4rp0zlg7', '.eJxVjEsOwjAMBe-SNYrquElaluw5Q-TENimgVupnhbg7VOoCtm9m3ssk2taatkXmNLA5G4jm9DtmKg8Zd8J3Gm-TLdO4zkO2u2IPutjrxPK8HO7fQaWlfmtU1CY6JB-csPri2QWJgAgM0GTCSLEvKsigrrTic5tLHxrVDgJ35v0BC5A4YA:1rD4GP:j9N_4O0CUEorBlu4DU4mJChRnm4uG0yE7Py5E9EvfZg', '2023-12-26 15:01:37.652954'),
	('keikphgkfgzqrydh0f8ub2603aa8y1zt', 'e30:1rFcWp:-8J28BtYzKmf6nHikkpqhMfbcjK0JtErbgIqZ1KyF1E', '2024-01-02 16:01:07.460288'),
	('o6j2mei04pxh8ymi1806o4cgx4pu1bbt', '.eJxVjEsOwjAMBe-SNYrquElaluw5Q-TENimgVupnhbg7VOoCtm9m3ssk2taatkXmNLA5G4jm9DtmKg8Zd8J3Gm-TLdO4zkO2u2IPutjrxPK8HO7fQaWlfmtU1CY6JB-csPri2QWJgAgM0GTCSLEvKsigrrTic5tLHxrVDgJ35v0BC5A4YA:1rCeBa:wRWrX6Gqu3Jw368E9SkCUIyMsrzcsayj3mMs71kKC9M', '2023-12-25 11:10:54.962076'),
	('p5xu0hvekmf2dx2b6bhyxtb7bclksjzh', '.eJxVjEEOwiAQRe_C2hBAKNSle89ApjODVA0kpV0Z7y5NutDte-__t4iwrTlujZc4k7gI7cXpF06ATy67oQeUe5VYy7rMk9wTedgmb5X4dT3av4MMLfe1t6goUNCoNCM640YL5Iyx4I3zAycYA1pSwOjPXnNKPWbQCjvnQXy-D2U4mw:1rFyDn:LdV2AD9DUvg2DhKsoymP06AEYrYO6trpO_LzUy-DGnQ', '2024-01-03 15:10:55.012619'),
	('vzn2toyc48n60rpyx89hz1xi3m3u1skf', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1qpo7Z:6LsgfB9fL3FPCyxFxB31OmERhDfrjcSvpahbw20O6F8', '2023-10-23 11:08:21.389702'),
	('wxdwsnzk3eb8ferm2ys63nu2pmkit1uy', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1quSTF:onsWLaFr0u0OoXliouFPRmz6xQPLW5bSw_R1jybxXOo', '2023-11-05 07:01:57.910094'),
	('xzb13zmuzmat8ur4vxc50jllw1lq35ia', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1qpQpx:-R0TkGVjg1nycIvEAVYQK8LS1VF090bTiN3jSaUP-Sk', '2023-10-22 10:16:37.523625'),
	('yxepyc8xwpjtr9y4r2sfxaennq3wbtfs', '.eJxVjMsOwiAQRf-FtSG8GsCle7-BDMyMVA0kpV0Z_12bdKHbe865L5FgW2vaBi1pRnEWRpx-twzlQW0HeId267L0ti5zlrsiDzrktSM9L4f7d1Bh1G8N1jBByVpn0NpbpCkSARsXGLMKwGCRlYreeYPKTFQiGmB02fuCQbw_GVg5Qg:1qrVLj:dhdgS-vg6dEGpcleh7wszChmZ5NuA8CyZdi4bPr4jpU', '2023-10-28 03:29:59.319899'),
	('zjcb5e71xuf7dbiwdh4mp6tp9j0hf0eq', '.eJxVjEEOwiAQRe_C2hBAKNSle89ApjODVA0kpV0Z7y5NutDte-__t4iwrTlujZc4k7gI7cXpF06ATy67oQeUe5VYy7rMk9wTedgmb5X4dT3av4MMLfe1t6goUNCoNCM640YL5Iyx4I3zAycYA1pSwOjPXnNKPWbQCjvnQXy-D2U4mw:1rFGXe:YLdn7gGDIPZZW_wEYvL7vwdvY2tyMMJe1YQBKksWg3M', '2024-01-01 16:32:30.733053');

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
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.inventory_details: ~7 rows (approximately)
INSERT INTO `inventory_details` (`inventory_id`, `quantity`, `price`, `productid`, `categoryid`, `userid`) VALUES
	(23, '11', '10', '15283', '9512', NULL),
	(24, '2', '1', '16119', '9512', NULL),
	(25, '2', '1', '15192', '9512', NULL),
	(26, '2221212', '121', '12087', '2550', NULL),
	(27, '2', '1', '16119', '9512', 17),
	(28, '10', '121', '18858', '9700', 17),
	(29, '12', '21', '18858', NULL, NULL);

-- Dumping structure for table ofs.logs
CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `description` varchar(50) DEFAULT NULL,
  `logged_on` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=188 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.logs: ~186 rows (approximately)
INSERT INTO `logs` (`id`, `username`, `ip`, `description`, `logged_on`) VALUES
	(1, 'lujana', '127.0.0.1', 'logged in', '2023-10-02 11:07:16'),
	(2, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-10-02 11:14:32'),
	(3, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-10-02 11:15:17'),
	(4, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-02 19:47:38'),
	(5, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-02 19:47:43'),
	(6, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-02 19:47:49'),
	(7, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-02 19:47:51'),
	(8, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-10-03 07:26:26'),
	(9, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-03 09:19:45'),
	(10, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-10-03 09:19:56'),
	(11, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-10-03 09:20:04'),
	(12, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-10-03 09:20:14'),
	(13, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-03 09:20:22'),
	(14, 'sajana', '127.0.0.1', 'logged in', '2023-10-03 09:20:44'),
	(15, 'sajana', '127.0.0.1', 'logged in', '2023-10-03 09:35:47'),
	(16, 'sajana', '127.0.0.1', 'logged in', '2023-10-03 09:39:27'),
	(17, 'sajana', '127.0.0.1', 'logged in', '2023-10-05 21:33:27'),
	(18, 'sajana', '127.0.0.1', 'logged in', '2023-10-08 09:22:38'),
	(19, 'sajana', '127.0.0.1', 'logged in', '2023-10-08 16:01:37'),
	(20, 'sajana', '127.0.0.1', 'logged in', '2023-10-09 09:40:37'),
	(21, 'sajana', '127.0.0.1', 'logged in', '2023-10-09 10:08:36'),
	(22, 'sajana', '127.0.0.1', 'logged in', '2023-10-09 16:30:23'),
	(23, 'sajana', '127.0.0.1', 'logged in', '2023-10-09 16:53:21'),
	(24, 'sajana', '127.0.0.1', 'logged in', '2023-10-12 14:43:53'),
	(25, 'sajana', '127.0.0.1', 'logged in', '2023-10-12 15:22:01'),
	(26, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-10-12 15:41:50'),
	(27, 'sajana', '127.0.0.1', 'logged in', '2023-10-12 15:41:59'),
	(28, 'sajana', '127.0.0.1', 'logged in', '2023-10-12 17:24:56'),
	(29, 'sajana', '127.0.0.1', 'logged in', '2023-10-12 17:25:31'),
	(30, 'sajana', '127.0.0.1', 'logged in', '2023-10-13 07:07:14'),
	(31, 'sajana', '127.0.0.1', 'logged in', '2023-10-13 07:30:30'),
	(32, 'sajana', '127.0.0.1', 'logged in', '2023-10-14 09:14:59'),
	(33, 'sajana', '127.0.0.1', 'logged in', '2023-10-14 13:55:57'),
	(34, 'sajana', '127.0.0.1', 'logged in', '2023-10-22 12:46:57'),
	(35, 'sajana', '127.0.0.1', 'logged in', '2023-11-08 21:03:46'),
	(36, 'sajana', '127.0.0.1', 'logged in', '2023-11-08 21:19:31'),
	(37, 'sajana', '127.0.0.1', 'logged in', '2023-11-08 21:19:44'),
	(38, 'sajana', '127.0.0.1', 'logged in', '2023-11-08 21:33:05'),
	(39, 'sajana', '127.0.0.1', 'logged in', '2023-11-18 21:57:20'),
	(40, 'sajana', '127.0.0.1', 'logged in', '2023-11-18 22:17:46'),
	(41, 'sajana', '127.0.0.1', 'logged in', '2023-11-19 17:36:55'),
	(42, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-20 10:59:22'),
	(43, 'lujanabajra@gmail.com', '127.0.0.1', 'Incorrect username/password', '2023-11-20 10:59:39'),
	(44, 'lujana', '127.0.0.1', 'logged in', '2023-11-20 10:59:44'),
	(45, 'bajraluni@gmail.com', '127.0.0.1', 'Incorrect username/password', '2023-11-20 18:17:12'),
	(46, 'bajraluni@gmail.com', '127.0.0.1', 'Incorrect username/password', '2023-11-20 18:17:23'),
	(47, 'bajraluni@gmail.com', '127.0.0.1', 'Incorrect username/password', '2023-11-20 18:18:02'),
	(48, 'luniva', '127.0.0.1', 'logged in', '2023-11-20 18:18:08'),
	(49, 'sajana', '127.0.0.1', 'logged in', '2023-11-20 20:38:44'),
	(50, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-21 21:00:00'),
	(51, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-21 21:00:24'),
	(52, 'sajana', '127.0.0.1', 'logged in', '2023-11-21 21:00:31'),
	(53, 'sajana', '127.0.0.1', 'logged in', '2023-11-21 21:22:18'),
	(54, 'sajana', '127.0.0.1', 'logged in', '2023-11-21 22:40:57'),
	(55, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 13:55:59'),
	(56, 'sajana', '127.0.0.1', 'logged in', '2023-11-23 13:56:07'),
	(57, 'sajana', '127.0.0.1', 'logged in', '2023-11-23 14:01:54'),
	(58, 'sajana', '127.0.0.1', 'logged in', '2023-11-23 14:03:30'),
	(59, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:29:50'),
	(60, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:29:57'),
	(61, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:30:06'),
	(62, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:30:13'),
	(63, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:30:20'),
	(64, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:30:27'),
	(65, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:30:32'),
	(66, 'luzzu', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:31:41'),
	(67, 'luzzu', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:31:50'),
	(68, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 22:32:13'),
	(69, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 22:49:34'),
	(70, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 22:52:40'),
	(71, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:53:18'),
	(72, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 22:53:26'),
	(73, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:54:42'),
	(74, 'test', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:54:48'),
	(75, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 22:54:57'),
	(76, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:55:34'),
	(77, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:55:40'),
	(78, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-23 22:55:48'),
	(79, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 22:55:57'),
	(80, 'lujana', '127.0.0.1', 'logged in', '2023-11-23 23:18:16'),
	(81, 'lujana', '127.0.0.1', 'logged in', '2023-11-24 09:39:37'),
	(82, 'lujana', '127.0.0.1', 'logged in', '2023-11-24 10:03:42'),
	(83, 'lujana', '127.0.0.1', 'logged in', '2023-11-24 21:59:15'),
	(84, 'lujana', '127.0.0.1', 'logged in', '2023-11-24 22:14:04'),
	(85, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-25 17:50:11'),
	(86, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 17:50:26'),
	(87, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 21:42:21'),
	(88, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 21:48:54'),
	(89, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 21:51:12'),
	(90, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 21:57:23'),
	(91, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:00:49'),
	(92, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:02:49'),
	(93, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:03:08'),
	(94, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:17:09'),
	(95, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:44:01'),
	(96, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:48:02'),
	(97, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:48:50'),
	(98, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:51:51'),
	(99, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-25 22:54:28'),
	(100, 'lujana', '127.0.0.1', 'logged in', '2023-11-25 22:54:34'),
	(101, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:09:36'),
	(102, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:27:09'),
	(103, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:42:41'),
	(104, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:44:07'),
	(105, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:45:25'),
	(106, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:48:47'),
	(107, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:51:27'),
	(108, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:56:36'),
	(109, 'lujana', '127.0.0.1', 'logged in', '2023-11-26 10:57:27'),
	(110, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:27:10'),
	(111, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:27:20'),
	(112, 'lujana1234', '127.0.0.1', 'logged in', '2023-11-30 17:29:19'),
	(113, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:31:27'),
	(114, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:31:34'),
	(115, 'lujana1234', '127.0.0.1', 'logged in', '2023-11-30 17:31:52'),
	(116, 'lujana1234', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:32:09'),
	(117, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:32:18'),
	(118, 'lujana1234', '127.0.0.1', 'logged in', '2023-11-30 17:32:26'),
	(119, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:36:03'),
	(120, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:36:09'),
	(121, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:36:20'),
	(122, 'lujana1234', '127.0.0.1', 'logged in', '2023-11-30 17:36:27'),
	(123, 'lujana1234', '127.0.0.1', 'logged in', '2023-11-30 17:38:27'),
	(124, 'lujana1234', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:39:57'),
	(125, 'lujana1234', '127.0.0.1', 'logged in', '2023-11-30 17:40:06'),
	(126, 'lujana1234', '127.0.0.1', 'Incorrect username/password', '2023-11-30 17:43:39'),
	(127, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:46:38'),
	(128, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:46:48'),
	(129, 'lujana1234', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:46:57'),
	(130, 'lujana1234', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:47:05'),
	(131, 'lujana123422212', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:48:49'),
	(132, 'lujana123422212', '127.0.0.1', 'logged in', '2023-12-01 04:48:55'),
	(133, 'lujana123', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:51:59'),
	(134, 'lujana1234', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:52:41'),
	(135, 'lujana123', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:52:54'),
	(136, 'lujana123', '127.0.0.1', 'Incorrect username/password', '2023-12-01 04:54:00'),
	(137, 'luzzu', '127.0.0.1', 'Incorrect username/password', '2023-12-07 14:05:07'),
	(138, 'luzzubaj', '127.0.0.1', 'logged in', '2023-12-07 14:05:18'),
	(139, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-07 18:54:19'),
	(140, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-07 18:54:31'),
	(141, 'luzzubaj', '127.0.0.1', 'logged in', '2023-12-07 18:54:44'),
	(142, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-08 01:27:59'),
	(143, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-12-08 01:54:49'),
	(144, 'manoj99', '127.0.0.1', 'logged in', '2023-12-08 01:55:28'),
	(145, 'manoj99', '127.0.0.1', 'Incorrect username/password', '2023-12-08 01:55:55'),
	(146, 'manoj99', '127.0.0.1', 'logged in', '2023-12-08 01:56:23'),
	(147, 'manoj99', '127.0.0.1', 'logged in', '2023-12-08 01:59:20'),
	(148, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-09 13:26:26'),
	(149, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-09 13:26:35'),
	(150, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-09 13:26:47'),
	(151, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-09 13:26:57'),
	(152, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-12-09 13:30:11'),
	(153, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-12-09 13:31:55'),
	(154, 'lbaj', '127.0.0.1', 'logged in', '2023-12-09 13:33:04'),
	(155, 'lbaj', '127.0.0.1', 'logged in', '2023-12-09 21:49:45'),
	(156, 'lbaj', '127.0.0.1', 'logged in', '2023-12-09 21:51:03'),
	(157, 'lujana', '127.0.0.1', 'Incorrect username/password', '2023-12-09 21:53:48'),
	(158, 'lbaj', '127.0.0.1', 'Incorrect username/password', '2023-12-09 21:53:58'),
	(159, 'lbaj', '127.0.0.1', 'logged in', '2023-12-09 21:54:07'),
	(160, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-11 16:54:37'),
	(161, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-11 16:54:48'),
	(162, 'luzzubaj', '127.0.0.1', 'Incorrect username/password', '2023-12-11 16:54:58'),
	(163, 'lbaj', '127.0.0.1', 'logged in', '2023-12-11 16:55:54'),
	(164, 'lbaj', '127.0.0.1', 'logged in', '2023-12-12 20:46:37'),
	(165, 'lbaj', '127.0.0.1', 'logged in', '2023-12-12 22:31:13'),
	(166, 'lbaj', '127.0.0.1', 'logged in', '2023-12-12 23:16:14'),
	(167, 'lbaj', '127.0.0.1', 'logged in', '2023-12-12 23:17:58'),
	(168, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-12-16 20:16:42'),
	(169, 'lbaj', '127.0.0.1', 'Incorrect username/password', '2023-12-16 20:16:53'),
	(170, 'sajana', '127.0.0.1', 'Incorrect username/password', '2023-12-16 20:16:56'),
	(171, 'lbaj', '127.0.0.1', 'Incorrect username/password', '2023-12-16 20:17:07'),
	(172, 'lbaj', '127.0.0.1', 'logged in', '2023-12-16 20:17:21'),
	(173, 'lbaj', '127.0.0.1', 'logged in', '2023-12-18 21:34:53'),
	(174, 'testing9968', '127.0.0.1', 'logged in', '2023-12-18 22:15:50'),
	(175, 'lbaj', '127.0.0.1', 'logged in', '2023-12-18 22:17:30'),
	(176, 'lbaj', '127.0.0.1', 'logged in', '2023-12-19 21:34:02'),
	(177, 'manojgamer99@gmail.com', '127.0.0.1', 'Incorrect username/password', '2023-12-19 21:43:38'),
	(178, 'manojgamer99@gmail.com', '127.0.0.1', 'Incorrect username/password', '2023-12-19 21:44:19'),
	(179, 'manojgamer99@gmail.com', '127.0.0.1', 'Incorrect password', '2023-12-19 21:45:39'),
	(180, 'manojgamer99@gmail.com', '127.0.0.1', 'Incorrect password', '2023-12-19 21:45:53'),
	(181, 'lbaj', '127.0.0.1', 'Incorrect username/password', '2023-12-19 21:57:23'),
	(182, 'lbaj', '127.0.0.1', 'logged in', '2023-12-19 21:57:30'),
	(183, 'lbaj', '127.0.0.1', 'logged in', '2023-12-20 09:39:41'),
	(184, 'lbaj', '127.0.0.1', 'logged in', '2023-12-20 09:43:37'),
	(185, 'lbaj', '127.0.0.1', 'logged in', '2023-12-20 09:47:00'),
	(186, 'lbaj', '127.0.0.1', 'logged in', '2023-12-20 09:54:27'),
	(187, 'lbaj', '127.0.0.1', 'logged in', '2023-12-20 10:10:55');

-- Dumping structure for table ofs.order_info
CREATE TABLE IF NOT EXISTS `order_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` varchar(50) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `ordered_date` varchar(50) DEFAULT NULL,
  `delivery_date` varchar(50) DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `productid` varchar(50) DEFAULT NULL,
  `userid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `productid` (`productid`),
  KEY `user_id` (`userid`),
  CONSTRAINT `productid` FOREIGN KEY (`productid`) REFERENCES `product_info` (`product_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `user_id` FOREIGN KEY (`userid`) REFERENCES `app_ofs_customuser` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.order_info: ~7 rows (approximately)
INSERT INTO `order_info` (`id`, `order_id`, `quantity`, `ordered_date`, `delivery_date`, `price`, `status`, `productid`, `userid`) VALUES
	(10, '1475', '', '2023-12-01', '', '', 'Completed', '12087', 17),
	(11, '1755', '2', '2023-12-02', '2023-12-01', '12', 'Ongoing', '15192', 17),
	(14, '1379', '1', '2023-12-11', '2023-12-14', '12', 'Completed', '15192', 17),
	(15, '1383', '12', '2023-12-01', '2023-12-02', '12', 'Completed', '15192', 17),
	(16, '1130', '12', '2023-12-02', '2023-12-04', '12', 'Completed', '15192', 17),
	(17, '1370', '2', '2023-12-16', '2023-12-23', '12', 'Ongoing', '17668', 17),
	(18, '1044', '12', '2023-12-08', '2023-12-11', '12', 'Completed', '12087', 17);

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
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ofs.product_info: ~0 rows (approximately)
INSERT INTO `product_info` (`id`, `product_id`, `product_name`, `product_description`, `category`, `userid`) VALUES
	(29, '15283', 'aedasd', 'sadf', '3922', NULL),
	(32, '16119', 'Account', 'Account Book', '9512', 15),
	(33, '15192', 'Nepali', 'Book', '9512', 17),
	(34, '12087', 'Blue Pen', 'Blue Pen', '2550', 17),
	(35, '17668', 'Red Pen', 'Red Pen', '2550', 17),
	(36, '10078', 'Black Pen', 'Black Pen', '2550', 17),
	(37, '13747', 'Large Size Copy', 'Large Size Copy', '9700', 17),
	(38, '18858', 'Small Size Copy', 'Small Size Copy', '9700', 17),
	(39, '13439', 'white pen', 'whitepen', '7087', 17);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
