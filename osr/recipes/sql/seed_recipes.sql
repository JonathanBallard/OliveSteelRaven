-- ==========================================================
-- RecipeBook seed: 15 common recipes + ingredients
-- Postgres / psql friendly
-- ==========================================================

BEGIN;

-- Change this if needed (owner_user_id is required)
-- Commented out because we're attaching this to management command
-- \set owner_id 1

-- -----------------------------
-- 1) Ingredients upsert helper
-- -----------------------------
-- We'll normalize ingredient keys in SQL roughly like:
-- lower(trim + collapse whitespace). This should match your normalize_name()
-- closely enough for typical ingredients.
WITH ingredient_src(name) AS (
  VALUES
    -- Pantry basics
    ('Salt'), ('Black Pepper'), ('Olive Oil'), ('Vegetable Oil'), ('Butter'),
    ('All-Purpose Flour'), ('Sugar'), ('Brown Sugar'), ('Baking Powder'), ('Baking Soda'),
    ('Vanilla Extract'), ('Cinnamon'),
    ('Milk'), ('Eggs'), ('Cheddar Cheese'), ('Parmesan Cheese'),
    ('Garlic'), ('Onion'), ('Lemon'),
    ('Chicken Breast'), ('Ground Beef'), ('Bacon'),
    ('Spaghetti'), ('Rice'),
    ('Tomato Sauce'), ('Diced Tomatoes'), ('Tomato Paste'),
    ('Chicken Broth'),
    ('Romaine Lettuce'), ('Croutons'),
    ('Tortillas'), ('Salsa'),
    ('Taco Seasoning'), ('Cumin'), ('Chili Powder'),
    ('Soy Sauce'), ('Ginger'),
    ('Carrots'), ('Celery'),
    ('Potatoes'), ('Sour Cream'),
    ('Bread'), ('Mayonnaise'), ('Mustard'),
    ('Bananas'), ('Chocolate Chips'),
    ('Oats'), ('Honey'),
    ('Peanut Butter'), ('Jelly'),
    ('Mixed Vegetables (Frozen)'),
    ('Shredded Mozzarella'),
    ('Basil (Dried)'),
    ('Oregano (Dried)')
),
ingredient_upsert AS (
  INSERT INTO ingredients (name, name_normalized)
  SELECT
    -- display name (Title Case-ish; DB doesn't enforce, but nice for UI)
    initcap(regexp_replace(trim(name), '\s+', ' ', 'g')) AS name,
    -- normalized key
    lower(regexp_replace(trim(name), '\s+', ' ', 'g')) AS name_normalized
  FROM ingredient_src
  ON CONFLICT (name_normalized)
  DO UPDATE SET name = EXCLUDED.name
  RETURNING id, name_normalized
)

-- --------------------------------
-- 2) Recipes insert (15 recipes)
-- --------------------------------
, recipe_src AS (
  SELECT * FROM (VALUES
    -- title, category_id, prep_time_minutes, difficulty, short_description, instructions
    ('Scrambled Eggs',                1, 10, 1,
      'Fluffy scrambled eggs—fast, reliable, and hard to mess up (famous last words).',
      '1) Beat eggs with a pinch of salt and pepper.\n2) Melt butter in a pan on low-medium.\n3) Add eggs and stir gently.\n4) Remove when just set; they keep cooking off-heat.'),

    ('Pancakes',                      1, 20, 2,
      'Classic pancakes with a golden exterior and soft middle.',
      '1) Mix dry ingredients.\n2) Whisk wet ingredients.\n3) Combine gently (small lumps are fine).\n4) Cook on a lightly oiled griddle until bubbles form, then flip.'),

    ('French Toast',                  2, 20, 2,
      'Crispy edges, custardy middle—breakfast pretending to be dessert.',
      '1) Whisk eggs, milk, cinnamon, and vanilla.\n2) Dip bread slices briefly.\n3) Cook in buttered pan until browned on both sides.\n4) Serve with syrup or fruit.'),

    ('BLT Sandwich',                 12, 15, 2,
      'Bacon, lettuce, tomato—simple, iconic, and somehow always better than expected.',
      '1) Cook bacon until crisp.\n2) Toast bread.\n3) Spread mayo.\n4) Layer lettuce, tomato, bacon.\n5) Slice and serve.'),

    ('Peanut Butter & Jelly',        12,  5, 1,
      'The undefeated lunchtime champion.',
      '1) Spread peanut butter on one slice.\n2) Spread jelly on the other.\n3) Press together.\n4) Optional: cut diagonally for +10% nostalgia.'),

    ('Spaghetti with Marinara',      21, 25, 2,
      'Straightforward spaghetti with a simple marinara sauce.',
      '1) Boil salted water and cook spaghetti.\n2) Warm tomato sauce with garlic and herbs.\n3) Toss pasta with sauce.\n4) Top with parmesan.'),

    ('Tacos (Ground Beef)',          22, 25, 2,
      'Weeknight tacos—fast, customizable, and universally photogenic.',
      '1) Brown ground beef with onion.\n2) Add taco seasoning + a splash of water.\n3) Warm tortillas.\n4) Assemble with salsa and toppings.'),

    ('Chicken Stir Fry',             23, 25, 3,
      'Quick stir fry with chicken and mixed vegetables.',
      '1) Slice chicken thin.\n2) Sear chicken in hot pan.\n3) Add veggies.\n4) Add soy sauce + ginger + garlic.\n5) Serve over rice.'),

    ('Caesar Salad',                  9, 15, 2,
      'Crisp romaine with parmesan and croutons.',
      '1) Chop romaine.\n2) Toss with dressing.\n3) Add croutons and parmesan.\n4) Finish with black pepper and lemon.'),

    ('Tomato Soup',                   8, 30, 2,
      'Comforting tomato soup—perfect for dunking anything bread-shaped.',
      '1) Sauté onion and garlic in olive oil.\n2) Add diced tomatoes + broth.\n3) Simmer 15–20 minutes.\n4) Blend (optional).\n5) Season to taste.'),

    ('Chicken Noodle Soup (Simple)',  8, 40, 2,
      'Simple chicken soup with carrots and celery.',
      '1) Simmer broth with onion, carrots, celery.\n2) Add cooked chicken.\n3) Simmer 10–15 minutes.\n4) Season with salt and pepper.'),

    ('Mashed Potatoes',              10, 35, 2,
      'Creamy mashed potatoes with butter and milk.',
      '1) Boil peeled potatoes until tender.\n2) Drain well.\n3) Mash with butter and warm milk.\n4) Season generously.'),

    ('Mac and Cheese (Stovetop)',    20, 25, 3,
      'Stovetop mac and cheese with cheddar—classic comfort food.',
      '1) Cook pasta.\n2) Warm milk with butter.\n3) Stir in cheddar until melted.\n4) Combine with pasta.\n5) Season with salt and pepper.'),

    ('Chocolate Chip Cookies',       27, 35, 3,
      'Classic chewy chocolate chip cookies.',
      '1) Cream butter + sugars.\n2) Mix in eggs + vanilla.\n3) Stir in flour + baking soda.\n4) Fold in chocolate chips.\n5) Bake until edges set.'),

    ('Banana Bread',                 26, 70, 3,
      'Moist banana bread—ideal for using up overripe bananas.',
      '1) Mash bananas.\n2) Mix wet ingredients.\n3) Mix dry ingredients separately.\n4) Combine gently.\n5) Bake until a toothpick comes out mostly clean.')
  ) AS t(title, category_id, prep_time_minutes, difficulty, short_description, instructions)
),
recipe_insert AS (
  INSERT INTO recipes (owner_user_id, title, category_id, prep_time_minutes, difficulty, short_description, long_description, instructions)
  SELECT
    :'owner_id'::bigint,
    r.title,
    r.category_id,
    r.prep_time_minutes,
    r.difficulty,
    r.short_description,
    ''::text AS long_description,
    r.instructions
  FROM recipe_src r
  WHERE NOT EXISTS (
    SELECT 1 FROM recipes x
    WHERE x.owner_user_id = :'owner_id'::bigint
      AND x.title = r.title
  )
  RETURNING id, title
)

