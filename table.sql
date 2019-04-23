CREATE TABLE `items` (
	`provider` ENUM('dorus','cmlt') NOT NULL COLLATE 'utf8_bin',
	`external_id` VARCHAR(50) NOT NULL COLLATE 'utf8_bin',
	`date` DATETIME NULL DEFAULT NULL,
	`title` VARCHAR(160) NOT NULL COLLATE 'utf8_bin',
	`description` TEXT NOT NULL COLLATE 'utf8_bin',
	`price` BIGINT(20) NULL DEFAULT NULL,
	`address` TEXT NOT NULL COLLATE 'utf8_bin',
	`coordinates` POINT NULL DEFAULT NULL,
	`ext_category` VARCHAR(50) NOT NULL COLLATE 'utf8_bin',
	`images` TEXT NULL COLLATE 'utf8_bin',
	`videos` TEXT NULL COLLATE 'utf8_bin',
	`site` TEXT NULL COLLATE 'utf8_bin',
	`details` TEXT NULL COLLATE 'utf8_bin',
	`author_external_id` VARCHAR(50) NOT NULL COLLATE 'utf8_bin',
	`author` VARCHAR(255) NOT NULL COLLATE 'utf8_bin',
	`phone` CHAR(10) NOT NULL COLLATE 'utf8_bin',
	`original_url` TEXT NOT NULL COLLATE 'utf8_bin',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`processed` TINYINT(4) NOT NULL DEFAULT '0',
	INDEX `identify` (`external_id`, `provider`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
;
