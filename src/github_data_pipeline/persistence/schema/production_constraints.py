
# src/github_data_pipeline/persistence/postgres/schema/production_constraints.py

from sqlalchemy import BigInteger


# =================================================
# 1. PRIMARY KEYS
# =================================================

PRIMARY_KEYS = {
    # Production Repository
    "production_repository.repository": ["id"],
    "production_repository.branch": ["repo_id", "name"],
    "production_repository.commit": ["repo_id", "sha"],
    "production_repository.contributor": ["repo_id", "user_id"],
    "production_repository.fork": ["repo_id", "fork_id"],
    "production_repository.issue": ["id"],
    "production_repository.language": ["repo_id", "language"],
    "production_repository.pull_request": ["id"],
    "production_repository.readme": ["repo_id"],
    "production_repository.release": ["id"],
    "production_repository.tag": ["repo_id", "tag_name"],
    "production_repository.topic": ["repo_id", "topic"],

    # Production User
    "production_user.user": ["id"],
    "production_user.profile": ["user_id"],
    "production_user.organization": ["id"],
    "production_user.follower": ["user_id", "follower_id"],
    "production_user.following": ["user_id", "following_id"],
    "production_user.gist": ["id"],
    "production_user.event": ["id"],
    "production_user.received_event": ["user_id", "id"],
    "production_user.starred": ["user_id", "repo_id"],
    "production_user.repository": ["user_id", "repo_id"],
}

# =================================================
# 2. UNIQUE CONSTRAINTS
# =================================================

UNIQUE_CONSTRAINTS = {
    "production_repository.repository": [
        ["full_name"],
    ],
    "production_repository.issue": [
        ["repo_id", "number"],
    ],
    "production_repository.pull_request": [
        ["repo_id", "number"],
    ],
    "production_repository.release": [
        ["repo_id", "tag_name"],
    ],

    "production_user.user": [
        ["login"],
        ["node_id"],
    ],
    "production_user.organization": [
        ["login"],
        ["node_id"],
    ],
}

# =================================================
# 3. ADDITIONAL PRODUCTION COLUMNS
# =================================================

ADDITIONAL_COLUMNS = {
    "production_user.follower": {
        "user_id": BigInteger,
        "follower_id": BigInteger,
    },
    "production_user.following": {
        "user_id": BigInteger,
        "following_id": BigInteger,
    },
    "production_user.received_event": {
        "user_id": BigInteger,
    },
    "production_user.starred": {
        "user_id": BigInteger,
        "repo_id": BigInteger,
    },
    "production_user.repository": {
        "user_id": BigInteger,
        "repo_id": BigInteger,
    },
}

# =================================================
# 4. PRODUCTION COLUMN MAPPINGS
# =================================================

PRODUCTION_COLUMNS = {
    # User relationships
    "production_user.follower": [
        "user_id",
        "follower_id",
    ],
    "production_user.following": [
        "user_id",
        "following_id",
    ],

    # Received events retain their event information.
    "production_user.received_event": [
        "user_id",
        "id",
        "type",
        "actor_id",
        "actor_login",
        "actor_url",
        "repo_id",
        "repo_name",
        "repo_url",
        "created_at",
    ],

    # Repository relationships instead of duplicated objects.
    "production_user.starred": [
        "user_id",
        "repo_id",
    ],
    "production_user.repository": [
        "user_id",
        "repo_id",
    ],
}

# =================================================
# 5. FOREIGN KEYS
# =================================================
# Each entry:
# (local_columns, referenced_schema,
#  referenced_table, referenced_columns)

FOREIGN_KEYS = {
    # Repository relationships
    "production_repository.branch": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
        (
            ["repo_id", "commit_sha"],
            "production_repository",
            "commit",
            ["repo_id", "sha"],
        ),
    ],

    "production_repository.commit": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.contributor": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.fork": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.issue": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.language": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.pull_request": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.readme": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.release": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.tag": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    "production_repository.topic": [
        (
            ["repo_id"],
            "production_repository",
            "repository",
            ["id"],
        ),
    ],

    # User relationships
    "production_user.profile": [
        (
            ["user_id"],
            "production_user",
            "user",
            ["id"],
        ),
    ],

    "production_user.follower": [
        (
            ["user_id"],
            "production_user",
            "user",
            ["id"],
        ),
    ],

    "production_user.following": [
        (
            ["user_id"],
            "production_user",
            "user",
            ["id"],
        ),
    ],

    "production_user.starred": [
        (
            ["user_id"],
            "production_user",
            "user",
            ["id"],
        ),
    ],

    "production_user.repository": [
        (
            ["user_id"],
            "production_user",
            "user",
            ["id"],
        ),
    ],
    }

# =================================================
# 6. CHECK CONSTRAINTS
# =================================================

CHECK_CONSTRAINTS = {
    "production_repository.repository": {
        "stars_count": "stars_count >= 0",
        "forks_count": "forks_count >= 0",
        "watchers_count": "watchers_count >= 0",
        "open_issues_count": "open_issues_count >= 0",
    },

    "production_repository.contributor": {
        "contributions": "contributions >= 0",
    },

    "production_repository.issue": {
        "number": "number > 0",
        "comments": "comments >= 0",
    },

    "production_repository.pull_request": {
        "number": "number > 0",
    },

    "production_user.profile": {
        "public_repos": "public_repos >= 0",
        "public_gists": "public_gists >= 0",
        "followers": "followers >= 0",
        "following": "following >= 0",
    },
}

# =================================================
# 9. COLUMN RENAMES
# =================================================

COLUMN_RENAMES = {
    "production_user.profile": {
        "id": "user_id",
    },
    "production_user.follower": {
        "id": "follower_id",
    },
    "production_user.following": {
        "id": "following_id",
    },
    "production_user.starred": {
        "id": "repo_id",
    },
    "production_user.repository": {
        "id": "repo_id",
    },
}

# =================================================
# 7. UPSERT CONFLICT TARGETS
# =================================================
# Used by the production writer.

UPSERT_KEYS = PRIMARY_KEYS

# =================================================
# 8. IMMUTABLE TABLES
# =================================================
# These tables generally use ON CONFLICT DO NOTHING.

IMMUTABLE_TABLES = {
    "production_user.event",
    "production_user.received_event",
}
