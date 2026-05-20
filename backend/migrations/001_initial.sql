CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    login_type TEXT NOT NULL,
    points_balance INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    last_login_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sms_codes (
    phone TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    prompt TEXT NOT NULL,
    style_id TEXT NOT NULL,
    template_id TEXT NOT NULL,
    ratio_id TEXT NOT NULL,
    quality_level TEXT NOT NULL,
    reference_mode TEXT,
    reference_image_count INTEGER NOT NULL DEFAULT 0,
    final_points INTEGER NOT NULL,
    provider_id TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,
    share_image_url TEXT,
    review_status TEXT NOT NULL,
    prompt_snapshot TEXT,
    style_id TEXT,
    template_id TEXT,
    ratio_id TEXT,
    quality_level TEXT,
    reference_mode TEXT,
    reference_image_count INTEGER DEFAULT 0,
    final_points INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES generation_tasks(id)
);

CREATE TABLE IF NOT EXISTS point_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    type TEXT NOT NULL,
    reason TEXT NOT NULL,
    related_order_id INTEGER,
    related_task_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS payment_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    amount REAL NOT NULL,
    points_amount INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS share_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    work_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    share_code TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (work_id) REFERENCES works(id)
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    work_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(user_id, work_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (work_id) REFERENCES works(id)
);

CREATE TABLE IF NOT EXISTS model_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id TEXT NOT NULL UNIQUE,
    provider_name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_key_ref TEXT,
    model_name TEXT NOT NULL,
    api_mode TEXT NOT NULL,
    capabilities TEXT,
    priority INTEGER NOT NULL DEFAULT 100,
    status TEXT NOT NULL,
    timeout_seconds INTEGER NOT NULL DEFAULT 60,
    qps_limit INTEGER NOT NULL DEFAULT 5,
    cost_level TEXT NOT NULL DEFAULT 'medium',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_health_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    success_rate REAL,
    average_latency_ms REAL,
    timeout_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    blocked_rate REAL,
    queue_depth INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (provider_id) REFERENCES model_providers(id)
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_generation_tasks_user_id ON generation_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_point_transactions_user_id ON point_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_orders_user_id ON payment_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_share_events_user_id ON share_events(user_id);
CREATE INDEX IF NOT EXISTS idx_model_health_logs_provider_id ON model_health_logs(provider_id);
