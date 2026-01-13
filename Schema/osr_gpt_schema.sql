-- ============================================================
-- Recipe Web App - PostgreSQL Schema (single file)
-- Includes:
--  - Users, Recipes, Categories
--  - Tags (M:N), Allergens (M:N)
--  - Ingredients with rich junction (quantity/unit/note/order)
--  - Ordered recipe steps
--  - User↔Recipe junctions: favorites, ratings, comments
--  - Count-only counters: attempts (per user+recipe), views (per user+recipe)
--  - Optional global view totals (per recipe) for anonymous traffic
-- ============================================================

BEGIN;

-- ----------------------------
-- Core: users
-- ----------------------------
CREATE TABLE IF NOT EXISTS users (
  id                BIGSERIAL PRIMARY KEY,
  username          VARCHAR(50)  NOT NULL UNIQUE,
  email             VARCHAR(254) NOT NULL UNIQUE,
  password_hash     TEXT         NOT NULL,
  profile_image_url TEXT,
  last_login_at     TIMESTAMPTZ,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------
-- Lookup: categories
-- ----------------------------
CREATE TABLE IF NOT EXISTS categories (
  id    BIGSERIAL PRIMARY KEY,
  name  VARCHAR(80) NOT NULL UNIQUE
);

-- ----------------------------
-- Core: recipes
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipes (
  id                 BIGSERIAL PRIMARY KEY,
  owner_user_id       BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  title              VARCHAR(200) NOT NULL,
  short_description  VARCHAR(500),
  long_description   TEXT,
  category_id        BIGINT REFERENCES categories(id) ON DELETE SET NULL,

  prep_time_minutes  INTEGER NOT NULL CHECK (prep_time_minutes >= 0),

  -- Optional cached counters (keep at 0; update in app code if you choose)
  -- If you prefer fully-derived counts, you can drop these columns.
  times_viewed       BIGINT  NOT NULL DEFAULT 0 CHECK (times_viewed >= 0),
  times_attempted    BIGINT  NOT NULL DEFAULT 0 CHECK (times_attempted >= 0),

  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_recipes_owner    ON recipes(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category_id);

-- ----------------------------
-- Tags (M:N)
-- ----------------------------
CREATE TABLE IF NOT EXISTS tags (
  id    BIGSERIAL PRIMARY KEY,
  name  VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_tags (
  recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  tag_id    BIGINT NOT NULL REFERENCES tags(id)    ON DELETE CASCADE,
  PRIMARY KEY (recipe_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_recipe_tags_tag ON recipe_tags(tag_id);

-- ----------------------------
-- Allergens (M:N)
-- ----------------------------
CREATE TABLE IF NOT EXISTS allergens (
  id    BIGSERIAL PRIMARY KEY,
  name  VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_allergens (
  recipe_id   BIGINT NOT NULL REFERENCES recipes(id)   ON DELETE CASCADE,
  allergen_id BIGINT NOT NULL REFERENCES allergens(id) ON DELETE CASCADE,
  PRIMARY KEY (recipe_id, allergen_id)
);

CREATE INDEX IF NOT EXISTS idx_recipe_allergens_allergen ON recipe_allergens(allergen_id);

-- ----------------------------
-- Ingredients + Units
-- ----------------------------
CREATE TABLE IF NOT EXISTS ingredients (
  id    BIGSERIAL PRIMARY KEY,
  name  VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS units (
  id      BIGSERIAL PRIMARY KEY,
  name    VARCHAR(40) NOT NULL UNIQUE,  -- e.g. "cup", "tbsp", "g"
  symbol  VARCHAR(20)                  -- e.g. "c", "Tbsp", "g"
);

-- Rich junction: ingredients in recipes
-- line_order in PK allows the same ingredient multiple times with different prep notes.
CREATE TABLE IF NOT EXISTS recipe_ingredients (
  recipe_id      BIGINT NOT NULL REFERENCES recipes(id)     ON DELETE CASCADE,
  ingredient_id  BIGINT NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
  quantity       NUMERIC(10,3), -- nullable for "to taste"
  unit_id        BIGINT REFERENCES units(id) ON DELETE SET NULL,
  prep_note      VARCHAR(200),
  line_order     INTEGER NOT NULL DEFAULT 1 CHECK (line_order > 0),

  PRIMARY KEY (recipe_id, ingredient_id, line_order)
);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe     ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);

-- ----------------------------
-- Recipe steps (ordered instructions)
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_steps (
  id          BIGSERIAL PRIMARY KEY,
  recipe_id   BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  step_no     INTEGER NOT NULL CHECK (step_no > 0),
  instruction TEXT NOT NULL,

  UNIQUE (recipe_id, step_no)
);

CREATE INDEX IF NOT EXISTS idx_recipe_steps_recipe ON recipe_steps(recipe_id);

-- ----------------------------
-- User ↔ Recipe: Favorites (M:N)
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_favorites (
  user_id    BIGINT NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
  recipe_id  BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_recipe_favorites_recipe ON recipe_favorites(recipe_id);

-- ----------------------------
-- User ↔ Recipe: Ratings (M:N + value)
-- One rating per user per recipe
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_ratings (
  user_id   BIGINT NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
  recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,

  rating    SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  rated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

  PRIMARY KEY (user_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_recipe_ratings_recipe ON recipe_ratings(recipe_id);

-- ----------------------------
-- User ↔ Recipe: Comments (M:N, many per user)
-- Optional threading via parent_comment_id
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_comments (
  id        BIGSERIAL PRIMARY KEY,
  user_id   BIGINT NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
  recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,

  comment_text TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

  parent_comment_id BIGINT REFERENCES recipe_comments(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recipe_comments_recipe ON recipe_comments(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_comments_user   ON recipe_comments(user_id);

-- ----------------------------
-- Count-only pattern: Attempts (M:N + counter)
-- One row per user+recipe. attempt_count increments over time.
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_attempt_counts (
  user_id           BIGINT NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
  recipe_id         BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,

  attempt_count     INTEGER NOT NULL DEFAULT 1 CHECK (attempt_count >= 1),
  first_attempted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_attempted_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

  PRIMARY KEY (user_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_attempt_counts_recipe ON recipe_attempt_counts(recipe_id);
CREATE INDEX IF NOT EXISTS idx_attempt_counts_user   ON recipe_attempt_counts(user_id);

-- ----------------------------
-- Count-only pattern: Views (M:N + counter)
-- One row per user+recipe. view_count increments over time.
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_view_counts (
  user_id          BIGINT NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
  recipe_id        BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,

  view_count       INTEGER NOT NULL DEFAULT 1 CHECK (view_count >= 1),
  first_viewed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_viewed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

  PRIMARY KEY (user_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_view_counts_recipe ON recipe_view_counts(recipe_id);
CREATE INDEX IF NOT EXISTS idx_view_counts_user   ON recipe_view_counts(user_id);

-- ----------------------------
-- Optional: Global view totals (per recipe)
-- Useful if you want to count anonymous traffic without per-view rows.
-- If you don't need this, you can drop this table.
-- ----------------------------
CREATE TABLE IF NOT EXISTS recipe_view_totals (
  recipe_id   BIGINT PRIMARY KEY REFERENCES recipes(id) ON DELETE CASCADE,
  view_count  BIGINT NOT NULL DEFAULT 0 CHECK (view_count >= 0),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;

-- ============================================================
-- Notes / Usage snippets (keep for reference)
-- ============================================================

-- Increment an attempt counter (count-only):
-- INSERT INTO recipe_attempt_counts (user_id, recipe_id, attempt_count)
-- VALUES ($1, $2, 1)
-- ON CONFLICT (user_id, recipe_id)
-- DO UPDATE SET
--   attempt_count      = recipe_attempt_counts.attempt_count + 1,
--   last_attempted_at  = now();

-- Increment a view counter (count-only):
-- INSERT INTO recipe_view_counts (user_id, recipe_id, view_count)
-- VALUES ($1, $2, 1)
-- ON CONFLICT (user_id, recipe_id)
-- DO UPDATE SET
--   view_count     = recipe_view_counts.view_count + 1,
--   last_viewed_at = now();

-- Increment global view totals (optional, for anonymous):
-- INSERT INTO recipe_view_totals (recipe_id, view_count)
-- VALUES ($1, 1)
-- ON CONFLICT (recipe_id)
-- DO UPDATE SET
--   view_count = recipe_view_totals.view_count + 1,
--   updated_at = now();

-- Derive total attempts per recipe:
-- SELECT recipe_id, COALESCE(SUM(attempt_count), 0) AS times_attempted
-- FROM recipe_attempt_counts
-- WHERE recipe_id = $1
-- GROUP BY recipe_id;

-- Derive total views per recipe (logged-in only):
-- SELECT recipe_id, COALESCE(SUM(view_count), 0) AS times_viewed
-- FROM recipe_view_counts
-- WHERE recipe_id = $1
-- GROUP BY recipe_id;
