CREATE TABLE `UserRecipeRating`(
    `user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `recipe_id` BIGINT NOT NULL,
    `(user_id, recipe_id)` BIGINT NOT NULL,
    `recipe_rating` SMALLINT NOT NULL,
    PRIMARY KEY(`(user_id, recipe_id)`)
);
CREATE TABLE `UserRecipeFavorite`(
    `user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `recipe_id` BIGINT NOT NULL,
    `(user_id, recipe_id)` BIGINT NOT NULL,
    PRIMARY KEY(`(user_id, recipe_id)`)
);
CREATE TABLE `UserRecipeAttempt`(
    `user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `recipe_id` BIGINT NOT NULL,
    `(user_id, recipe_id)` BIGINT NOT NULL,
    `times_attempted` BIGINT NOT NULL,
    PRIMARY KEY(`(user_id, recipe_id)`)
);
CREATE TABLE `Recipe`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `title` MEDIUMTEXT NOT NULL,
    `tags` BIGINT NULL,
    `description_short` MEDIUMTEXT NOT NULL,
    `description_full` LONGTEXT NULL,
    `difficulty` SMALLINT NOT NULL,
    `user_rating` SMALLINT NULL,
    `preparation_time` TEXT NOT NULL,
    `allergies` TEXT NULL,
    `ingredients` JSON NOT NULL,
    `instructions` JSON NOT NULL,
    `views` BIGINT NOT NULL DEFAULT '0',
    `attempts` BIGINT NOT NULL DEFAULT '0',
    `created_by` BIGINT NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL
);
ALTER TABLE
    `Recipe` ADD INDEX `recipe_ingredients_index`(`ingredients`);
CREATE TABLE `User`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `username` TEXT NOT NULL,
    `email` TEXT NOT NULL,
    `password` LONGTEXT NOT NULL,
    `image` BLOB NULL DEFAULT 'default.jpg',
    `recipes_authored` BIGINT NULL,
    `created_at` TIMESTAMP NOT NULL,
    `last_login` TIMESTAMP NOT NULL
);
ALTER TABLE
    `User` ADD INDEX `user_recipes_authored_index`(`recipes_authored`);
ALTER TABLE
    `User` ADD CONSTRAINT `user_recipes_authored_foreign` FOREIGN KEY(`recipes_authored`) REFERENCES `Recipe`(`id`);
ALTER TABLE
    `UserRecipeFavorite` ADD CONSTRAINT `userrecipefavorite_recipe_id_foreign` FOREIGN KEY(`recipe_id`) REFERENCES `Recipe`(`id`);
ALTER TABLE
    `Recipe` ADD CONSTRAINT `recipe_created_by_foreign` FOREIGN KEY(`created_by`) REFERENCES `User`(`id`);
ALTER TABLE
    `UserRecipeAttempt` ADD CONSTRAINT `userrecipeattempt_recipe_id_foreign` FOREIGN KEY(`recipe_id`) REFERENCES `Recipe`(`id`);
ALTER TABLE
    `UserRecipeAttempt` ADD CONSTRAINT `userrecipeattempt_user_id_foreign` FOREIGN KEY(`user_id`) REFERENCES `User`(`id`);
ALTER TABLE
    `UserRecipeFavorite` ADD CONSTRAINT `userrecipefavorite_user_id_foreign` FOREIGN KEY(`user_id`) REFERENCES `User`(`id`);
ALTER TABLE
    `UserRecipeRating` ADD CONSTRAINT `userreciperating_recipe_id_foreign` FOREIGN KEY(`recipe_id`) REFERENCES `Recipe`(`id`);
ALTER TABLE
    `UserRecipeRating` ADD CONSTRAINT `userreciperating_user_id_foreign` FOREIGN KEY(`user_id`) REFERENCES `User`(`id`);