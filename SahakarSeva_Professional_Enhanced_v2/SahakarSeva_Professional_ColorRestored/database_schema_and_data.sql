-- ============================================================================
-- SahakarSeva Cooperative Services - Database Backup Dump
-- Exported: 2026-09-27 20:32:42
-- Database: contractor_erp_db
-- Total Tables: 22
-- ============================================================================

SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- --------------------------------------------------------
-- Table structure for `activity_logs`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `activity_logs`;
CREATE TABLE `activity_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `details` text COLLATE utf8_unicode_ci NOT NULL,
  `old_value` text COLLATE utf8_unicode_ci,
  `new_value` text COLLATE utf8_unicode_ci,
  `entity_type` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `entity_id` int(11) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_activity_logs_timestamp` (`timestamp`),
  CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `activity_logs`
LOCK TABLES `activity_logs` WRITE;
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (1, 1, 'ONBOARD_CONTRACTOR', 'Apex Federation approved Chembur Labour Cooperative Society Ltd. with Pro tier.', NULL, 'Approved', 'Contractor', 1, '2026-05-30 14:34:55', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (2, 2, 'DISPATCH_WORKER', 'Assigned Master Artisan John Doe to Service Request SR-2026-00101', 'Unassigned', 'Assigned: jdoe', 'ServiceRequest', 1, '2026-09-22 10:34:55', '192.168.1.101');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (3, 7, 'VERIFY_OTP', 'Worker John Doe verified Customer OTP 4829 for Service Request SR-2026-00101', 'OTP_PENDING', 'OTP_VERIFIED', 'ServiceRequest', 1, '2026-09-22 10:49:55', '192.168.1.55');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (4, 17, 'PAYMENT_SUCCESS', 'Customer Anita Deshmukh settled Rs. 4,850.00 via Razorpay for Invoice INV-2026-00101', 'Pending', 'Paid', 'Payment', 1, '2026-09-22 13:34:55', '103.21.124.4');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (5, 1, 'SURAKSHA_NIDHI_RECONCILE', 'Automated welfare engine reconciled 4% Suraksha Nidhi cess ledger for Chembur society.', 'Unreconciled', 'Reconciled', 'WelfareLedger', 1, '2026-09-26 14:34:55', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (197, 17, 'Submit Review SR-RATE-907110', 'Customer @anita_deshmukh submitted 4-star review for Electrical', NULL, NULL, NULL, NULL, '2026-09-27 14:38:27', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (198, 17, 'Submit Review SR-FORM-907172', 'Customer @anita_deshmukh submitted 5-star review for Cleaning', NULL, NULL, NULL, NULL, '2026-09-27 14:38:27', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (199, 17, 'Submit Review SR-AGG2-907230', 'Customer @anita_deshmukh submitted 2-star review for Plumbing', NULL, NULL, NULL, NULL, '2026-09-27 14:38:27', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (200, 17, 'Book Service SR-2026-000009', 'Customer @anita_deshmukh submitted Normal ticket SR-2026-000009 (Electrician) in Kurla-Govandi corridor', NULL, NULL, NULL, NULL, '2026-09-27 14:38:29', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (201, 61, 'Apex Conciliation: Resolved in Customer Favor - Restitution & Work Guarantee Cleared', 'Publisher arbitrated ticket TKT-APX-0043. Status: Resolved. Notes: Full restitution approved under SahakarSeva statutory guarantee.', NULL, NULL, NULL, NULL, '2026-09-27 14:38:45', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (202, 3, 'Enable 2FA (Google Authenticator)', 'Enabled two-factor authentication via Google Authenticator app.', NULL, NULL, NULL, NULL, '2026-09-27 14:41:19', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (203, 61, 'Apex Conciliation: Resolved in Customer Favor - Restitution & Work Guarantee Cleared', 'Publisher arbitrated ticket TKT-APX-0045. Status: Resolved. Notes: Full restitution approved under SahakarSeva statutory guarantee.', NULL, NULL, NULL, NULL, '2026-09-27 14:59:08', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (204, 61, 'Apex Conciliation: Resolved in Customer Favor - Restitution & Work Guarantee Cleared', 'Publisher arbitrated ticket TKT-APX-0047. Status: Resolved. Notes: Full restitution approved under SahakarSeva statutory guarantee.', NULL, NULL, NULL, NULL, '2026-09-27 14:59:55', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (205, 17, 'Approved Quotation QTN-TEST-329103', 'Customer @anita_deshmukh approved quotation #QTN-TEST-329103 (Electrical)', NULL, NULL, NULL, NULL, '2026-09-27 15:02:09', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (206, 61, 'Apex Conciliation: Resolved in Customer Favor - Restitution & Work Guarantee Cleared', 'Publisher arbitrated ticket TKT-APX-0049. Status: Resolved. Notes: Full restitution approved under SahakarSeva statutory guarantee.', NULL, NULL, NULL, NULL, '2026-09-27 15:02:19', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (207, 17, 'Submit Review SR-RATE-349337', 'Customer @anita_deshmukh submitted 4-star review for Electrical', NULL, NULL, NULL, NULL, '2026-09-27 15:02:29', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (208, 17, 'Submit Review SR-FORM-349391', 'Customer @anita_deshmukh submitted 5-star review for Cleaning', NULL, NULL, NULL, NULL, '2026-09-27 15:02:29', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (209, 17, 'Submit Review SR-AGG2-349448', 'Customer @anita_deshmukh submitted 2-star review for Plumbing', NULL, NULL, NULL, NULL, '2026-09-27 15:02:29', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (210, 17, 'Book Service SR-2026-000314', 'Customer @anita_deshmukh submitted Normal ticket SR-2026-000314 (Electrician) in Kurla-Govandi corridor', NULL, NULL, NULL, NULL, '2026-09-27 15:02:31', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (211, 17, 'Approved Quotation QTN-TEST-351764', 'Customer @anita_deshmukh approved quotation #QTN-TEST-351764 (Electrical)', NULL, NULL, NULL, NULL, '2026-09-27 15:02:31', '127.0.0.1');
INSERT INTO `activity_logs` (`id`, `user_id`, `action`, `details`, `old_value`, `new_value`, `entity_type`, `entity_id`, `timestamp`, `ip_address`) VALUES (212, 61, 'Apex Conciliation: Resolved in Customer Favor - Restitution & Work Guarantee Cleared', 'Publisher arbitrated ticket TKT-APX-0052. Status: Resolved. Notes: Full restitution approved under SahakarSeva statutory guarantee.', NULL, NULL, NULL, NULL, '2026-09-27 15:02:32', '127.0.0.1');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `ai_delay_predictions`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `ai_delay_predictions`;
CREATE TABLE `ai_delay_predictions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) DEFAULT NULL,
  `risk_level` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `delay_percentage` decimal(5,2) DEFAULT NULL,
  `expected_delay_days` int(11) DEFAULT NULL,
  `reason` text COLLATE utf8_unicode_ci,
  `suggested_actions` text COLLATE utf8_unicode_ci,
  `created_at` datetime DEFAULT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `ai_delay_predictions`
LOCK TABLES `ai_delay_predictions` WRITE;
INSERT INTO `ai_delay_predictions` (`id`, `project_id`, `risk_level`, `delay_percentage`, `expected_delay_days`, `reason`, `suggested_actions`, `created_at`, `service_request_id`) VALUES (1, 1, 'Low', 0.00, 0, 'All required genuine MCB units in stock at Chembur hub. No transit delay predicted.', 'Standard dispatch procedure maintained.', '2026-09-21 14:34:55', 1);
INSERT INTO `ai_delay_predictions` (`id`, `project_id`, `risk_level`, `delay_percentage`, `expected_delay_days`, `reason`, `suggested_actions`, `created_at`, `service_request_id`) VALUES (2, 8, 'Medium', 35.00, 2, 'Monsoon precipitation humidity level > 85% in Mumbai suburbs may prolong wall putty curing time.', 'Utilize rapid-curing polymer damp-proofing coat before primer application.', '2026-09-26 14:34:55', 8);
INSERT INTO `ai_delay_predictions` (`id`, `project_id`, `risk_level`, `delay_percentage`, `expected_delay_days`, `reason`, `suggested_actions`, `created_at`, `service_request_id`) VALUES (3, 5, 'Low', 5.00, 0, 'Tile consignment arriving on schedule via Kurla logistics depot.', 'Commence surface hacking in parallel with logistics arrival.', '2026-09-27 08:34:55', 5);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `ai_estimates`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `ai_estimates`;
CREATE TABLE `ai_estimates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_request_id` int(11) NOT NULL,
  `service_type` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `house_size` decimal(10,2) NOT NULL,
  `num_rooms` int(11) DEFAULT NULL,
  `problem_type` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `urgency` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `est_material_cost` decimal(10,2) DEFAULT NULL,
  `est_labour_cost` decimal(10,2) DEFAULT NULL,
  `est_total_cost` decimal(10,2) DEFAULT NULL,
  `est_completion_time` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `confidence_score` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `service_request_id` (`service_request_id`),
  CONSTRAINT `ai_estimates_ibfk_1` FOREIGN KEY (`service_request_id`) REFERENCES `service_requests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `ai_estimates`
LOCK TABLES `ai_estimates` WRITE;
INSERT INTO `ai_estimates` (`id`, `service_request_id`, `service_type`, `house_size`, `num_rooms`, `problem_type`, `urgency`, `est_material_cost`, `est_labour_cost`, `est_total_cost`, `est_completion_time`, `confidence_score`) VALUES (1, 1, 'Electrical', 1200.00, 3, 'Burnt MCB and Load Imbalance', 'Urgent', 755.00, 3500.00, 4255.00, '3.5 hours', 96.50);
INSERT INTO `ai_estimates` (`id`, `service_request_id`, `service_type`, `house_size`, `num_rooms`, `problem_type`, `urgency`, `est_material_cost`, `est_labour_cost`, `est_total_cost`, `est_completion_time`, `confidence_score`) VALUES (2, 2, 'Plumbing', 4500.00, 12, 'Pump Bearing Seizure & Flow Restriction', 'Normal', 2845.00, 4800.00, 7645.00, '5.0 hours', 94.20);
INSERT INTO `ai_estimates` (`id`, `service_request_id`, `service_type`, `house_size`, `num_rooms`, `problem_type`, `urgency`, `est_material_cost`, `est_labour_cost`, `est_total_cost`, `est_completion_time`, `confidence_score`) VALUES (3, 3, 'Carpentry', 950.00, 2, 'Door Sag & Smart Lock Fitting', 'Normal', 650.00, 2400.00, 3050.00, '4.0 hours', 92.80);
INSERT INTO `ai_estimates` (`id`, `service_request_id`, `service_type`, `house_size`, `num_rooms`, `problem_type`, `urgency`, `est_material_cost`, `est_labour_cost`, `est_total_cost`, `est_completion_time`, `confidence_score`) VALUES (4, 8, 'Painting', 1800.00, 4, 'Monsoon Dampness & Flaking Paint', 'Normal', 11900.00, 5500.00, 17400.00, '24.0 hours', 91.40);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `ai_material_forecasts`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `ai_material_forecasts`;
CREATE TABLE `ai_material_forecasts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `trade_category` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `material_name` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `days_remaining` int(11) DEFAULT NULL,
  `recommended_purchase_qty` decimal(10,2) DEFAULT NULL,
  `supplier_recommendation` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `alert_level` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------
-- Table structure for `attendance`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `attendance`;
CREATE TABLE `attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_archived` tinyint(1) NOT NULL,
  `worker_id` int(11) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `date` date NOT NULL,
  `check_in_time` datetime DEFAULT NULL,
  `check_out_time` datetime DEFAULT NULL,
  `status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `check_in_lat` decimal(10,8) DEFAULT NULL,
  `check_in_lng` decimal(11,8) DEFAULT NULL,
  `check_out_lat` decimal(10,8) DEFAULT NULL,
  `check_out_lng` decimal(11,8) DEFAULT NULL,
  `verified_by_gps` tinyint(1) DEFAULT NULL,
  `verified_by_qr` tinyint(1) DEFAULT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `worker_id` (`worker_id`),
  KEY `project_id` (`project_id`),
  KEY `ix_attendance_date` (`date`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`worker_id`) REFERENCES `workers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `attendance`
LOCK TABLES `attendance` WRITE;
INSERT INTO `attendance` (`id`, `is_archived`, `worker_id`, `project_id`, `date`, `check_in_time`, `check_out_time`, `status`, `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `verified_by_gps`, `verified_by_qr`, `service_request_id`) VALUES (1, 0, 7, 1, '2026-09-22', '2026-09-22 09:58:00', '2026-09-22 13:30:00', 'Present', 19.07700000, 72.90800000, 19.07702000, 72.90801000, 1, 1, 1);
INSERT INTO `attendance` (`id`, `is_archived`, `worker_id`, `project_id`, `date`, `check_in_time`, `check_out_time`, `status`, `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `verified_by_gps`, `verified_by_qr`, `service_request_id`) VALUES (2, 0, 9, 2, '2026-09-24', '2026-09-24 08:55:00', '2026-09-24 14:00:00', 'Present', 19.05200000, 72.91500000, 19.05201000, 72.91502000, 1, 1, 2);
INSERT INTO `attendance` (`id`, `is_archived`, `worker_id`, `project_id`, `date`, `check_in_time`, `check_out_time`, `status`, `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `verified_by_gps`, `verified_by_qr`, `service_request_id`) VALUES (3, 0, 8, 3, '2026-09-27', '2026-09-27 10:52:00', NULL, 'Present', 19.06100000, 72.89950000, NULL, NULL, 1, 1, 3);
INSERT INTO `attendance` (`id`, `is_archived`, `worker_id`, `project_id`, `date`, `check_in_time`, `check_out_time`, `status`, `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `verified_by_gps`, `verified_by_qr`, `service_request_id`) VALUES (4, 0, 16, 7, '2026-09-19', '2026-09-19 08:25:00', '2026-09-19 15:00:00', 'Present', 19.05200000, 72.91500000, 19.05201000, 72.91501000, 1, 1, 7);
INSERT INTO `attendance` (`id`, `is_archived`, `worker_id`, `project_id`, `date`, `check_in_time`, `check_out_time`, `status`, `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `verified_by_gps`, `verified_by_qr`, `service_request_id`) VALUES (5, 0, 10, NULL, '2026-09-26', '2026-09-26 09:10:00', '2026-09-26 17:30:00', 'Present', 19.06880000, 72.87970000, 19.06880000, 72.87970000, 1, 0, NULL);
INSERT INTO `attendance` (`id`, `is_archived`, `worker_id`, `project_id`, `date`, `check_in_time`, `check_out_time`, `status`, `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `verified_by_gps`, `verified_by_qr`, `service_request_id`) VALUES (6, 0, 11, NULL, '2026-09-25', '2026-09-25 08:45:00', '2026-09-25 17:00:00', 'Present', 19.07120000, 72.88500000, 19.07120000, 72.88500000, 1, 0, NULL);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `contractor_documents`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `contractor_documents`;
CREATE TABLE `contractor_documents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contractor_id` int(11) NOT NULL,
  `worker_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `title` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `category` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `file_path` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `file_size` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8_unicode_ci,
  `expiry_date` date DEFAULT NULL,
  `uploaded_at` datetime DEFAULT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contractor_id` (`contractor_id`),
  KEY `worker_id` (`worker_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `contractor_documents_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE CASCADE,
  CONSTRAINT `contractor_documents_ibfk_2` FOREIGN KEY (`worker_id`) REFERENCES `workers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `contractor_documents`
LOCK TABLES `contractor_documents` WRITE;
INSERT INTO `contractor_documents` (`id`, `contractor_id`, `worker_id`, `project_id`, `title`, `category`, `file_path`, `file_size`, `notes`, `expiry_date`, `uploaded_at`, `service_request_id`) VALUES (1, 1, NULL, 1, 'State Cooperative Registration Certificate', 'Site Permit', '/static/uploads/vault/chembur_coop_registration.pdf', '1.4 MB', 'Official registration under Maharashtra Cooperative Societies Act 1960', '2028-09-26', '2026-06-19 14:34:55', 1);
INSERT INTO `contractor_documents` (`id`, `contractor_id`, `worker_id`, `project_id`, `title`, `category`, `file_path`, `file_size`, `notes`, `expiry_date`, `uploaded_at`, `service_request_id`) VALUES (2, 1, 7, 1, 'Class-A Government Electrical Contractor License', 'Worker License', '/static/uploads/vault/jdoe_electrical_license_a.pdf', '850 KB', 'Certified for high voltage up to 33kV installations by Maharashtra PWD', '2027-09-27', '2026-06-29 14:34:55', 1);
INSERT INTO `contractor_documents` (`id`, `contractor_id`, `worker_id`, `project_id`, `title`, `category`, `file_path`, `file_size`, `notes`, `expiry_date`, `uploaded_at`, `service_request_id`) VALUES (3, 1, NULL, NULL, 'Federation Comprehensive Public Liability Insurance', 'Insurance Policy', '/static/uploads/vault/chembur_public_liability_2026.pdf', '2.1 MB', 'Rs. 2.5 Crore coverage for residential and commercial site liabilities', '2027-07-04', '2026-07-04 14:34:55', NULL);
INSERT INTO `contractor_documents` (`id`, `contractor_id`, `worker_id`, `project_id`, `title`, `category`, `file_path`, `file_size`, `notes`, `expiry_date`, `uploaded_at`, `service_request_id`) VALUES (4, 2, NULL, 2, 'Kurla-Govandi Cooperative State Registration Bye-Laws', 'Contract', '/static/uploads/vault/kurla_bye_laws_2026.pdf', '3.2 MB', 'Approved Labour Cooperative Bye-laws ratified by District Registrar', '2029-06-23', '2026-06-24 14:34:55', 2);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `contractor_reviews`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `contractor_reviews`;
CREATE TABLE `contractor_reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contractor_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `rating` int(11) NOT NULL,
  `title` varchar(150) COLLATE utf8_unicode_ci DEFAULT NULL,
  `review_text` text COLLATE utf8_unicode_ci,
  `is_approved` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contractor_id` (`contractor_id`),
  KEY `customer_id` (`customer_id`),
  KEY `service_request_id` (`service_request_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `contractor_reviews_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE CASCADE,
  CONSTRAINT `contractor_reviews_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `contractor_reviews_ibfk_3` FOREIGN KEY (`service_request_id`) REFERENCES `service_requests` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `contractor_reviews`
LOCK TABLES `contractor_reviews` WRITE;
INSERT INTO `contractor_reviews` (`id`, `contractor_id`, `customer_id`, `service_request_id`, `project_id`, `rating`, `title`, `review_text`, `is_approved`, `created_at`) VALUES (1, 1, 17, 1, 1, 5, 'Exemplary Cooperative Electrical Service', 'John from Chembur Cooperative was professional, equipped with calibrated Fluke meters, and fixed our dangerous sparking circuit with full transparency.', 1, '2026-09-22 14:34:55');
INSERT INTO `contractor_reviews` (`id`, `contractor_id`, `customer_id`, `service_request_id`, `project_id`, `rating`, `title`, `review_text`, `is_approved`, `created_at`) VALUES (2, 1, 19, 2, 2, 5, 'Flawless Booster Pump Overhaul for CHS', 'Overhead pressure across our 7th floor wings is completely restored. Impressed by the cooperative ethos and lack of hidden charges.', 1, '2026-09-24 14:34:55');
INSERT INTO `contractor_reviews` (`id`, `contractor_id`, `customer_id`, `service_request_id`, `project_id`, `rating`, `title`, `review_text`, `is_approved`, `created_at`) VALUES (3, 2, 19, 7, 7, 5, 'Robust Compound Gate Welding', 'The Kurla cooperative welder reinforced the pivot hinge with heavy gussets. Sturdy and well finished.', 1, '2026-09-20 14:34:55');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `contractors`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `contractors`;
CREATE TABLE `contractors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `company_name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `company_logo` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `license_number` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `business_type` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `service_areas` text COLLATE utf8_unicode_ci,
  `website` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `established_year` int(11) DEFAULT NULL,
  `cooperative_reg_no` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `federation_name` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `contact_phone` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `contact_email` varchar(120) COLLATE utf8_unicode_ci DEFAULT NULL,
  `office_address` text COLLATE utf8_unicode_ci,
  `business_hours` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `license_document` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `onboarding_status` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `verified_at` datetime DEFAULT NULL,
  `rejection_reason` text COLLATE utf8_unicode_ci,
  `total_projects_completed` int(11) DEFAULT NULL,
  `average_rating` decimal(3,2) DEFAULT NULL,
  `total_reviews` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `contractors_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `contractors`
LOCK TABLES `contractors` WRITE;
INSERT INTO `contractors` (`id`, `user_id`, `company_name`, `company_logo`, `license_number`, `business_type`, `description`, `service_areas`, `website`, `established_year`, `cooperative_reg_no`, `federation_name`, `contact_phone`, `contact_email`, `office_address`, `business_hours`, `license_document`, `onboarding_status`, `is_active`, `is_verified`, `verified_at`, `rejection_reason`, `total_projects_completed`, `average_rating`, `total_reviews`, `created_at`) VALUES (1, 2, 'Chembur Labour Cooperative Society Ltd.', '/static/uploads/contractors/chembur_logo.png', 'REG-BOM-LABOUR-1982-0042', 'Multi-Trade Cooperative', 'Premier multi-trade labour cooperative registered in 1982. Providing certified electrical, plumbing, carpentry, and masonry artisans across Eastern Mumbai.', 'Chembur, Govandi, Deonar, Tilak Nagar', 'https://chemburseva.coop', 1982, 'MAH/BOM/COOP/1982/042', 'Maharashtra Apex Labour Cooperative Federation', '+91-9820012345', 'admin@chemburseva.coop', 'Plot 14, Cooperative Bhavan, Chembur Naka, Chembur, Mumbai - 400071', '07:00 - 21:00', NULL, 'approved', 1, 1, NULL, NULL, 342, 4.00, 3, '2026-09-27 14:34:58');
INSERT INTO `contractors` (`id`, `user_id`, `company_name`, `company_logo`, `license_number`, `business_type`, `description`, `service_areas`, `website`, `established_year`, `cooperative_reg_no`, `federation_name`, `contact_phone`, `contact_email`, `office_address`, `business_hours`, `license_document`, `onboarding_status`, `is_active`, `is_verified`, `verified_at`, `rejection_reason`, `total_projects_completed`, `average_rating`, `total_reviews`, `created_at`) VALUES (2, 3, 'Kurla-Govandi Shramik Sahakari Sanstha Maryadit', '/static/uploads/contractors/kurla_logo.png', 'REG-BOM-SHRAMIK-1994-0118', 'Civil & Structural Cooperative', 'Affiliated labour cooperative federation unit specialized in civil works, fabrication, pipefitting, and emergency household repairs with 120+ registered artisans.', 'Kurla, Chunabhatti, Nehru Nagar, Qureshi Nagar', 'https://kurlashramik.coop', 1994, 'MAH/BOM/COOP/1994/118', 'Maharashtra Apex Labour Cooperative Federation', '+91-9820054321', 'admin@kurlashramik.coop', 'Shramik Seva Kendra, Building 24, Nehru Nagar, Kurla East, Mumbai - 400024', '07:30 - 20:30', NULL, 'approved', 1, 1, NULL, NULL, 215, 4.79, 215, '2026-09-27 14:34:58');
INSERT INTO `contractors` (`id`, `user_id`, `company_name`, `company_logo`, `license_number`, `business_type`, `description`, `service_areas`, `website`, `established_year`, `cooperative_reg_no`, `federation_name`, `contact_phone`, `contact_email`, `office_address`, `business_hours`, `license_document`, `onboarding_status`, `is_active`, `is_verified`, `verified_at`, `rejection_reason`, `total_projects_completed`, `average_rating`, `total_reviews`, `created_at`) VALUES (3, 5, 'ContractorFlow Facilities Pvt. Ltd.', '/static/uploads/contractors/flow_logo.png', 'U74999MH2021PTC368910', 'Facilities Engineering Enterprise', 'Private facilities engineering enterprise integrating with SahakarSeva under cooperative joint venture framework for specialized HVAC and industrial refrigeration.', 'Dadar, Lower Parel, Prabhadevi', 'https://contractorflow.in', 2021, 'PVT-JV-2021-368', 'Maharashtra Apex Labour Cooperative Federation', '+91-9820098765', 'contact@contractorflow.in', 'Suite 401, Trade Center, Dadar West, Mumbai - 400028', '09:00 - 18:00', NULL, 'pending_approval', 1, 0, NULL, NULL, 18, 4.60, 18, '2026-09-27 14:34:58');
INSERT INTO `contractors` (`id`, `user_id`, `company_name`, `company_logo`, `license_number`, `business_type`, `description`, `service_areas`, `website`, `established_year`, `cooperative_reg_no`, `federation_name`, `contact_phone`, `contact_email`, `office_address`, `business_hours`, `license_document`, `onboarding_status`, `is_active`, `is_verified`, `verified_at`, `rejection_reason`, `total_projects_completed`, `average_rating`, `total_reviews`, `created_at`) VALUES (4, 4, 'Ghatkopar Sahakari Mazdoor Sangh Maryadit', '/static/uploads/contractors/ghatkopar_logo.png', 'REG-BOM-MAZDOOR-2001-0309', 'Home & Commercial Maintenance Cooperative', 'Community cooperative with dedicated women artisan collectives specializing in house painting, deep cleaning, domestic maintenance, and pest barrier application.', 'Ghatkopar, Vidyavihar, Pant Nagar, Amrut Nagar', 'https://ghatkoparcoop.in', 2001, 'MAH/BOM/COOP/2001/309', 'Maharashtra Apex Labour Cooperative Federation', '+91-9820078901', 'admin@ghatkoparcoop.in', 'Amrut Nagar Sahakari Complex, LBS Marg, Ghatkopar West, Mumbai - 400086', '08:00 - 20:00', NULL, 'approved', 1, 1, NULL, NULL, 189, 4.91, 189, '2026-09-27 14:34:58');
INSERT INTO `contractors` (`id`, `user_id`, `company_name`, `company_logo`, `license_number`, `business_type`, `description`, `service_areas`, `website`, `established_year`, `cooperative_reg_no`, `federation_name`, `contact_phone`, `contact_email`, `office_address`, `business_hours`, `license_document`, `onboarding_status`, `is_active`, `is_verified`, `verified_at`, `rejection_reason`, `total_projects_completed`, `average_rating`, `total_reviews`, `created_at`) VALUES (21, 62, 'Test Apex Linked Society PACS', NULL, NULL, 'Multi-Trade', NULL, 'Chembur Central', NULL, NULL, NULL, 'State Labour Cooperative Federation', '9820112233', NULL, NULL, '09:00 - 18:00', NULL, 'approved', 1, 1, NULL, NULL, 0, 0.00, 0, '2026-09-27 14:38:45');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `customers`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `customers`;
CREATE TABLE `customers` (
  `id` int(11) NOT NULL,
  `is_archived` tinyint(1) NOT NULL,
  `company_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `billing_address` text COLLATE utf8_unicode_ci,
  `emergency_contact` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `customers`
LOCK TABLES `customers` WRITE;
INSERT INTO `customers` (`id`, `is_archived`, `company_name`, `billing_address`, `emergency_contact`) VALUES (17, 0, 'Anita Deshmukh Residence', 'Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077', 'Ashok Deshmukh (+91-9820033091)');
INSERT INTO `customers` (`id`, `is_archived`, `company_name`, `billing_address`, `emergency_contact`) VALUES (18, 0, 'Rahul Sharma Household', 'B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071', 'Sunita Sharma (+91-9820033092)');
INSERT INTO `customers` (`id`, `is_archived`, `company_name`, `billing_address`, `emergency_contact`) VALUES (19, 0, 'Deonar Heights Co-op Housing Society Ltd.', 'Deonar Heights CHS, Deonar Farm Road, Deonar, Mumbai - 400088', 'CHS Security Office (+91-9820033093)');
INSERT INTO `customers` (`id`, `is_archived`, `company_name`, `billing_address`, `emergency_contact`) VALUES (20, 0, 'Priya Nair Apartment', 'Flat 603, Green Acres CHS, Tilak Nagar, Chembur, Mumbai - 400089', 'Rajesh Nair (+91-9820033094)');
INSERT INTO `customers` (`id`, `is_archived`, `company_name`, `billing_address`, `emergency_contact`) VALUES (21, 0, 'Vikas Patil Enterprises', 'Office 301, Commercial Arcade, LBS Marg, Kurla West, Mumbai - 400070', 'Estate Manager (+91-9820033095)');
INSERT INTO `customers` (`id`, `is_archived`, `company_name`, `billing_address`, `emergency_contact`) VALUES (63, 0, NULL, 'Flat 402, Sai Heights, Chembur', NULL);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `login_histories`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `login_histories`;
CREATE TABLE `login_histories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `user_agent` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_login_histories_timestamp` (`timestamp`),
  CONSTRAINT `login_histories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `login_histories`
LOCK TABLES `login_histories` WRITE;
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (1, 1, '2026-09-27 13:34:55', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SahakarSeva/Desktop', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (2, 2, '2026-09-27 12:34:55', '192.168.1.101', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (3, 7, '2026-09-27 11:34:55', '192.168.1.55', 'Mozilla/5.0 (Linux; Android 14; Mobile) SahakarSevaWorker/2.0', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (4, 17, '2026-09-26 14:34:55', '103.21.124.4', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (5, 3, '2026-09-25 14:34:55', '192.168.1.112', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/128.0', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (6, 18, '2026-09-27 09:34:55', '103.21.124.8', 'Mozilla/5.0 (Linux; Android 14; Pixel 8)', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (285, 17, '2026-09-27 14:38:27', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (286, 10, '2026-09-27 14:38:27', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (287, 2, '2026-09-27 14:38:28', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (288, 1, '2026-09-27 14:38:28', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (289, 17, '2026-09-27 14:38:29', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (290, 2, '2026-09-27 14:41:38', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (291, 2, '2026-09-27 14:42:34', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (292, 1, '2026-09-27 14:43:25', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (293, 3, '2026-09-27 14:44:09', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36', 'Success (2FA)');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (294, 17, '2026-09-27 15:02:29', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (295, 10, '2026-09-27 15:02:29', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (296, 2, '2026-09-27 15:02:30', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (297, 1, '2026-09-27 15:02:30', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
INSERT INTO `login_histories` (`id`, `user_id`, `timestamp`, `ip_address`, `user_agent`, `status`) VALUES (298, 17, '2026-09-27 15:02:31', '127.0.0.1', 'Werkzeug/3.1.8', 'Success');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `notifications`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_archived` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `message` text COLLATE utf8_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `type` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `priority` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_notifications_timestamp` (`timestamp`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `notifications`
LOCK TABLES `notifications` WRITE;
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (1, 0, 17, 'Service Request Completed', 'Your DB Box overhaul (SR-2026-00101) has been certified complete by Master Artisan John Doe. Please provide your review.', 1, '2026-09-22 13:34:55', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (2, 0, 7, 'Suraksha Nidhi Fund Credit', 'Rs. 194.00 (4% statutory welfare cess) credited to your Suraksha Nidhi Social Security Account from job #SR-2026-00101.', 1, '2026-09-22 14:34:55', 'Success', 'High');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (3, 0, 2, 'Emergency Job Dispatched', 'Emergency request #SR-2026-00106 broadcasted in Ghatkopar East radius. 3 workers alerted.', 0, '2026-09-27 14:24:55', 'Alert', 'Emergency');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (4, 0, 1, 'New Contractor Application', 'ContractorFlow Ltd. submitted accreditation application. Pending Apex verification.', 0, '2026-09-24 14:34:55', 'Info', 'High');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (5, 0, 18, 'Quotation Ready for Review', 'Quotation QT-2026-00108 for your painting service is ready for review.', 0, '2026-09-26 14:34:55', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (709, 0, 1, 'Booking Cancelled', 'Customer @anita_deshmukh cancelled booking #TEST-CANCEL-1790519906. Reason: Fixed it myself', 0, '2026-09-27 14:38:26', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (710, 0, 1, 'New Support Ticket', 'Client @anita_deshmukh submitted society ticket #41: Question regarding electrician invoice.', 0, '2026-09-27 14:38:26', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (711, 0, 1, 'Booking Cancelled', 'Customer @anita_deshmukh cancelled booking #TEST-EMG-BCAST-1790519906. Reason: Neighbor turned off the main valve', 0, '2026-09-27 14:38:27', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (712, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000009 at 0.67 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 14:38:27', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (713, 0, 2, 'New Service Request Published', 'Customer @anita_deshmukh submitted service ticket SR-2026-000009 for Electrician.', 0, '2026-09-27 14:38:29', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (714, 0, 1, 'Apex Escalated Grievance', 'Client @testcitizen1 submitted Apex Escalated ticket #42: Emergency Plumbing Leak Unresolved with Extra Surcharge.', 0, '2026-09-27 14:38:45', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (715, 0, 63, 'Apex Conciliation: TKT-APX-0043', 'Your escalated dispute (TKT-APX-0043) was arbitrated and resolved in your favor by the Apex Council. Restitution and corrective measures have been mandated to the primary cooperative society. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 14:38:45', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (716, 0, 62, 'Apex Conciliation Notice: TKT-APX-0043', 'Dispute (TKT-APX-0043) resolved by Apex Federation. Society directive: Resolved in Customer Favor - Restitution & Work Guarantee Cleared. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 14:38:45', 'Warning', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (717, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000010 at 2.35 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 14:50:22', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (718, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000010 at 1.77 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 14:50:22', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (719, 0, 17, '[ARTISAN EN ROUTE] Emergency Claimed', 'Artisan @jdoe has accepted your emergency request EMG-2026-000010 and is en route! Mobile: +91-9820091001.', 0, '2026-09-27 14:50:22', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (720, 0, 7, 'Emergency Job Confirmed', 'You successfully claimed emergency dispatch #EMG-2026-000010. Destination: Chembur West, Mumbai. OTP verification required on arrival.', 0, '2026-09-27 14:50:22', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (721, 0, 17, '[ARTISAN EN ROUTE] Emergency Claimed', 'Artisan @jdoe has accepted your emergency request EMG-2026-000010 and is en route! Mobile: +91-9820091001.', 0, '2026-09-27 14:50:34', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (722, 0, 7, 'Emergency Job Confirmed', 'You successfully claimed emergency dispatch #EMG-2026-000010. Destination: Chembur West, Mumbai. OTP verification required on arrival.', 0, '2026-09-27 14:50:34', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (723, 0, 17, '[ARTISAN EN ROUTE] Emergency Claimed', 'Artisan @jdoe has accepted your emergency request EMG-2026-000010 and is en route! Mobile: +91-9820091001.', 0, '2026-09-27 14:50:48', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (724, 0, 7, 'Emergency Job Confirmed', 'You successfully claimed emergency dispatch #EMG-2026-000010. Destination: Chembur West, Mumbai. OTP verification required on arrival.', 0, '2026-09-27 14:50:48', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (725, 0, 17, '[ARTISAN EN ROUTE] Emergency Claimed', 'Artisan @jdoe has accepted your emergency request EMG-2026-000010 and is en route! Mobile: +91-9820091001.', 0, '2026-09-27 14:54:18', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (726, 0, 7, 'Emergency Job Confirmed', 'You successfully claimed emergency dispatch #EMG-2026-000010. Destination: Chembur West, Mumbai. OTP verification required on arrival.', 0, '2026-09-27 14:54:18', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (727, 0, 17, 'Service Request Completed', 'Your service request EMG-TEST-SYNC05 has been marked completed by technician @jdoe.', 0, '2026-09-27 14:54:59', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (728, 0, 1, 'Service Job Completed', 'Technician @jdoe marked service ticket EMG-TEST-SYNC05 as completed.', 0, '2026-09-27 14:54:59', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (729, 0, 17, 'Arrival OTP Verified Successfully', 'Arrival OTP verified by technician @jdoe. Service is now active and in progress.', 0, '2026-09-27 14:54:59', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (730, 0, 1, 'Arrival OTP Verified', 'Technician @jdoe verified arrival OTP for request EMG-TEST-SYNC01.', 0, '2026-09-27 14:54:59', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (731, 0, 17, 'Service Request Completed', 'Your service request EMG-TEST-SYNC05 has been marked completed by technician @jdoe.', 0, '2026-09-27 14:55:16', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (732, 0, 1, 'Service Job Completed', 'Technician @jdoe marked service ticket EMG-TEST-SYNC05 as completed.', 0, '2026-09-27 14:55:16', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (733, 0, 17, 'Arrival OTP Verified Successfully', 'Arrival OTP verified by technician @jdoe. Service is now active and in progress.', 0, '2026-09-27 14:55:16', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (734, 0, 1, 'Arrival OTP Verified', 'Technician @jdoe verified arrival OTP for request EMG-TEST-SYNC01.', 0, '2026-09-27 14:55:16', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (735, 0, 17, 'Service Request Completed', 'Your service request EMG-TEST-SYNC05 has been marked completed by technician @jdoe.', 0, '2026-09-27 14:56:12', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (736, 0, 1, 'Service Job Completed', 'Technician @jdoe marked service ticket EMG-TEST-SYNC05 as completed.', 0, '2026-09-27 14:56:12', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (737, 0, 17, 'Service Request Completed', 'Your service request EMG-TEST-SYNC05 has been marked completed by technician @jdoe.', 0, '2026-09-27 14:57:43', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (738, 0, 1, 'Service Job Completed', 'Technician @jdoe marked service ticket EMG-TEST-SYNC05 as completed.', 0, '2026-09-27 14:57:43', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (739, 0, 17, 'Arrival OTP Verified Successfully', 'Arrival OTP verified by technician @jdoe. Service is now active and in progress.', 0, '2026-09-27 14:57:43', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (740, 0, 1, 'Arrival OTP Verified', 'Technician @jdoe verified arrival OTP for request EMG-TEST-SYNC01.', 0, '2026-09-27 14:57:43', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (741, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000010 at 2.35 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 14:59:07', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (742, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000010 at 1.77 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 14:59:07', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (743, 0, 17, '[ARTISAN EN ROUTE] Emergency Claimed', 'Artisan @jdoe has accepted your emergency request EMG-2026-000010 and is en route! Mobile: +91-9820091001.', 0, '2026-09-27 14:59:07', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (744, 0, 7, 'Emergency Job Confirmed', 'You successfully claimed emergency dispatch #EMG-2026-000010. Destination: Chembur West, Mumbai. OTP verification required on arrival.', 0, '2026-09-27 14:59:07', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (745, 0, 17, 'Service Request Completed', 'Your service request EMG-TEST-SYNC05 has been marked completed by technician @jdoe.', 0, '2026-09-27 14:59:08', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (746, 0, 1, 'Service Job Completed', 'Technician @jdoe marked service ticket EMG-TEST-SYNC05 as completed.', 0, '2026-09-27 14:59:08', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (747, 0, 17, 'Arrival OTP Verified Successfully', 'Arrival OTP verified by technician @jdoe. Service is now active and in progress.', 0, '2026-09-27 14:59:08', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (748, 0, 1, 'Arrival OTP Verified', 'Technician @jdoe verified arrival OTP for request EMG-TEST-SYNC01.', 0, '2026-09-27 14:59:08', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (749, 0, 1, 'Apex Escalated Grievance', 'Client @testcitizen1 submitted Apex Escalated ticket #44: Emergency Plumbing Leak Unresolved with Extra Surcharge.', 0, '2026-09-27 14:59:08', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (750, 0, 63, 'Apex Conciliation: TKT-APX-0045', 'Your escalated dispute (TKT-APX-0045) was arbitrated and resolved in your favor by the Apex Council. Restitution and corrective measures have been mandated to the primary cooperative society. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 14:59:08', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (751, 0, 62, 'Apex Conciliation Notice: TKT-APX-0045', 'Dispute (TKT-APX-0045) resolved by Apex Federation. Society directive: Resolved in Customer Favor - Restitution & Work Guarantee Cleared. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 14:59:08', 'Warning', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (752, 0, 1, 'Apex Escalated Grievance', 'Client @testcitizen1 submitted Apex Escalated ticket #46: Emergency Plumbing Leak Unresolved with Extra Surcharge.', 0, '2026-09-27 14:59:55', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (753, 0, 63, 'Apex Conciliation: TKT-APX-0047', 'Your escalated dispute (TKT-APX-0047) was arbitrated and resolved in your favor by the Apex Council. Restitution and corrective measures have been mandated to the primary cooperative society. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 14:59:55', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (754, 0, 62, 'Apex Conciliation Notice: TKT-APX-0047', 'Dispute (TKT-APX-0047) resolved by Apex Federation. Society directive: Resolved in Customer Favor - Restitution & Work Guarantee Cleared. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 14:59:55', 'Warning', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (755, 0, 1, 'Quotation Approved & Invoice Issued', 'Customer @anita_deshmukh approved quotation QTN-TEST-329103 for Rs. 8000.40. Invoice #INV-2026-000370 has been generated.', 0, '2026-09-27 15:02:09', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (756, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000010 at 1.78 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 15:02:09', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (757, 0, 1, 'Apex Escalated Grievance', 'Client @testcitizen1 submitted Apex Escalated ticket #48: Emergency Plumbing Leak Unresolved with Extra Surcharge.', 0, '2026-09-27 15:02:19', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (758, 0, 63, 'Apex Conciliation: TKT-APX-0049', 'Your escalated dispute (TKT-APX-0049) was arbitrated and resolved in your favor by the Apex Council. Restitution and corrective measures have been mandated to the primary cooperative society. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 15:02:19', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (759, 0, 62, 'Apex Conciliation Notice: TKT-APX-0049', 'Dispute (TKT-APX-0049) resolved by Apex Federation. Society directive: Resolved in Customer Favor - Restitution & Work Guarantee Cleared. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 15:02:19', 'Warning', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (760, 0, 1, 'Booking Cancelled', 'Customer @anita_deshmukh cancelled booking #TEST-CANCEL-1790521348. Reason: Fixed it myself', 0, '2026-09-27 15:02:28', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (761, 0, 1, 'New Support Ticket', 'Client @anita_deshmukh submitted society ticket #50: Question regarding electrician invoice.', 0, '2026-09-27 15:02:29', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (762, 0, 1, 'Booking Cancelled', 'Customer @anita_deshmukh cancelled booking #TEST-EMG-BCAST-1790521349. Reason: Neighbor turned off the main valve', 0, '2026-09-27 15:02:29', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (763, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000010 at 2.23 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 15:02:29', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (764, 0, 2, 'New Service Request Published', 'Customer @anita_deshmukh submitted service ticket SR-2026-000314 for Electrician.', 0, '2026-09-27 15:02:31', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (765, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000011 at 2.35 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 15:02:31', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (766, 0, 7, '[EMERGENCY DISPATCH] Electrical', 'Urgent emergency ticket #EMG-2026-000011 at 1.77 km away. Guaranteed Payout: Rs. 572 (+Rs. 26 Suraksha Nidhi). Claim now!', 0, '2026-09-27 15:02:31', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (767, 0, 17, '[ARTISAN EN ROUTE] Emergency Claimed', 'Artisan @jdoe has accepted your emergency request EMG-2026-000011 and is en route! Mobile: +91-9820091001.', 0, '2026-09-27 15:02:31', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (768, 0, 7, 'Emergency Job Confirmed', 'You successfully claimed emergency dispatch #EMG-2026-000011. Destination: Chembur West, Mumbai. OTP verification required on arrival.', 0, '2026-09-27 15:02:31', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (769, 0, 1, 'Quotation Approved & Invoice Issued', 'Customer @anita_deshmukh approved quotation QTN-TEST-351764 for Rs. 8000.40. Invoice #INV-2026-000397 has been generated.', 0, '2026-09-27 15:02:31', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (770, 0, 17, 'Service Request Completed', 'Your service request EMG-TEST-SYNC05 has been marked completed by technician @jdoe.', 0, '2026-09-27 15:02:32', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (771, 0, 1, 'Service Job Completed', 'Technician @jdoe marked service ticket EMG-TEST-SYNC05 as completed.', 0, '2026-09-27 15:02:32', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (772, 0, 17, 'Arrival OTP Verified Successfully', 'Arrival OTP verified by technician @jdoe. Service is now active and in progress.', 0, '2026-09-27 15:02:32', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (773, 0, 1, 'Arrival OTP Verified', 'Technician @jdoe verified arrival OTP for request EMG-TEST-SYNC01.', 0, '2026-09-27 15:02:32', 'Info', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (774, 0, 1, 'Apex Escalated Grievance', 'Client @testcitizen1 submitted Apex Escalated ticket #51: Emergency Plumbing Leak Unresolved with Extra Surcharge.', 0, '2026-09-27 15:02:32', 'Alert', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (775, 0, 63, 'Apex Conciliation: TKT-APX-0052', 'Your escalated dispute (TKT-APX-0052) was arbitrated and resolved in your favor by the Apex Council. Restitution and corrective measures have been mandated to the primary cooperative society. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 15:02:32', 'Success', 'Normal');
INSERT INTO `notifications` (`id`, `is_archived`, `user_id`, `title`, `message`, `is_read`, `timestamp`, `type`, `priority`) VALUES (776, 0, 62, 'Apex Conciliation Notice: TKT-APX-0052', 'Dispute (TKT-APX-0052) resolved by Apex Federation. Society directive: Resolved in Customer Favor - Restitution & Work Guarantee Cleared. Notes: Full restitution approved under SahakarSeva statutory guarantee.', 0, '2026-09-27 15:02:32', 'Warning', 'Normal');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `payments`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `payments`;
CREATE TABLE `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_archived` tinyint(1) NOT NULL,
  `type` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `date` date DEFAULT NULL,
  `status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `contractor_id` int(11) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `worker_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  `invoice_number` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `receipt_path` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `signed_by_customer` tinyint(1) DEFAULT NULL,
  `signature_path` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `quotation_number` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `discount` decimal(10,2) DEFAULT NULL,
  `gst` decimal(10,2) DEFAULT NULL,
  `labour_cost` decimal(10,2) DEFAULT NULL,
  `material_cost` decimal(10,2) DEFAULT NULL,
  `worker_payout` decimal(10,2) DEFAULT NULL,
  `society_admin_fee` decimal(10,2) DEFAULT NULL,
  `federation_fee` decimal(10,2) DEFAULT NULL,
  `welfare_cess` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_payments_invoice_number` (`invoice_number`),
  KEY `customer_id` (`customer_id`),
  KEY `worker_id` (`worker_id`),
  KEY `project_id` (`project_id`),
  KEY `service_request_id` (`service_request_id`),
  KEY `ix_payments_date` (`date`),
  KEY `ix_payments_contractor_id` (`contractor_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`worker_id`) REFERENCES `workers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payments_ibfk_5` FOREIGN KEY (`service_request_id`) REFERENCES `service_requests` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `payments`
LOCK TABLES `payments` WRITE;
INSERT INTO `payments` (`id`, `is_archived`, `type`, `amount`, `date`, `status`, `contractor_id`, `customer_id`, `worker_id`, `project_id`, `service_request_id`, `invoice_number`, `description`, `receipt_path`, `signed_by_customer`, `signature_path`, `quotation_number`, `discount`, `gst`, `labour_cost`, `material_cost`, `worker_payout`, `society_admin_fee`, `federation_fee`, `welfare_cess`) VALUES (1, 0, 'revenue', 4850.00, '2026-09-22', 'Paid', 1, 17, 7, 1, 1, 'INV-2026-00101', 'Payment for DB Box Overhaul & Master Circuit Breaker Tripping Resolution (SR-2026-00101)', '/static/uploads/receipts/rec_101.pdf', 1, '/static/uploads/signatures/sig_anita.png', 'QT-2026-00101', 200.00, 572.00, 3500.00, 755.00, 4268.00, 388.00, 0.00, 194.00);
INSERT INTO `payments` (`id`, `is_archived`, `type`, `amount`, `date`, `status`, `contractor_id`, `customer_id`, `worker_id`, `project_id`, `service_request_id`, `invoice_number`, `description`, `receipt_path`, `signed_by_customer`, `signature_path`, `quotation_number`, `discount`, `gst`, `labour_cost`, `material_cost`, `worker_payout`, `society_admin_fee`, `federation_fee`, `welfare_cess`) VALUES (2, 0, 'revenue', 8600.00, '2026-09-24', 'Paid', 1, 19, 9, 2, 2, 'INV-2026-00102', 'Payment for Society Underground Booster Pump Overhaul (SR-2026-00102)', '/static/uploads/receipts/rec_102.pdf', 1, '/static/uploads/signatures/sig_deonar.png', 'QT-2026-00102', 500.00, 1242.00, 4800.00, 2845.00, 7568.00, 688.00, 0.00, 344.00);
INSERT INTO `payments` (`id`, `is_archived`, `type`, `amount`, `date`, `status`, `contractor_id`, `customer_id`, `worker_id`, `project_id`, `service_request_id`, `invoice_number`, `description`, `receipt_path`, `signed_by_customer`, `signature_path`, `quotation_number`, `discount`, `gst`, `labour_cost`, `material_cost`, `worker_payout`, `society_admin_fee`, `federation_fee`, `welfare_cess`) VALUES (3, 0, 'revenue', 11200.00, '2026-09-19', 'Paid', 2, 19, 16, 7, 7, 'INV-2026-00107', 'Payment for Security Gate Heavy Duty Welding & PU Coating (SR-2026-00107)', '/static/uploads/receipts/rec_107.pdf', 1, '/static/uploads/signatures/sig_deonar.png', NULL, 0.00, 1708.00, 6500.00, 3000.00, 9856.00, 896.00, 0.00, 448.00);
INSERT INTO `payments` (`id`, `is_archived`, `type`, `amount`, `date`, `status`, `contractor_id`, `customer_id`, `worker_id`, `project_id`, `service_request_id`, `invoice_number`, `description`, `receipt_path`, `signed_by_customer`, `signature_path`, `quotation_number`, `discount`, `gst`, `labour_cost`, `material_cost`, `worker_payout`, `society_admin_fee`, `federation_fee`, `welfare_cess`) VALUES (4, 0, 'salary', 11836.00, '2026-09-12', 'Paid', 1, NULL, 7, NULL, NULL, 'SAL-2026-001', 'Bi-weekly Guaranteed Fair Wage Settlement for John Doe', '/static/uploads/receipts/sal_jdoe.pdf', 0, NULL, NULL, 0.00, 0.00, 11836.00, 0.00, 11836.00, 0.00, 0.00, 0.00);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `quotations`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `quotations`;
CREATE TABLE `quotations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_archived` tinyint(1) NOT NULL,
  `quotation_number` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `service_request_id` int(11) NOT NULL,
  `material_list` text COLLATE utf8_unicode_ci,
  `labour_cost` decimal(10,2) DEFAULT NULL,
  `equipment_charges` decimal(10,2) DEFAULT NULL,
  `gst` decimal(10,2) DEFAULT NULL,
  `discount` decimal(10,2) DEFAULT NULL,
  `grand_total` decimal(10,2) NOT NULL,
  `terms_conditions` text COLLATE utf8_unicode_ci,
  `validity_date` date NOT NULL,
  `status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_quotations_quotation_number` (`quotation_number`),
  KEY `service_request_id` (`service_request_id`),
  KEY `ix_quotations_status` (`status`),
  CONSTRAINT `quotations_ibfk_1` FOREIGN KEY (`service_request_id`) REFERENCES `service_requests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `quotations`
LOCK TABLES `quotations` WRITE;
INSERT INTO `quotations` (`id`, `is_archived`, `quotation_number`, `service_request_id`, `material_list`, `labour_cost`, `equipment_charges`, `gst`, `discount`, `grand_total`, `terms_conditions`, `validity_date`, `status`, `created_at`) VALUES (1, 0, 'QT-2026-00101', 1, '[{"name": "Havells 16A MCB Single Pole", "qty": 1, "rate": 185.0, "total": 185.0}, {"name": "Polycab FR 2.5 sq mm Wire", "qty": 15, "rate": 28.0, "total": 420.0}, {"name": "PVC Insulation & Consumables", "qty": 1, "rate": 150.0, "total": 150.0}]', 3500.00, 250.00, 572.00, 200.00, 4850.00, 'Standard 6-month cooperative service warranty against electrical arcing.', '2026-10-27', 'Approved', '2026-09-21 14:34:55');
INSERT INTO `quotations` (`id`, `is_archived`, `quotation_number`, `service_request_id`, `material_list`, `labour_cost`, `equipment_charges`, `gst`, `discount`, `grand_total`, `terms_conditions`, `validity_date`, `status`, `created_at`) VALUES (2, 0, 'QT-2026-00102', 2, '[{"name": "SKF Industrial Deep Groove Ball Bearings", "qty": 2, "rate": 850.0, "total": 1700.0}, {"name": "Leader 1-inch Brass Ball Valve", "qty": 1, "rate": 495.0, "total": 495.0}, {"name": "Mechanical Seal & Gland Gaskets", "qty": 1, "rate": 650.0, "total": 650.0}]', 4800.00, 500.00, 1242.00, 500.00, 8600.00, 'Includes 1-year cooperative guarantee on booster pump alignment.', '2026-10-27', 'Approved', '2026-09-23 14:34:55');
INSERT INTO `quotations` (`id`, `is_archived`, `quotation_number`, `service_request_id`, `material_list`, `labour_cost`, `equipment_charges`, `gst`, `discount`, `grand_total`, `terms_conditions`, `validity_date`, `status`, `created_at`) VALUES (3, 0, 'QT-2026-00108', 8, '[{"name": "Asian Paints Damp Sheath Polymer Primer", "qty": 10, "rate": 420.0, "total": 4200.0}, {"name": "TruCare Acrylic Wall Putty (40kg)", "qty": 2, "rate": 950.0, "total": 1900.0}, {"name": "Asian Paints Royale Luxury Emulsion (20L)", "qty": 1, "rate": 5800.0, "total": 5800.0}]', 5500.00, 300.00, 2050.00, 1000.00, 18500.00, 'Includes 3-year warranty against dampness and peeling on prepared surface.', '2026-10-12', 'Pending', '2026-09-26 14:34:55');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `service_requests`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `service_requests`;
CREATE TABLE `service_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_archived` tinyint(1) NOT NULL,
  `request_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `contractor_id` int(11) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `customer_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `mobile_number` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `category` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `title` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `voice_path` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `photos` text COLLATE utf8_unicode_ci,
  `address` text COLLATE utf8_unicode_ci NOT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `status` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `assigned_worker_id` int(11) DEFAULT NULL,
  `visit_date` date DEFAULT NULL,
  `estimated_cost` decimal(10,2) DEFAULT NULL,
  `priority` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_emergency` tinyint(1) DEFAULT NULL,
  `emergency_severity` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `fixed_rate` decimal(10,2) DEFAULT NULL,
  `broadcast_status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `dispatch_radius_km` float DEFAULT NULL,
  `claimed_at` datetime DEFAULT NULL,
  `broadcast_expires_at` datetime DEFAULT NULL,
  `otp` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `otp_verified` tinyint(1) DEFAULT NULL,
  `arrived_at` datetime DEFAULT NULL,
  `preferred_time` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `progress` int(11) DEFAULT NULL,
  `completion_videos` text COLLATE utf8_unicode_ci,
  `materials_used` text COLLATE utf8_unicode_ci,
  `time_worked` decimal(10,2) DEFAULT NULL,
  `completion_date` datetime DEFAULT NULL,
  `completion_photos` text COLLATE utf8_unicode_ci,
  `completion_notes` text COLLATE utf8_unicode_ci,
  `completion_voice_path` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  `review_comment` text COLLATE utf8_unicode_ci,
  `rework_comments` text COLLATE utf8_unicode_ci,
  `payment_status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_service_requests_request_id` (`request_id`),
  KEY `customer_id` (`customer_id`),
  KEY `assigned_worker_id` (`assigned_worker_id`),
  KEY `ix_service_requests_is_emergency` (`is_emergency`),
  KEY `ix_service_requests_status` (`status`),
  KEY `ix_service_requests_contractor_id` (`contractor_id`),
  KEY `ix_service_requests_broadcast_status` (`broadcast_status`),
  CONSTRAINT `service_requests_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_requests_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `service_requests_ibfk_3` FOREIGN KEY (`assigned_worker_id`) REFERENCES `workers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `service_requests`
LOCK TABLES `service_requests` WRITE;
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (1, 0, 'SR-2026-00101', 1, 17, 'Anita Deshmukh', '+91-9820033001', 'Electrical', 'Complete DB Box Overhaul & Master Circuit Breaker Tripping Resolution', 'Main switchboard sparking on heavy appliance load. Requires full load rebalancing, replacement of burnt 32A MCB, and insulation testing across 4 circuit lines.', '/static/uploads/voice/req_101.wav', '/static/uploads/requests/db_box_burnt.jpg', 'Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077', 19.07700000, 72.90800000, 'Completed', 7, '2026-09-22', 4850.00, 'Urgent', 0, 'Standard', 4850.00, 'Claimed', 5.0, '2026-09-22 10:34:55', '2026-09-22 11:34:55', '4829', 1, '2026-09-22 10:49:55', '10:00 AM - 01:00 PM', 100, '/static/uploads/videos/db_box_test.mp4', '1x Havells 16A MCB, 15m Polycab FR 2.5 wire, PVC insulation tape', 3.50, '2026-09-22 13:34:55', '/static/uploads/completions/db_box_done.jpg', 'Replaced burnt MCB with genuine Havells 16A unit. Neutral loop corrected. Tested on 4kW heating load with Fluke meter. Megger insulation resistance > 100 Megaohms.', '/static/uploads/voice/comp_101.wav', 5, 'Exceptional cooperative service! John arrived promptly with safety gear and resolved the dangerous sparking in less than 3 hours. Transparent rates!', NULL, 'Paid', '2026-09-21 14:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (2, 0, 'SR-2026-00102', 1, 19, 'Deonar Heights Co-op Housing Society Ltd.', '+91-9820033003', 'Plumbing', 'Society Underground Booster Pump Overhaul & Non-Return Valve Replacement', 'Overhead distribution pump vibrating excessively with low discharge pressure to 7th floor wings. Needs bearing replacement and 2-inch NRV inspection.', '/static/uploads/voice/req_102.wav', '/static/uploads/requests/pump_leak.jpg', 'Deonar Heights CHS, Deonar Farm Road, Deonar, Mumbai - 400088', 19.05200000, 72.91500000, 'Completed', 9, '2026-09-24', 8600.00, 'Normal', 0, 'Standard', 8600.00, 'Claimed', 8.0, '2026-09-24 08:34:55', '2026-09-24 09:34:55', '7712', 1, '2026-09-24 09:24:55', '09:00 AM - 02:00 PM', 100, '/static/uploads/videos/pump_pressure_test.mp4', '2x SKF Ball Bearings, 1x Leader 1-inch Brass Ball Valve, Teflon gland packing', 5.00, '2026-09-24 13:34:55', '/static/uploads/completions/pump_overhaul_done.jpg', 'Replaced degraded bearings and installed new Leader brass valve. Discharge pressure restored to 4.2 Bar across all terrace risers.', '/static/uploads/voice/comp_102.wav', 5, 'Extremely reliable cooperative execution. Society committee appreciated the detailed bill of materials and digital warranty.', NULL, 'Paid', '2026-09-23 14:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (3, 0, 'SR-2026-00103', 1, 18, 'Rahul Sharma', '+91-9820033002', 'Carpentry', 'Teak Wood Main Entrance Door Alignment & Godrej High-Security Lock Fitting', 'Main entrance door rubbing against marble floor due to hinge sag. Customer requested installation of multi-bolt smart biometric lock and weather seal strip.', '/static/uploads/voice/req_103.wav', '/static/uploads/requests/door_hinge.jpg', 'B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071', 19.06100000, 72.89950000, 'In Progress', 8, '2026-09-27', 3200.00, 'Normal', 0, 'Standard', 3200.00, 'Claimed', 5.0, '2026-09-27 11:34:55', '2026-09-27 12:34:55', '9143', 1, '2026-09-27 12:49:55', '11:00 AM - 03:00 PM', 65, NULL, 'Heavy duty brass ball-bearing hinges, 4-inch screws', 2.25, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-26 14:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (4, 0, 'SR-2026-00104', 1, 20, 'Priya Nair', '+91-9820033004', 'Appliance', 'Split Air Conditioner Cooling Coil Gas Leakage Diagnosis & Refilling', 'Daikin 1.5 Ton inverter AC blowing warm air. Gas pressure drop suspected in outdoor unit flared copper joints.', '/static/uploads/voice/req_104.wav', '/static/uploads/requests/ac_leak.jpg', 'Flat 603, Green Acres CHS, Tilak Nagar, Chembur, Mumbai - 400089', 19.06300000, 72.89450000, 'Travelling', 12, '2026-09-27', 2600.00, 'Normal', 0, 'Standard', 2600.00, 'Claimed', 6.0, '2026-09-27 13:49:55', '2026-09-27 14:19:55', '3891', 0, NULL, '02:00 PM - 04:00 PM', 25, NULL, 'R32 Refrigerant canister, Nitrogen testing kit', 0.50, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-27 11:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (5, 0, 'SR-2026-00105', 2, 21, 'Vikas Patil Enterprises', '+91-9820033005', 'Civil', 'Commercial Office Restroom Anti-Skid Tile Laying & Concealed Grouting', 'Restroom floor tile renovation across 180 sq ft area. Epoxy grouting required to prevent floor seepage into lower server room.', '/static/uploads/voice/req_105.wav', '/static/uploads/requests/office_tiles.jpg', 'Office 301, Commercial Arcade, LBS Marg, Kurla West, Mumbai - 400070', 19.06700000, 72.87800000, 'Assigned', 11, '2026-09-28', 14500.00, 'Normal', 0, 'Standard', 14500.00, 'Claimed', 10.0, '2026-09-27 08:34:55', '2026-09-27 09:34:55', '6152', 0, NULL, 'Tomorrow 09:00 AM', 10, NULL, 'Kajaria 300x300 anti-skid tiles, Laticrete epoxy grout', 0.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-27 06:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (6, 0, 'SR-2026-00106', 1, 17, 'Anita Deshmukh', '+91-9820033001', 'Plumbing', 'EMERGENCY: Burst Main Kitchen Angle Cock Flooding Apartment', 'High pressure hot water line burst behind sink cabinet. Water cascading into living room. Immediate isolation and angle cock replacement required!', '/static/uploads/voice/req_106.wav', '/static/uploads/requests/emergency_leak.jpg', 'Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077', 19.07700000, 72.90800000, 'Pending', NULL, '2026-09-27', 1200.00, 'Emergency', 1, 'Critical', 1200.00, 'Broadcasting', 7.5, NULL, '2026-09-27 15:19:55', '5521', 0, NULL, 'Immediate Emergency Dispatch', 0, NULL, '1/2 inch brass angle cock, Teflon tape, heavy pipe wrench', 0.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-27 14:24:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (7, 0, 'SR-2026-00107', 2, 19, 'Deonar Heights Co-op Housing Society Ltd.', '+91-9820033003', 'Fabrication', 'Security Gate Heavy Duty Hinges Re-Welding & Anti-Rust Polyurethane Coating', 'Main entrance compound swing gate sagged due to fractured bottom pivot pin. Needs heavy steel plate gusset reinforcement and ARC welding.', '/static/uploads/voice/req_107.wav', '/static/uploads/requests/gate_broken.jpg', 'Deonar Heights CHS, Deonar Farm Road, Deonar, Mumbai - 400088', 19.05200000, 72.91500000, 'Completed', 16, '2026-09-19', 11200.00, 'Urgent', 0, 'Standard', 11200.00, 'Claimed', 8.0, '2026-09-19 06:34:55', '2026-09-19 07:34:55', '8902', 1, '2026-09-19 07:04:55', '08:30 AM - 05:00 PM', 100, '/static/uploads/videos/gate_welding.mp4', '10mm MS Plate gussets, E6013 welding electrodes, 2L Red Oxide primer', 6.50, '2026-09-19 13:34:55', '/static/uploads/completions/gate_finished.jpg', 'Fabricated new heavy-duty pivot bracket, double-pass welded joints, and applied dual coats of zinc chromate primer and black enamel paint.', '/static/uploads/voice/comp_107.wav', 4, 'Strong welding work. Needed slight touch up on inner latch paint which worker completed without hassle.', 'Touch-up coat on latch bolt applied on 2nd inspection.', 'Paid', '2026-09-18 14:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (8, 0, 'SR-2026-00108', 1, 18, 'Rahul Sharma', '+91-9820033002', 'Painting', 'Interior Hall & Dining Waterproof Coating with 2-Tone Royale Luxury Finish', 'Wall seepage near window sill caused blistering of paint. Full scraping, polymer putty touch-up, and 2 coats of Asian Paints Royale required.', '/static/uploads/voice/req_108.wav', '/static/uploads/requests/wall_peel.jpg', 'B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071', 19.06100000, 72.89950000, 'Pending', NULL, '2026-09-29', 18500.00, 'Normal', 0, 'Standard', NULL, 'None', 5.0, NULL, NULL, '1289', 0, NULL, 'Next Monday 10:00 AM', 0, NULL, 'Asian Paints Damp Sheath, TruCare wall putty, 20L Royale Luxury emulsion', 0.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-25 14:34:55');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (313, 0, 'SR-2026-000009', 1, 17, 'Anita Deshmukh', '9820011223', 'Electrician', 'Fuse Replacement', 'Fuse tripped in main board', NULL, NULL, 'Chembur Colony, Mumbai', NULL, NULL, 'Pending Review', NULL, '2026-09-30', NULL, 'Normal', 0, 'Critical', NULL, 'None', 5.0, NULL, NULL, '8791', 0, NULL, NULL, 0, NULL, NULL, 0.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-27 14:38:29');
INSERT INTO `service_requests` (`id`, `is_archived`, `request_id`, `contractor_id`, `customer_id`, `customer_name`, `mobile_number`, `category`, `title`, `description`, `voice_path`, `photos`, `address`, `latitude`, `longitude`, `status`, `assigned_worker_id`, `visit_date`, `estimated_cost`, `priority`, `is_emergency`, `emergency_severity`, `fixed_rate`, `broadcast_status`, `dispatch_radius_km`, `claimed_at`, `broadcast_expires_at`, `otp`, `otp_verified`, `arrived_at`, `preferred_time`, `progress`, `completion_videos`, `materials_used`, `time_worked`, `completion_date`, `completion_photos`, `completion_notes`, `completion_voice_path`, `rating`, `review_comment`, `rework_comments`, `payment_status`, `created_at`) VALUES (384, 0, 'SR-2026-000314', 1, 17, 'Anita Deshmukh', '9820011223', 'Electrician', 'Fuse Replacement', 'Fuse tripped in main board', NULL, NULL, 'Chembur Colony, Mumbai', NULL, NULL, 'Pending Review', NULL, '2026-09-30', NULL, 'Normal', 0, 'Critical', NULL, 'None', 5.0, NULL, NULL, '9863', 0, NULL, NULL, 0, NULL, NULL, 0.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Pending', '2026-09-27 15:02:31');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `support_tickets`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `support_tickets`;
CREATE TABLE `support_tickets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_archived` tinyint(1) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `title` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `status` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `priority` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `target_tier` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `escalation_level` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_apex_dispute` tinyint(1) DEFAULT NULL,
  `contractor_id` int(11) DEFAULT NULL,
  `contractor_name` varchar(150) COLLATE utf8_unicode_ci DEFAULT NULL,
  `resolution_notes` text COLLATE utf8_unicode_ci,
  `arbitration_action` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `contractor_id` (`contractor_id`),
  CONSTRAINT `support_tickets_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `support_tickets_ibfk_2` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `support_tickets`
LOCK TABLES `support_tickets` WRITE;
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (1, 0, 17, 'Query regarding GST invoice breakdown for housing society audit', 'Please issue a formal digitally stamped GST tax invoice copy for SR-2026-00101 to submit to our housing society auditor.', 'Resolved', 'Medium', '2026-09-23 14:34:55', '2026-09-24 14:34:55', 'society', 'society', 0, 1, 'Chembur Labour Cooperative Society Ltd.', 'Official digitally signed invoice #INV-2026-00101 emailed to anita.deshmukh@gmail.com.', 'Resolved by Society Admin');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (2, 0, 19, 'Request for Apex Federation Verification of Cooperative Bye-laws', 'Housing society management committee requests certified copy of Maharashtra State Federation bye-law affiliation.', 'Resolved', 'Low', '2026-09-17 14:34:55', '2026-09-19 14:34:55', 'apex', 'apex', 0, 1, 'Chembur Labour Cooperative Society Ltd.', 'Federation affiliation certificate MH-FED-2026 provided via document vault.', 'Verified by Apex Federation');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (3, 0, 21, 'Expedited commercial site safety clearance request', 'Commercial complex management requires worker insurance certificate (PMJJBY/PMSBY/ESIC) before site entry tomorrow morning.', 'In Progress', 'High', '2026-09-27 08:34:55', '2026-09-27 12:34:55', 'society', 'society', 0, 2, 'Kurla-Govandi Shramik Sahakari Sanstha', 'Compiling ESIC IP numbers and PMJJBY policy certificates for worker Ganesh Shinde.', 'Processing Certificate Dispatch');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (4, 0, 19, 'Dispute over inner latch spray finish and paint overspray', 'Customer noted that overspray from the compound gate primer reached the adjacent boundary flower bed and the inner latch bolt was slightly stiff.', 'Resolved', 'High', '2026-09-20 14:34:55', '2026-09-21 14:34:55', 'apex', 'apex', 1, 2, 'Kurla-Govandi Shramik Sahakari Sanstha Maryadit', 'Arbitrated by Apex State Federation Super Admin. Contractor agreed to apply secondary gloss coat and clean flower bed edging.', 'Resolved in Customer Favor');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (5, 0, 18, 'Quotation clarification on dampness treatment chemical brands', 'Customer requested confirmation that Dr Fixit / Asian Paints certified polymer primer is being used instead of standard white cement.', 'Open', 'Medium', '2026-09-26 14:34:55', '2026-09-26 14:34:55', 'apex', 'apex', 1, 1, 'Chembur Labour Cooperative Society Ltd.', 'Under review by Society Chief Engineer. Brand specification sheet shared with customer.', 'Arbitration Underway');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (41, 0, 17, 'Question regarding electrician invoice', 'Please explain the welfare cess line item on the invoice.', 'Open', 'Normal', '2026-09-27 14:38:26', '2026-09-27 14:38:26', 'society', 'society', 0, 1, 'Chembur Labour Cooperative Society Ltd.', NULL, NULL);
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (43, 0, 63, 'Electrical Panel Sparking Dispute', 'Customer disputes additional billing for circuit inspection.', 'Resolved', 'High', '2026-09-27 14:38:45', '2026-09-27 14:38:45', 'apex', 'apex', 1, 21, NULL, 'Full restitution approved under SahakarSeva statutory guarantee.', 'Resolved in Customer Favor - Restitution & Work Guarantee Cleared');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (45, 0, 63, 'Electrical Panel Sparking Dispute', 'Customer disputes additional billing for circuit inspection.', 'Resolved', 'High', '2026-09-27 14:59:08', '2026-09-27 14:59:08', 'apex', 'apex', 1, 21, NULL, 'Full restitution approved under SahakarSeva statutory guarantee.', 'Resolved in Customer Favor - Restitution & Work Guarantee Cleared');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (47, 0, 63, 'Electrical Panel Sparking Dispute', 'Customer disputes additional billing for circuit inspection.', 'Resolved', 'High', '2026-09-27 14:59:55', '2026-09-27 14:59:55', 'apex', 'apex', 1, 21, NULL, 'Full restitution approved under SahakarSeva statutory guarantee.', 'Resolved in Customer Favor - Restitution & Work Guarantee Cleared');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (49, 0, 63, 'Electrical Panel Sparking Dispute', 'Customer disputes additional billing for circuit inspection.', 'Resolved', 'High', '2026-09-27 15:02:19', '2026-09-27 15:02:19', 'apex', 'apex', 1, 21, NULL, 'Full restitution approved under SahakarSeva statutory guarantee.', 'Resolved in Customer Favor - Restitution & Work Guarantee Cleared');
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (50, 0, 17, 'Question regarding electrician invoice', 'Please explain the welfare cess line item on the invoice.', 'Open', 'Normal', '2026-09-27 15:02:29', '2026-09-27 15:02:29', 'society', 'society', 0, 1, 'Chembur Labour Cooperative Society Ltd.', NULL, NULL);
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (51, 0, 63, 'Emergency Plumbing Leak Unresolved with Extra Surcharge', 'Pipe repair was charged extra in cash and valve leaked again. Requesting Apex Council statutory refund and conciliation.', 'Open', 'Emergency', '2026-09-27 15:02:32', '2026-09-27 15:02:32', 'apex', 'apex', 1, NULL, 'Chembur Labour Cooperative Society Ltd.', NULL, NULL);
INSERT INTO `support_tickets` (`id`, `is_archived`, `customer_id`, `title`, `description`, `status`, `priority`, `created_at`, `updated_at`, `target_tier`, `escalation_level`, `is_apex_dispute`, `contractor_id`, `contractor_name`, `resolution_notes`, `arbitration_action`) VALUES (52, 0, 63, 'Electrical Panel Sparking Dispute', 'Customer disputes additional billing for circuit inspection.', 'Resolved', 'High', '2026-09-27 15:02:32', '2026-09-27 15:02:32', 'apex', 'apex', 1, 21, NULL, 'Full restitution approved under SahakarSeva statutory guarantee.', 'Resolved in Customer Favor - Restitution & Work Guarantee Cleared');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `system_announcements`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `system_announcements`;
CREATE TABLE `system_announcements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `content` text COLLATE utf8_unicode_ci NOT NULL,
  `target_role` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by_id` (`created_by_id`),
  CONSTRAINT `system_announcements_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `system_announcements`
LOCK TABLES `system_announcements` WRITE;
INSERT INTO `system_announcements` (`id`, `title`, `content`, `target_role`, `is_active`, `created_at`, `created_by_id`) VALUES (1, 'Statutory Monsoon Safety Protocols for all Cooperative Electrical Artisans', 'All primary societies and artisans must strictly adhere to Indian Standard IS 732:2019 during heavy rainfall. Ensure double earthing and use CAT-IV rated insulated gloves at all outdoor installations.', 'worker', 1, '2026-09-12 14:34:55', 1);
INSERT INTO `system_announcements` (`id`, `title`, `content`, `target_role`, `is_active`, `created_at`, `created_by_id`) VALUES (2, 'State Cooperative Federation Annual General Body Meeting (AGM) Notice', 'The 28th Annual General Body Meeting of all accredited Primary Labour Cooperatives will convene at Sahakar Bhavan, Mumbai Central on 15th October 2026. Review of Suraksha Nidhi allocations on agenda.', 'admin', 1, '2026-09-17 14:34:55', 1);
INSERT INTO `system_announcements` (`id`, `title`, `content`, `target_role`, `is_active`, `created_at`, `created_by_id`) VALUES (3, 'Subsidized Festive Home Maintenance Services for Cooperative Housing Societies', 'Cooperative housing societies across Chembur, Kurla, and Ghatkopar can now book certified pre-monsoon plumbing and electrical maintenance at pre-fixed cooperative tariffs.', 'customer', 1, '2026-09-22 14:34:55', 1);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `system_settings`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `system_settings`;
CREATE TABLE `system_settings` (
  `key` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `value` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `system_settings`
LOCK TABLES `system_settings` WRITE;
INSERT INTO `system_settings` (`key`, `value`) VALUES ('business_hours', '07:00 - 21:00 (Emergency 24x7)');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('company_address', 'Sahakar Bhavan, Chembur Naka, Chembur, Mumbai, MH 400071');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('company_email', 'support@sahakarseva.coop');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('company_name', 'SahakarSeva Cooperative Gig Federation (Mumbai Central)');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('company_phone', '+91 (022) 2522-9100');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('currency', 'Rs.');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('demo_data_seeded', 'true');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('demo_seeded', 'true');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('email_sender', 'alerts@sahakarseva.coop');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('email_smtp_host', 'smtp.sahakarseva.coop');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('email_smtp_port', '587');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('emergency_dispatch_window_mins', '15');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('global_banner', 'SahakarSeva: Certified Labour Cooperatives for Trusted Household & Community Gig Services');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('instant_dispatch_radius_km', '7.5');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('kyc_mandatory', 'true');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('language', 'en');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('lockout_contractors', 'false');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('lockout_customers', 'false');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('lockout_workers', 'false');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('maintenance_mode', 'false');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('minimum_hourly_rate', '250.00');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('service_region', 'Mumbai Eastern Suburbs (Kurla - Chembur - Govandi - Ghatkopar)');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sih_category', 'Software');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sih_department', 'National Council for Cooperative Training (NCCT)');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sih_organization', 'Ministry of Cooperation');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sih_problem_id', '26089');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sih_problem_title', 'Cooperative Gig Services Platform for Household & Community Services');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sih_theme', 'Agriculture, FoodTech & Rural Development');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sms_api_key', 'sahakar_sms_live_key_99182');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('sms_provider', 'CDAC-Gov-SMS');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('society_admin_fee_percentage', '8.0');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('statutory_min_hourly_wage', '275.00');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('tax_rate', '18.00');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('theme', 'light');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('welfare_cess_percentage', '4.0');
INSERT INTO `system_settings` (`key`, `value`) VALUES ('worker_fair_wage_percentage', '88.0');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `users`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `theme_preference` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8_unicode_ci,
  `profile_pic` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `is_archived` tinyint(1) NOT NULL,
  `two_factor_secret` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `two_factor_enabled` tinyint(1) NOT NULL,
  `dashboard_config` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `users`
LOCK TABLES `users` WRITE;
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (1, 'publisher', 'federation.admin@sahakarseva.coop', 'scrypt:32768:8:1$MVICmeAA9VHl1BnI$aa27eaba1334568153429ca39c299c2289a50dbce9f0318caa60b65ef4157345edfda15a4b835324aee74377000ef41a5ae3a53998ee3f22ea49f5e9a0e9e153', 'publisher', 'light', '+91-9820010001', 'Apex State Labour Cooperative Federation, Mumbai Central, Mumbai - 400008', '/static/uploads/profiles/publisher.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"nav_collapsed":false,"default_tab":"governance"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (2, 'admin', 'admin@chemburseva.coop', 'scrypt:32768:8:1$ozGwdtFp8giB5ZFQ$a94864510f240465b15434548ca4f1394bc848babd7145400e1bd73fec5cd4e7e0c08719718052ea604321e17e9183ea9a5798554d0c59772091d73eb97d1b5d', 'admin', 'light', '+91-9820012345', 'Plot 14, Cooperative Bhavan, Chembur Naka, Chembur, Mumbai - 400071', '/static/uploads/profiles/chembur_admin.jpg', '2026-05-30 14:34:55', 0, 'YLBKHVDELPYYP6VK65FE6S4RJMI3FPM2', 0, '{"dashboard_view":"compact","auto_refresh":true}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (3, 'kurla_admin', 'admin@kurlashramik.coop', 'scrypt:32768:8:1$QAwYIfjqQ0wjyCE5$da6d963db64d98340a7198380000dd1fe77fcc7201b6e34a097d0ad27aee07f94510cf2148b93c73a975cbc636f1f02b438c2086b9f4cf812cdfc1796192ce6c', 'admin', 'light', '+91-9820054321', 'Shramik Seva Kendra, Building 24, Nehru Nagar, Kurla East, Mumbai - 400024', '/static/uploads/profiles/kurla_admin.jpg', '2026-05-30 14:34:55', 0, 'EQUWEUG6O67ECWZ3O6KCMNWAH2LE26DO', 1, '{"dashboard_view":"full"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (4, 'ghatkopar_admin', 'admin@ghatkoparcoop.in', 'scrypt:32768:8:1$rHBJ7Zi3afMzY3b3$264c625db35af1b9715bf1b0d215895faf4aeefd2c29a78a016f11abf83b5c76129ac38d9e89fe635359040f1ab6d7d6e6b321b666799c8d615fc1aa6679f8ef', 'admin', 'light', '+91-9820078901', 'Amrut Nagar Sahakari Complex, LBS Marg, Ghatkopar West, Mumbai - 400086', '/static/uploads/profiles/ghatkopar_admin.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"dashboard_view":"compact"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (5, 'contractorflow_admin', 'contact@contractorflow.in', 'scrypt:32768:8:1$lAsRIqXznKBg5Hlc$c5ee1ef85bb4b94fc9a752a61302c499abdd6de77b28b28c6c50de7ace0488e564e5be1edff9278ffa8e930b258786696bcc6e9a4736b08296ae9786b513ba16', 'admin', 'light', '+91-9820098765', 'Suite 401, Trade Center, Dadar West, Mumbai - 400028', '/static/uploads/profiles/flow_admin.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (6, 'apex_auditor', 'audit@sahakarseva.coop', 'scrypt:32768:8:1$rX4QO2LkcoQKq0qM$e32d5678904757cf43e6b76c3aa8211f4aec04a6735a8d806855d4c1c9fcb12428d835b441486f000421f5b527bae3e0bb3d9a2388d7d42b9ea6e24e73422d4b', 'publisher', 'light', '+91-9820010099', 'Directorate of Cooperative Audit, New Administrative Building, Mumbai - 400032', '/static/uploads/profiles/auditor.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"view":"compliance"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (7, 'jdoe', 'john.doe@chemburseva.coop', 'scrypt:32768:8:1$e4H8ZF4IejkNvbVr$d40db5f757f3b42327fc708ae8cedad553bd99eeaea87db8fb743ccd005fcbe69f1e8c53dc66f2b78c927d64b96f44e4301880b33a728d47d08c25397bacb33c', 'worker', 'light', '+91-9820091001', 'Room 12, Sahakar Vasahat, Tilak Nagar, Chembur, Mumbai - 400089', '/static/uploads/profiles/worker_jdoe.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (8, 'savitri', 'savitri.kamble@chemburseva.coop', 'scrypt:32768:8:1$fn8lKubayjR4PNsP$7b88d04edbaf052b7128a6fafa596205f3ab74f886a7c121f2b87d159175339bb21fa055bb3282043432a78049d100e58e48a198d5adbbf433430e8dd5f5b888', 'worker', 'light', '+91-9820091002', 'B-204, Shramik Chawl, Govandi East, Mumbai - 400043', '/static/uploads/profiles/worker_savitri.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (9, 'jsmith', 'john.smith@chemburseva.coop', 'scrypt:32768:8:1$49V2nX4R9gtiKUgS$e99196beafc8bc1ea457bb6c8b51e3224a4af6aad72b8c1e44f687a05c91309a4b5da24da0a16b7190454532219f23d36dadb3c8610544deba0768fe5f497c96', 'worker', 'light', '+91-9820091003', 'Plot 45, Labour Camp, Ghatkopar West, Mumbai - 400086', '/static/uploads/profiles/worker_jsmith.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"general"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (10, 'ramesh', 'ramesh.shinde@kurlashramik.coop', 'scrypt:32768:8:1$AIf31uZGa7zU9hXY$6522505a9de5d6553d5d1186f660ee7b841a89590abb08240f334c52c8ec99237564113eb42f4adf3f6f6a716081402897f2a3d343ebc99eee81af07a7e27f04', 'worker', 'light', '+91-9820091004', 'Building 18, Kamgar Nagar, Kurla East, Mumbai - 400024', '/static/uploads/profiles/worker_ramesh.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (11, 'ganesh', 'ganesh.jadhav@kurlashramik.coop', 'scrypt:32768:8:1$wymDN9qIaZV4IDrO$be2ceb22dfdcf4dc9b5f31571ac4a4777aa8c7658acefb2f087d46517d7a5a6a04cc40bc6347deb32da75252a80a766029476848531e26d77318c40dafa514be', 'worker', 'light', '+91-9820091005', '102, Shramik Seva Society, Qureshi Nagar, Kurla East, Mumbai - 400024', '/static/uploads/profiles/worker_ganesh.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"evening"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (12, 'prakash', 'prakash.more@ghatkoparcoop.in', 'scrypt:32768:8:1$sPOTjHUKyo7ngjTI$62f5b1ce2974b3829b6367538c4bfd54b22ebd738cfe5d06e87665d55490f1ce7f74c16e6a17062ce3c108b0e6b1b0cc7779d141b02128b63c8da1f228a2d20c', 'worker', 'light', '+91-9820091006', '304, Sahyadri Chawl, Bhatwadi, Ghatkopar West, Mumbai - 400084', '/static/uploads/profiles/worker_prakash.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (13, 'anand', 'anand.kadam@chemburseva.coop', 'scrypt:32768:8:1$KqehOmrVPoxT4Wid$7a5683dcb865b85e08cbb53ee7db45fd843aaebeeb9c12811b93f3dff8ef301af95f18780bd737b5e00f5297a3b4160525b2af495db6b32fa51c53102b56a91b', 'worker', 'light', '+91-9820091007', 'D-11, Subhash Nagar, Chembur, Mumbai - 400071', '/static/uploads/profiles/worker_anand.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"general"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (14, 'meena', 'meena.gaikwad@chemburseva.coop', 'scrypt:32768:8:1$OnmDrnY9mlbYvjko$ffb3f997fd984b38bb64cb7d64b6e7a41b7253340be28044bd77ca77376758cafcc32effd9aeee7e179db441c876ac11a2e256a97c21464860120e4121af1b8f', 'worker', 'light', '+91-9820091008', 'Room 8, Indira Nagar Zopadpatti, Chembur East, Mumbai - 400074', '/static/uploads/profiles/worker_meena.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (15, 'sunil', 'sunil.jadhav@chemburseva.coop', 'scrypt:32768:8:1$VnTfax4vJnC5f73H$fbe647b7ca66c482635c01584d63ae8f712cbb8e08e226bd601cfa3ae9d523cbf72492ba2e0b4f1651dbaec7a4158c1da447dd946082c24c4203b717e696c9f1', 'worker', 'light', '+91-9820091009', 'C-3, Siddharth Colony, Chembur, Mumbai - 400071', '/static/uploads/profiles/worker_sunil.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (16, 'vikram', 'vikram.sawant@kurlashramik.coop', 'scrypt:32768:8:1$ULSq3RpB82AQ7Eqe$c87b294af60cc60b5e9082e69482a30df782e6bafba63d406c8556c57cd459bcd3be9d8909025c0bbcdd83abf23d804816e82e48629f0e0b8228bf9e0bc95883', 'worker', 'light', '+91-9820091010', 'Room 401, Ekta CHS, Chunabhatti, Kurla East, Mumbai - 400022', '/static/uploads/profiles/worker_vikram.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"shift":"morning"}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (17, 'anita_deshmukh', 'anita.deshmukh@gmail.com', 'scrypt:32768:8:1$UrLaqTy9TPU3L7QJ$41973e8a5d1ef293c3eaa3ba3a87f40b9987ade9e5445884ddefd2ce825aa9c0520055536220f1f0eabfa78a34778cf0bfa916b02e2d02503cc8115bc700fc26', 'customer', 'light', '+91-9820033001', 'Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077', '/static/uploads/profiles/cust_anita.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (18, 'rahul_sharma', 'rahul.sharma@outlook.com', 'scrypt:32768:8:1$5qIInztjeX4GIiI2$2d9b2ed32c29d3358e232f8d521aed70d95f0ccc8f615bf29f7caa2268da5489913b4221027a20f70dd86aa2d7f87ed86245dfe6311bf7319132d4d9fa103965', 'customer', 'light', '+91-9820033002', 'B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071', '/static/uploads/profiles/cust_rahul.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (19, 'deonar_heights_chs', 'secretary@deonarheights.org', 'scrypt:32768:8:1$8HwIGGInP8EyZSIr$5437c0938475808a55847e42f10e77b8d0dd0318dd5b1b860e19c8fe9f9b5fa132ae6d09cf52069f97d4fa5f24f4e3dfeb7e916c45d95aa7501f09bfc0132f9a', 'customer', 'light', '+91-9820033003', 'Deonar Heights Co-op Housing Society Ltd., Deonar Farm Road, Deonar, Mumbai - 400088', '/static/uploads/profiles/cust_deonar.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{"is_bulk_buyer":true}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (20, 'priya_nair', 'priya.nair@tcs.com', 'scrypt:32768:8:1$CnS6j3ikuSJorfoj$793a1eee506c7eda2466d1578732121303f0012d1e381dcf1869f0ee2374954504d15f4ccd88f32ef87c00e91aa0cfaa30893e8f669c6de3054713fe5d69c85a', 'customer', 'light', '+91-9820033004', 'Flat 603, Green Acres CHS, Tilak Nagar, Chembur, Mumbai - 400089', '/static/uploads/profiles/cust_priya.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (21, 'vikas_patil', 'vikas.patil@rediffmail.com', 'scrypt:32768:8:1$YFAfuKBOE0zeRogu$3ceabb1fd736b729e13ae6bcd9b38a9fc899775918222e7db5df29acef713c90ec380e3ba5f3cbdb5caea0dc7aa33ae045dea76cb48903c7e96dbc41da064300', 'customer', 'light', '+91-9820033005', 'Office 301, Commercial Arcade, LBS Marg, Kurla West, Mumbai - 400070', '/static/uploads/profiles/cust_vikas.jpg', '2026-05-30 14:34:55', 0, NULL, 0, '{}');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (61, 'testpubsuper', 'test_pub_super@sahakar.coop', 'scrypt:32768:8:1$eQCLzHcHJBtjrMSj$fc5e3406ef465f2cdfcff7aa6e9964b1d4851b406dfe16eb9db9dd0fb76e962ee137e2bf16ff26faae682d80e9727e8eb77ce1dbfdf66c22fc29d05acab25d15', 'publisher', 'light', NULL, NULL, NULL, '2026-09-27 14:38:45', 0, NULL, 0, NULL);
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (62, 'testconowner', 'test_con_owner@sahakar.coop', 'scrypt:32768:8:1$WmGEfQTOckzlgEhO$38a459e1a64356ecd3ef36d050ffe76e78e8c7a580c9832b12f2dcc2b6bf5e580f277f9fb12b6e69bb38fc988a518daa36522539fa7888b6eb82d153667c1aef', 'admin', 'light', NULL, NULL, NULL, '2026-09-27 14:38:45', 0, NULL, 0, NULL);
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `theme_preference`, `phone`, `address`, `profile_pic`, `created_at`, `is_archived`, `two_factor_secret`, `two_factor_enabled`, `dashboard_config`) VALUES (63, 'testcitizen1', 'test_complaint_citizen@sahakar.coop', 'scrypt:32768:8:1$bGqmzIcdaJg7PVrK$4e98543e12fc60b394dab7ef674c0c151163ae86311e98abe03d59cb41b90ba11777b8f890bb38d3b9ada274d4e7b0fa518052da46f2e721d27db4f1c0fb4f13', 'customer', 'light', '9820011223', NULL, NULL, '2026-09-27 14:38:45', 0, NULL, 0, NULL);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `welfare_transactions`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `welfare_transactions`;
CREATE TABLE `welfare_transactions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `worker_id` int(11) NOT NULL,
  `payment_id` int(11) DEFAULT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  `transaction_type` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `amount` float NOT NULL,
  `balance_after` float NOT NULL,
  `description` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `reference_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `service_request_id` (`service_request_id`),
  KEY `ix_welfare_transactions_worker_id` (`worker_id`),
  KEY `ix_welfare_transactions_created_at` (`created_at`),
  KEY `ix_welfare_transactions_payment_id` (`payment_id`),
  CONSTRAINT `welfare_transactions_ibfk_1` FOREIGN KEY (`worker_id`) REFERENCES `workers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `welfare_transactions_ibfk_2` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE SET NULL,
  CONSTRAINT `welfare_transactions_ibfk_3` FOREIGN KEY (`service_request_id`) REFERENCES `service_requests` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `welfare_transactions`
LOCK TABLES `welfare_transactions` WRITE;
INSERT INTO `welfare_transactions` (`id`, `worker_id`, `payment_id`, `service_request_id`, `transaction_type`, `amount`, `balance_after`, `description`, `reference_id`, `created_at`) VALUES (1, 7, 1, 1, 'CESS_CREDIT', 194.0, 3240.0, 'Suraksha Nidhi 4% Welfare Allocation from Invoice #INV-2026-00101', 'INV-2026-00101', '2026-09-22 14:34:55');
INSERT INTO `welfare_transactions` (`id`, `worker_id`, `payment_id`, `service_request_id`, `transaction_type`, `amount`, `balance_after`, `description`, `reference_id`, `created_at`) VALUES (2, 9, 2, 2, 'CESS_CREDIT', 344.0, 2580.0, 'Suraksha Nidhi 4% Welfare Allocation from Invoice #INV-2026-00102', 'INV-2026-00102', '2026-09-24 14:34:55');
INSERT INTO `welfare_transactions` (`id`, `worker_id`, `payment_id`, `service_request_id`, `transaction_type`, `amount`, `balance_after`, `description`, `reference_id`, `created_at`) VALUES (3, 16, 3, 7, 'CESS_CREDIT', 448.0, 2980.0, 'Suraksha Nidhi 4% Welfare Allocation from Invoice #INV-2026-00107', 'INV-2026-00107', '2026-09-19 14:34:55');
INSERT INTO `welfare_transactions` (`id`, `worker_id`, `payment_id`, `service_request_id`, `transaction_type`, `amount`, `balance_after`, `description`, `reference_id`, `created_at`) VALUES (4, 7, NULL, NULL, 'PMSBY_PREMIUM', -20.0, 3046.0, 'Automated Annual Premium Debit: Pradhan Mantri Suraksha Bima Yojana', 'PMSBY-NIC-2026-441829', '2026-08-18 14:34:55');
INSERT INTO `welfare_transactions` (`id`, `worker_id`, `payment_id`, `service_request_id`, `transaction_type`, `amount`, `balance_after`, `description`, `reference_id`, `created_at`) VALUES (5, 7, NULL, NULL, 'PMJJBY_PREMIUM', -436.0, 3066.0, 'Automated Annual Premium Debit: Pradhan Mantri Jeevan Jyoti Bima Yojana', 'PMJJBY-LIC-2026-781920', '2026-08-18 14:34:55');
INSERT INTO `welfare_transactions` (`id`, `worker_id`, `payment_id`, `service_request_id`, `transaction_type`, `amount`, `balance_after`, `description`, `reference_id`, `created_at`) VALUES (6, 8, NULL, NULL, 'WELFARE_GRANT', 2500.0, 2860.0, 'Cooperative Artisan Child Merit Education Scholarship Grant', 'COOP-EDU-GRANT-2026-01', '2026-09-02 14:34:55');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `worker_certifications`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `worker_certifications`;
CREATE TABLE `worker_certifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `worker_id` int(11) NOT NULL,
  `cert_title` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `issuing_body` varchar(150) COLLATE utf8_unicode_ci DEFAULT NULL,
  `cert_number` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `document_file` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `status` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `admin_notes` text COLLATE utf8_unicode_ci,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `worker_id` (`worker_id`),
  CONSTRAINT `worker_certifications_ibfk_1` FOREIGN KEY (`worker_id`) REFERENCES `workers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `worker_certifications`
LOCK TABLES `worker_certifications` WRITE;
INSERT INTO `worker_certifications` (`id`, `worker_id`, `cert_title`, `issuing_body`, `cert_number`, `document_file`, `issue_date`, `expiry_date`, `status`, `admin_notes`, `created_at`) VALUES (1, 7, 'National Trade Certificate (NTC) - Electrician', 'NCVT / Directorate General of Training, Govt of India', 'NTC-ELE-MH-2017-9102', '/static/uploads/certs/jdoe_ntc.pdf', '2017-12-23', NULL, 'Verified', 'Verified against NCVT MIS portal roll number database.', '2026-07-29 14:34:55');
INSERT INTO `worker_certifications` (`id`, `worker_id`, `cert_title`, `issuing_body`, `cert_number`, `document_file`, `issue_date`, `expiry_date`, `status`, `admin_notes`, `created_at`) VALUES (2, 8, 'NSDC Level 4 Master Carpenter Trade Certificate', 'National Skill Development Corporation (NSDC)', 'NSDC-CARP-2020-4102', '/static/uploads/certs/savitri_nsdc.pdf', '2020-12-27', NULL, 'Verified', 'Verified through Skill India Digital portal QR verification.', '2026-08-08 14:34:55');
INSERT INTO `worker_certifications` (`id`, `worker_id`, `cert_title`, `issuing_body`, `cert_number`, `document_file`, `issue_date`, `expiry_date`, `status`, `admin_notes`, `created_at`) VALUES (3, 9, 'NABET Master Certified Pipefitter & Sanitary Inspector', 'National Accreditation Board for Education & Training', 'NABET-PLB-2018-7712', '/static/uploads/certs/jsmith_nabet.pdf', '2019-01-27', NULL, 'Verified', 'Original trade certificate verified by Chembur Cooperative Committee.', '2026-08-03 14:34:55');
INSERT INTO `worker_certifications` (`id`, `worker_id`, `cert_title`, `issuing_body`, `cert_number`, `document_file`, `issue_date`, `expiry_date`, `status`, `admin_notes`, `created_at`) VALUES (4, 16, 'Government Industrial Training Institute (ITI) ARC Welder', 'ITI Kurla, Directorate of Vocational Education, Govt of MH', 'ITI-WLD-KURLA-2016', '/static/uploads/certs/vikram_iti.pdf', '2017-02-26', NULL, 'Verified', 'Verified with Govt ITI Kurla institutional records.', '2026-08-13 14:34:55');
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `worker_task_checklists`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `worker_task_checklists`;
CREATE TABLE `worker_task_checklists` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contractor_id` int(11) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `worker_id` int(11) DEFAULT NULL,
  `task_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `is_completed` tinyint(1) NOT NULL,
  `completed_at` datetime DEFAULT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contractor_id` (`contractor_id`),
  KEY `project_id` (`project_id`),
  KEY `worker_id` (`worker_id`),
  CONSTRAINT `worker_task_checklists_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE CASCADE,
  CONSTRAINT `worker_task_checklists_ibfk_3` FOREIGN KEY (`worker_id`) REFERENCES `workers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `worker_task_checklists`
LOCK TABLES `worker_task_checklists` WRITE;
INSERT INTO `worker_task_checklists` (`id`, `contractor_id`, `project_id`, `worker_id`, `task_name`, `description`, `is_completed`, `completed_at`, `service_request_id`) VALUES (1, 1, 1, 7, 'Isolate Main Incoming Power Supply & Tag Out', 'Ensure zero voltage using Fluke tester before handling panel wires', 1, '2026-09-22 11:34:55', 1);
INSERT INTO `worker_task_checklists` (`id`, `contractor_id`, `project_id`, `worker_id`, `task_name`, `description`, `is_completed`, `completed_at`, `service_request_id`) VALUES (2, 1, 1, 7, 'Inspect Busbar & Remove Burnt 32A MCB', 'Carefully unclip melted breaker and check DIN rail for oxidation', 1, '2026-09-22 12:04:55', 1);
INSERT INTO `worker_task_checklists` (`id`, `contractor_id`, `project_id`, `worker_id`, `task_name`, `description`, `is_completed`, `completed_at`, `service_request_id`) VALUES (3, 1, 1, 7, 'Install Genuine Havells 16A MCB & Re-torque Terminals', 'Torque terminal screws to manufacturer specification (2.5 Nm)', 1, '2026-09-22 12:49:55', 1);
INSERT INTO `worker_task_checklists` (`id`, `contractor_id`, `project_id`, `worker_id`, `task_name`, `description`, `is_completed`, `completed_at`, `service_request_id`) VALUES (4, 1, 1, 7, 'Perform Insulation & Megger Earth Leakage Test', 'Verify insulation resistance exceeds 100M Ohm to ensure safety', 1, '2026-09-22 13:34:55', 1);
INSERT INTO `worker_task_checklists` (`id`, `contractor_id`, `project_id`, `worker_id`, `task_name`, `description`, `is_completed`, `completed_at`, `service_request_id`) VALUES (5, 1, 3, 8, 'Measure Door Clearance & Unhinge Leaf', 'Mark rubbing zones on bottom edge and plane evenly', 1, '2026-09-27 12:34:55', 3);
INSERT INTO `worker_task_checklists` (`id`, `contractor_id`, `project_id`, `worker_id`, `task_name`, `description`, `is_completed`, `completed_at`, `service_request_id`) VALUES (6, 1, 3, 8, 'Mortise Pocket for High-Security Smart Lock', 'Chisel precise pocket and install heavy brass strike plate', 0, NULL, 3);
UNLOCK TABLES;

-- --------------------------------------------------------
-- Table structure for `workers`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `workers`;
CREATE TABLE `workers` (
  `id` int(11) NOT NULL,
  `is_archived` tinyint(1) NOT NULL,
  `contractor_id` int(11) DEFAULT NULL,
  `skills` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `experience_years` int(11) DEFAULT NULL,
  `salary_rate` decimal(10,2) DEFAULT NULL,
  `performance_rating` decimal(3,2) DEFAULT NULL,
  `availability_status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `verification_status` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `id_proof_file` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `emergency_contact` text COLLATE utf8_unicode_ci,
  `bank_details` text COLLATE utf8_unicode_ci,
  `documents_paths` text COLLATE utf8_unicode_ci,
  `tier` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `tier_updated_at` datetime DEFAULT NULL,
  `gps_lat` decimal(10,8) DEFAULT NULL,
  `gps_lng` decimal(11,8) DEFAULT NULL,
  `gps_last_updated` datetime DEFAULT NULL,
  `insurance_provider` varchar(120) COLLATE utf8_unicode_ci DEFAULT NULL,
  `insurance_policy_no` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `insurance_valid_until` date DEFAULT NULL,
  `insurance_coverage_amount` decimal(12,2) DEFAULT NULL,
  `coop_welfare_fund_enrolled` tinyint(1) DEFAULT NULL,
  `welfare_fund_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `welfare_balance` float DEFAULT NULL,
  `pmjjby_id` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `pmjjby_status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `pmjjby_renewal_date` date DEFAULT NULL,
  `pmsby_id` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `pmsby_status` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `pmsby_renewal_date` date DEFAULT NULL,
  `esic_ip_number` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_workers_contractor_id` (`contractor_id`),
  CONSTRAINT `workers_ibfk_1` FOREIGN KEY (`id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `workers_ibfk_2` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping data for table `workers`
LOCK TABLES `workers` WRITE;
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (7, 0, 1, 'Master Electrical Wireman, High-Voltage Panel DB Maintenance, Inverter Overhaul', 12, 650.00, 5.00, 'available', 1, 'approved', '/static/uploads/ids/jdoe_aadhaar.pdf', 'Sunita Doe (Wife) +91-9820091091', 'Union Bank of India, Chembur Br, A/C: 382901928401, IFSC: UBIN0538299', '/static/uploads/docs/jdoe_certs.zip', 'Master Artisan', '2026-08-28 14:34:55', 19.06260000, 72.87970000, '2026-09-27 14:19:55', 'The New India Assurance Co. Ltd.', 'NIA-MUM-COOP-2026-00124', '2027-07-04', 500000.00, 1, 'WF-CHEMBUR-2026-007', 3240.0, 'PMJJBY-LIC-2026-781920', 'Active', '2027-05-25', 'PMSBY-NIC-2026-441829', 'Active', '2027-05-25', '3100984521');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (8, 0, 1, 'Carpentry, Teak Wood Cabinetry, Locksmithing, Door Alignment, Modular Kitchens', 8, 550.00, 3.00, 'busy', 1, 'approved', '/static/uploads/ids/savitri_aadhaar.pdf', 'Mahadev Kamble (Husband) +91-9820091092', 'State Bank of India, Govandi Br, A/C: 20192840192, IFSC: SBIN0001053', '/static/uploads/docs/savitri_certs.zip', 'Master Artisan', '2026-08-28 14:34:55', 19.05500000, 72.90500000, '2026-09-27 14:19:55', 'National Insurance Company Ltd.', 'NIC-MUM-COOP-2026-00561', '2027-04-05', 500000.00, 1, 'WF-CHEMBUR-2026-008', 2860.0, 'PMJJBY-LIC-2026-781921', 'Active', '2027-03-26', 'PMSBY-NIC-2026-441830', 'Active', '2027-03-26', '3100984522');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (9, 0, 1, 'Plumbing & Sanitaryware, Concealed Piping, Booster Pumps, Water Tank Sanitation', 10, 600.00, 4.90, 'available', 1, 'approved', '/static/uploads/ids/jsmith_aadhaar.pdf', 'Pooja Smith (Wife) +91-9820091093', 'Bank of Baroda, Chembur Br, A/C: 049281029481, IFSC: BARB0CHEMBU', '/static/uploads/docs/jsmith_certs.zip', 'Master Artisan', '2026-08-28 14:34:55', 19.06400000, 72.89700000, '2026-09-27 14:19:55', 'The New India Assurance Co. Ltd.', 'NIA-MUM-COOP-2026-00125', '2027-08-03', 500000.00, 1, 'WF-CHEMBUR-2026-009', 2580.0, 'PMJJBY-LIC-2026-781922', 'Active', '2027-06-14', 'PMSBY-NIC-2026-441831', 'Active', '2027-06-14', '3100984523');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (10, 0, 2, 'Masonry, Waterproofing, Concrete Repair, Plastering, Anti-Seepage Chemical Injections', 15, 600.00, 4.80, 'available', 1, 'approved', '/static/uploads/ids/ramesh_aadhaar.pdf', 'Lata Shinde (Wife) +91-9820091094', 'Maharashtra State Co-op Bank, Kurla Br, A/C: 11029481029, IFSC: MSCB0000014', '/static/uploads/docs/ramesh_certs.zip', 'Master Artisan', '2026-08-28 14:34:55', 19.06900000, 72.88000000, '2026-09-27 14:19:55', 'United India Insurance Co.', 'UII-MUM-COOP-2026-00812', '2027-02-24', 500000.00, 1, 'WF-KURLA-2026-010', 3890.0, 'PMJJBY-LIC-2026-781923', 'Active', '2027-01-25', 'PMSBY-NIC-2026-441832', 'Active', '2027-01-25', '3100984524');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (11, 0, 2, 'Civil Tiling, Marble Laying, Terrace Waterproofing, Grouting', 6, 500.00, 4.75, 'available', 1, 'approved', '/static/uploads/ids/ganesh_aadhaar.pdf', 'Sarika Jadhav (Wife) +91-9820091095', 'Canara Bank, Kurla Br, A/C: 294810294810, IFSC: CNRB0002948', '/static/uploads/docs/ganesh_certs.zip', 'Skilled Craftsman', '2026-08-28 14:34:55', 19.07100000, 72.88500000, '2026-09-27 14:19:55', 'United India Insurance Co.', 'UII-MUM-COOP-2026-00813', '2027-02-24', 300000.00, 1, 'WF-KURLA-2026-011', 1740.0, 'PMJJBY-LIC-2026-781924', 'Active', '2027-01-25', 'PMSBY-NIC-2026-441833', 'Active', '2027-01-25', '3100984525');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (12, 0, 4, 'Appliance Repair, Inverter AC Gas Filling, Washing Machine PCB Diagnosis', 7, 550.00, 4.88, 'busy', 1, 'approved', '/static/uploads/ids/prakash_aadhaar.pdf', 'Rekha More (Wife) +91-9820091096', 'Punjab National Bank, Ghatkopar Br, A/C: 092810294810, IFSC: PUNB0092800', '/static/uploads/docs/prakash_certs.zip', 'Skilled Craftsman', '2026-08-28 14:34:55', 19.08500000, 72.90800000, '2026-09-27 14:19:55', 'Oriental Insurance Company Ltd.', 'OIC-MUM-COOP-2026-00339', '2027-05-05', 300000.00, 1, 'WF-GHATKOPAR-2026-012', 2150.0, 'PMJJBY-LIC-2026-781925', 'Active', '2027-04-05', 'PMSBY-NIC-2026-441834', 'Active', '2027-04-05', '3100984526');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (13, 0, 1, 'Interior & Exterior Painting, Texture Finishes, Damp Wall Polymer Plaster', 5, 450.00, 4.78, 'available', 1, 'approved', '/static/uploads/ids/anand_aadhaar.pdf', 'Shobha Kadam (Mother) +91-9820091097', 'Union Bank of India, Chembur Br, A/C: 382901928405, IFSC: UBIN0538299', '/static/uploads/docs/anand_certs.zip', 'Skilled Craftsman', '2026-08-28 14:34:55', 19.05800000, 72.89500000, '2026-09-27 14:19:55', 'The New India Assurance Co. Ltd.', 'NIA-MUM-COOP-2026-00126', '2027-08-03', 300000.00, 1, 'WF-CHEMBUR-2026-013', 1420.0, 'PMJJBY-LIC-2026-781926', 'Active', '2027-06-14', 'PMSBY-NIC-2026-441835', 'Active', '2027-06-14', '3100984527');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (14, 0, 1, 'Domestic Helper & Housekeeping, Deep House Cleaning, Sanitation, Floor Scrubbing', 3, 400.00, 4.93, 'available', 1, 'approved', '/static/uploads/ids/meena_aadhaar.pdf', 'Prakash Gaikwad (Husband) +91-9820091098', 'Bank of India, Chembur Br, A/C: 00192840192, IFSC: BKID0000019', '/static/uploads/docs/meena_certs.zip', 'Skilled Craftsman', '2026-08-28 14:34:55', 19.05400000, 72.89900000, '2026-09-27 14:19:55', 'National Insurance Company Ltd.', 'NIC-MUM-COOP-2026-00928', '2027-04-25', 300000.00, 1, 'WF-CHEMBUR-2026-014', 1280.0, 'PMJJBY-LIC-2026-781927', 'Active', '2027-02-24', 'PMSBY-NIC-2026-441836', 'Active', '2027-02-24', '3100984528');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (15, 0, 1, 'Gardener & Caregiver Assistant, Horticulture, Lawn Maintenance, Trainee Plumbing', 1, 350.00, 4.70, 'pending_verification', 0, 'pending', '/static/uploads/ids/sunil_aadhaar.pdf', 'Vasant Jadhav (Father) +91-9820091099', 'State Bank of India, Chembur Br, A/C: 30192840192, IFSC: SBIN0000301', NULL, 'Apprentice', '2026-08-28 14:34:55', 19.06000000, 72.89600000, '2026-09-27 14:19:55', 'The New India Assurance Co. Ltd.', 'NIA-PENDING-2026', '2026-12-26', 200000.00, 1, 'WF-CHEMBUR-2026-015', 350.0, 'PMJJBY-PENDING', 'Pending', '2026-11-26', 'PMSBY-PENDING', 'Pending', '2026-11-26', '3100984529');
INSERT INTO `workers` (`id`, `is_archived`, `contractor_id`, `skills`, `experience_years`, `salary_rate`, `performance_rating`, `availability_status`, `is_verified`, `verification_status`, `id_proof_file`, `emergency_contact`, `bank_details`, `documents_paths`, `tier`, `tier_updated_at`, `gps_lat`, `gps_lng`, `gps_last_updated`, `insurance_provider`, `insurance_policy_no`, `insurance_valid_until`, `insurance_coverage_amount`, `coop_welfare_fund_enrolled`, `welfare_fund_id`, `welfare_balance`, `pmjjby_id`, `pmjjby_status`, `pmjjby_renewal_date`, `pmsby_id`, `pmsby_status`, `pmsby_renewal_date`, `esic_ip_number`) VALUES (16, 0, 2, 'Verified Commercial Driver, Transport Logistics, ARC & TIG Welding Fabrication', 9, 700.00, 4.94, 'available', 1, 'approved', '/static/uploads/ids/vikram_aadhaar.pdf', 'Suvarna Sawant (Wife) +91-9820091000', 'IDBI Bank, Kurla Br, A/C: 01928401920, IFSC: IBKL0000192', '/static/uploads/docs/vikram_certs.zip', 'Master Artisan', '2026-08-28 14:34:55', 19.07300000, 72.88100000, '2026-09-27 14:19:55', 'United India Insurance Co.', 'UII-MUM-COOP-2026-00820', '2027-06-24', 500000.00, 1, 'WF-KURLA-2026-016', 2980.0, 'PMJJBY-LIC-2026-781928', 'Active', '2027-05-15', 'PMSBY-NIC-2026-441837', 'Active', '2027-05-15', '3100984530');
UNLOCK TABLES;

SET FOREIGN_KEY_CHECKS=1;
COMMIT;
