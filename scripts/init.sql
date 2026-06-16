-- AutoML SaaS - Initial DB Setup
-- This runs automatically when MySQL container first starts

CREATE DATABASE IF NOT EXISTS automl_saas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE automl_saas;

-- Grant privileges
GRANT ALL PRIVILEGES ON automl_saas.* TO 'automl_user'@'%';
FLUSH PRIVILEGES;
