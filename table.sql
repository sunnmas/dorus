CREATE TABLE `items` (
	`provider` ENUM('dorus','cmlt','phtdsk','irr','cian') NOT NULL COLLATE 'utf8_bin',
	`external_id` VARCHAR(50) NOT NULL COLLATE 'utf8_bin',
	`date` DATETIME NOT NULL,
	`title` VARCHAR(160) NOT NULL COLLATE 'utf8_bin',
	`description` TEXT NOT NULL COLLATE 'utf8_bin',
	`price` BIGINT(20) NOT NULL DEFAULT '0',
	`price_unit` ENUM('₽','₽ в год','₽ в месяц','₽ в неделю','₽ в сутки','₽ в час','₽ за 10 шт.','₽ за кг','₽ за комплект','₽ за м','₽ за м²','₽ за м³','₽ за т','₽ за штуку') NOT NULL DEFAULT '₽' COLLATE 'utf8_bin',
	`address` TEXT NULL COLLATE 'utf8_bin',
	`coordinates` POINT NULL DEFAULT NULL,
	`category` VARCHAR(50) NOT NULL COLLATE 'utf8_bin',
	`images` TEXT NULL COLLATE 'utf8_bin',
	`videos` TEXT NULL COLLATE 'utf8_bin',
	`site` TEXT NULL COLLATE 'utf8_bin',
	`details` TEXT NULL COLLATE 'utf8_bin',
	`author_external_id` VARCHAR(50) NOT NULL COLLATE 'utf8_bin',
	`author` VARCHAR(255) NOT NULL COLLATE 'utf8_bin',
	`company` TINYINT(1) NOT NULL DEFAULT '0',
	`phone` CHAR(11) NOT NULL COLLATE 'utf8_bin',
	`original_url` TEXT NOT NULL COLLATE 'utf8_bin',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`processed` TINYINT(4) NOT NULL DEFAULT '0' COMMENT '3 разряда. 2 - продакшн, 1 - стейдж, 0 - девелоп',
	`actual` TINYINT(1) NOT NULL DEFAULT '1',
	UNIQUE INDEX `identify` (`external_id`, `provider`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
;
