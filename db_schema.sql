-- db_schema.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT,
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS personality (
    user_id INTEGER PRIMARY KEY,
    openness REAL DEFAULT 0,
    conscientiousness REAL DEFAULT 0,
    extraversion REAL DEFAULT 0,
    agreeableness REAL DEFAULT 0,
    neuroticism REAL DEFAULT 0,
    updated_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    destination TEXT,
    country TEXT,
    score REAL,
    params_json TEXT,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