-- ------------------------------------------------------
-- 3) Recipe ingredients (with line_order per recipe)
-- ------------------------------------------------------
INSERT INTO recipe_ingredients (recipe_id, ingredient_id, line_order, quantity, unit_text, prep_note)
SELECT
  rec.id AS recipe_id,
  ing.id AS ingredient_id,
  ri.line_order,
  ri.quantity,
  ri.unit_text,
  ri.prep_note
FROM recipe_insert rec
JOIN LATERAL (
  -- For each inserted recipe title, define its ingredient lines.
  SELECT * FROM (
    VALUES
      -- Scrambled Eggs
      ('Scrambled Eggs', 1, 4.000, 'large', NULL, 'Eggs'),
      ('Scrambled Eggs', 2, 1.000, 'tbsp',  NULL, 'Butter'),
      ('Scrambled Eggs', 3, NULL,  NULL,    NULL, 'Salt'),
      ('Scrambled Eggs', 4, NULL,  NULL,    NULL, 'Black Pepper'),
      ('Scrambled Eggs', 5, 2.000, 'tbsp',  NULL, 'Milk'),

      -- Pancakes
      ('Pancakes', 1, 1.500, 'cups', NULL, 'All-Purpose Flour'),
      ('Pancakes', 2, 1.000, 'tbsp', NULL, 'Sugar'),
      ('Pancakes', 3, 2.000, 'tsp',  NULL, 'Baking Powder'),
      ('Pancakes', 4, 1.000, 'cup',  NULL, 'Milk'),
      ('Pancakes', 5, 1.000, 'large',NULL, 'Eggs'),
      ('Pancakes', 6, 2.000, 'tbsp', NULL, 'Butter'),

      -- French Toast
      ('French Toast', 1, 2.000, 'large', NULL, 'Eggs'),
      ('French Toast', 2, 0.750, 'cup',  NULL, 'Milk'),
      ('French Toast', 3, 1.000, 'tsp',  NULL, 'Cinnamon'),
      ('French Toast', 4, 1.000, 'tsp',  NULL, 'Vanilla Extract'),
      ('French Toast', 5, 6.000, 'slices',NULL, 'Bread'),
      ('French Toast', 6, 1.000, 'tbsp', NULL, 'Butter'),

      -- BLT Sandwich
      ('BLT Sandwich', 1, 8.000, 'slices',NULL, 'Bacon'),
      ('BLT Sandwich', 2, 4.000, 'slices',NULL, 'Bread'),
      ('BLT Sandwich', 3, 2.000, 'tbsp', NULL, 'Mayonnaise'),
      ('BLT Sandwich', 4, 1.000, 'head', NULL, 'Romaine Lettuce'),
      ('BLT Sandwich', 5, 1.000, 'whole',NULL, 'Diced Tomatoes'),

      -- PB&J
      ('Peanut Butter & Jelly', 1, 2.000, 'slices', NULL, 'Bread'),
      ('Peanut Butter & Jelly', 2, 2.000, 'tbsp',   NULL, 'Peanut Butter'),
      ('Peanut Butter & Jelly', 3, 2.000, 'tbsp',   NULL, 'Jelly'),

      -- Spaghetti Marinara
      ('Spaghetti with Marinara', 1, 12.000, 'oz',  NULL, 'Spaghetti'),
      ('Spaghetti with Marinara', 2, 2.000,  'cups',NULL, 'Tomato Sauce'),
      ('Spaghetti with Marinara', 3, 2.000,  'cloves', 'minced', 'Garlic'),
      ('Spaghetti with Marinara', 4, 1.000,  'tsp', NULL, 'Basil (Dried)'),
      ('Spaghetti with Marinara', 5, 0.500,  'tsp', NULL, 'Oregano (Dried)'),
      ('Spaghetti with Marinara', 6, NULL,   NULL,  NULL, 'Salt'),
      ('Spaghetti with Marinara', 7, 0.250,  'cup', NULL, 'Parmesan Cheese'),

      -- Tacos (Ground Beef)
      ('Tacos (Ground Beef)', 1, 1.000, 'lb',  NULL, 'Ground Beef'),
      ('Tacos (Ground Beef)', 2, 0.500, 'whole', 'diced', 'Onion'),
      ('Tacos (Ground Beef)', 3, 1.000, 'packet',NULL, 'Taco Seasoning'),
      ('Tacos (Ground Beef)', 4, 8.000, 'small', NULL, 'Tortillas'),
      ('Tacos (Ground Beef)', 5, 0.500, 'cup',  NULL, 'Salsa'),
      ('Tacos (Ground Beef)', 6, 1.000, 'cup',  NULL, 'Cheddar Cheese'),
      ('Tacos (Ground Beef)', 7, 0.250, 'cup',  NULL, 'Sour Cream'),

      -- Chicken Stir Fry
      ('Chicken Stir Fry', 1, 1.000, 'lb', NULL, 'Chicken Breast'),
      ('Chicken Stir Fry', 2, 3.000, 'cups', NULL, 'Mixed Vegetables (Frozen)'),
      ('Chicken Stir Fry', 3, 2.000, 'tbsp', NULL, 'Soy Sauce'),
      ('Chicken Stir Fry', 4, 1.000, 'tsp',  'grated', 'Ginger'),
      ('Chicken Stir Fry', 5, 2.000, 'cloves', 'minced', 'Garlic'),
      ('Chicken Stir Fry', 6, 1.500, 'cups', NULL, 'Rice'),
      ('Chicken Stir Fry', 7, 1.000, 'tbsp', NULL, 'Vegetable Oil'),

      -- Caesar Salad
      ('Caesar Salad', 1, 1.000, 'head', NULL, 'Romaine Lettuce'),
      ('Caesar Salad', 2, 1.000, 'cup',  NULL, 'Croutons'),
      ('Caesar Salad', 3, 0.333, 'cup',  NULL, 'Parmesan Cheese'),
      ('Caesar Salad', 4, 1.000, 'whole', 'juiced', 'Lemon'),
      ('Caesar Salad', 5, NULL,  NULL,   NULL, 'Black Pepper'),

      -- Tomato Soup
      ('Tomato Soup', 1, 1.000, 'tbsp', NULL, 'Olive Oil'),
      ('Tomato Soup', 2, 1.000, 'whole', 'diced', 'Onion'),
      ('Tomato Soup', 3, 3.000, 'cloves','minced', 'Garlic'),
      ('Tomato Soup', 4, 28.000,'oz',   NULL, 'Diced Tomatoes'),
      ('Tomato Soup', 5, 2.000, 'cups', NULL, 'Chicken Broth'),
      ('Tomato Soup', 6, NULL,  NULL,   NULL, 'Salt'),
      ('Tomato Soup', 7, NULL,  NULL,   NULL, 'Black Pepper'),

      -- Chicken Noodle Soup (Simple)
      ('Chicken Noodle Soup (Simple)', 1, 4.000, 'cups', NULL, 'Chicken Broth'),
      ('Chicken Noodle Soup (Simple)', 2, 1.000, 'whole','diced', 'Onion'),
      ('Chicken Noodle Soup (Simple)', 3, 2.000, 'whole','sliced', 'Carrots'),
      ('Chicken Noodle Soup (Simple)', 4, 2.000, 'stalks','sliced', 'Celery'),
      ('Chicken Noodle Soup (Simple)', 5, 1.000, 'lb', NULL, 'Chicken Breast'),
      ('Chicken Noodle Soup (Simple)', 6, NULL,  NULL, NULL, 'Salt'),
      ('Chicken Noodle Soup (Simple)', 7, NULL,  NULL, NULL, 'Black Pepper'),

      -- Mashed Potatoes
      ('Mashed Potatoes', 1, 2.000, 'lb', NULL, 'Potatoes'),
      ('Mashed Potatoes', 2, 3.000, 'tbsp',NULL, 'Butter'),
      ('Mashed Potatoes', 3, 0.500, 'cup', NULL, 'Milk'),
      ('Mashed Potatoes', 4, NULL,  NULL,  NULL, 'Salt'),
      ('Mashed Potatoes', 5, NULL,  NULL,  NULL, 'Black Pepper'),

      -- Mac and Cheese
      ('Mac and Cheese (Stovetop)', 1, 12.000, 'oz', NULL, 'Spaghetti'),
      ('Mac and Cheese (Stovetop)', 2, 2.000, 'cups',NULL, 'Cheddar Cheese'),
      ('Mac and Cheese (Stovetop)', 3, 2.000, 'tbsp',NULL, 'Butter'),
      ('Mac and Cheese (Stovetop)', 4, 1.000, 'cup', NULL, 'Milk'),
      ('Mac and Cheese (Stovetop)', 5, NULL,  NULL,  NULL, 'Salt'),
      ('Mac and Cheese (Stovetop)', 6, NULL,  NULL,  NULL, 'Black Pepper'),

      -- Cookies
      ('Chocolate Chip Cookies', 1, 0.500, 'cup', NULL, 'Butter'),
      ('Chocolate Chip Cookies', 2, 0.500, 'cup', NULL, 'Sugar'),
      ('Chocolate Chip Cookies', 3, 0.500, 'cup', NULL, 'Brown Sugar'),
      ('Chocolate Chip Cookies', 4, 2.000, 'large',NULL, 'Eggs'),
      ('Chocolate Chip Cookies', 5, 2.000, 'tsp', NULL, 'Vanilla Extract'),
      ('Chocolate Chip Cookies', 6, 2.250, 'cups',NULL, 'All-Purpose Flour'),
      ('Chocolate Chip Cookies', 7, 1.000, 'tsp', NULL, 'Baking Soda'),
      ('Chocolate Chip Cookies', 8, 2.000, 'cups',NULL, 'Chocolate Chips'),

      -- Banana Bread
      ('Banana Bread', 1, 3.000, 'whole', 'mashed', 'Bananas'),
      ('Banana Bread', 2, 0.333, 'cup',  NULL, 'Butter'),
      ('Banana Bread', 3, 0.750, 'cup',  NULL, 'Sugar'),
      ('Banana Bread', 4, 2.000, 'large',NULL, 'Eggs'),
      ('Banana Bread', 5, 1.000, 'tsp',  NULL, 'Vanilla Extract'),
      ('Banana Bread', 6, 1.500, 'cups', NULL, 'All-Purpose Flour'),
      ('Banana Bread', 7, 1.000, 'tsp',  NULL, 'Baking Soda'),
      ('Banana Bread', 8, 0.500, 'tsp',  NULL, 'Cinnamon')
  ) AS v(recipe_title, line_order, quantity, unit_text, prep_note, ingredient_name)
  WHERE v.recipe_title = rec.title
) ri ON true
JOIN ingredients ing
  ON ing.name_normalized = lower(regexp_replace(trim(ri.ingredient_name), '\s+', ' ', 'g'))
ON CONFLICT (recipe_id, line_order) DO NOTHING;

COMMIT;
