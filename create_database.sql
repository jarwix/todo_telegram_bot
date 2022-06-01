CREATE SCHEMA `telegramtaskbot` DEFAULT CHARACTER SET utf8mb4 ;

CREATE TABLE `telegramtaskbot`.`tasksdata` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `idtg` VARCHAR(100) NOT NULL,
  `tasks` VARCHAR(45) NOT NULL,
  `time` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`));
);
