-- src/github_data_pipeline/persistence/postgres/sql/staging_tables.sql

-- ===============================================
-- staging_user.follower
-- ===============================================
CREATE TABLE IF NOT EXISTS staging_user.follower (
    user_id BIGINT NOT NULL,
    login TEXT NOT NULL,
    id BIGINT NOT NULL,
    node_id TEXT NOT NULL,
    avatar_url TEXT NOT NULL,
    gravatar_id TEXT NOT NULL,
    url TEXT NOT NULL,
    html_url TEXT NOT NULL,
    followers_url TEXT NOT NULL,
    following_url TEXT NOT NULL,
    gists_url TEXT NOT NULL,
    starred_url TEXT NOT NULL,
    subscriptions_url TEXT NOT NULL,
    organizations_url TEXT NOT NULL,
    repos_url TEXT NOT NULL,
    events_url TEXT NOT NULL,
    received_events_url TEXT NOT NULL,
    type TEXT NOT NULL,
    site_admin BOOLEAN NOT NULL
);

-- ==============================================
-- staging_user.following
-- ==============================================
CREATE TABLE IF NOT EXISTS staging_user.following (
    user_id BIGINT NOT NULL,
    login TEXT NOT NULL,
    id BIGINT NOT NULL,
    node_id TEXT NOT NULL,
    avatar_url TEXT NOT NULL,
    gravatar_id TEXT NOT NULL,
    url TEXT NOT NULL,
    html_url TEXT NOT NULL,
    followers_url TEXT NOT NULL,
    following_url TEXT NOT NULL,
    gists_url TEXT NOT NULL,
    starred_url TEXT NOT NULL,
    subscriptions_url TEXT NOT NULL,
    organizations_url TEXT NOT NULL,
    repos_url TEXT NOT NULL,
    events_url TEXT NOT NULL,
    received_events_url TEXT NOT NULL,
    type TEXT NOT NULL,
    site_admin BOOLEAN NOT NULL
);

-- ===================================================
-- staging_user.received_event
-- ===================================================
CREATE TABLE IF NOT EXISTS staging_user.received_event (
    user_id BIGINT NOT NULL,
    id TEXT NOT NULL,
    type TEXT NOT NULL,
    actor_id BIGINT NOT NULL,
    actor_login TEXT NOT NULL,
    actor_url TEXT NOT NULL,
    repo_id BIGINT NOT NULL,
    repo_name TEXT NOT NULL,
    repo_url TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- ==================================================
-- staging_user.starred
-- ==================================================
CREATE TABLE IF NOT EXISTS staging_user.starred (
    user_id BIGINT NOT NULL,
    id BIGINT NOT NULL,
    node_id TEXT NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    private BOOLEAN NOT NULL,
    owner JSONB NOT NULL,
    html_url TEXT NOT NULL,
    description TEXT,
    fork BOOLEAN NOT NULL,
    url TEXT NOT NULL
);

-- ====================================================
-- staging_user.repository
-- ====================================================
CREATE TABLE IF NOT EXISTS staging_user.repository (
    user_id BIGINT NOT NULL,
    id BIGINT NOT NULL,
    node_id TEXT NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    private BOOLEAN NOT NULL,
    owner JSONB NOT NULL,
    html_url TEXT NOT NULL,
    description TEXT,
    fork BOOLEAN NOT NULL,
    url TEXT NOT NULL
);