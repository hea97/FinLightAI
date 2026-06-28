CREATE TABLE IF NOT EXISTS news_articles (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news_filter_results (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES news_articles(id),
    is_reliable BOOLEAN NOT NULL,
    final_score NUMERIC(5, 4) NOT NULL,
    breakdown JSONB NOT NULL,
    flags JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_signals (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    signal TEXT NOT NULL CHECK (signal IN ('RED', 'YELLOW', 'GREEN')),
    event_score NUMERIC(5, 4) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(80) PRIMARY KEY,
    username VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL,
    language VARCHAR(30) NOT NULL DEFAULT 'Korean',
    alert_channel VARCHAR(80) NOT NULL DEFAULT 'Kakao Channel',
    channel_connected BOOLEAN NOT NULL DEFAULT FALSE,
    interests JSONB NOT NULL DEFAULT '[]'::JSONB,
    alert_settings JSONB NOT NULL DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolio_assets (
    id VARCHAR(80) PRIMARY KEY,
    user_id VARCHAR(80) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_name VARCHAR(120) NOT NULL,
    symbol VARCHAR(30) NOT NULL,
    market VARCHAR(20) NOT NULL,
    industry VARCHAR(80) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL CHECK (quantity >= 0),
    average_buy_price DOUBLE PRECISION NOT NULL CHECK (average_buy_price >= 0),
    current_price DOUBLE PRECISION NOT NULL CHECK (current_price >= 0),
    recent_sell_price DOUBLE PRECISION,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(30) NOT NULL,
    decision_memo TEXT,
    related_news_count INTEGER NOT NULL DEFAULT 0,
    caution_news_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_portfolio_user_symbol_market UNIQUE (user_id, symbol, market)
);

CREATE INDEX IF NOT EXISTS ix_portfolio_assets_user_id ON portfolio_assets(user_id);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id VARCHAR(80) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kakao_alert_rules (
    user_id VARCHAR(80) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rule_id VARCHAR(80) NOT NULL,
    icon VARCHAR(20) NOT NULL,
    label VARCHAR(255) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (user_id, rule_id)
);

CREATE TABLE IF NOT EXISTS alert_history (
    id VARCHAR(80) PRIMARY KEY,
    user_id VARCHAR(80) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type VARCHAR(80) NOT NULL,
    trigger VARCHAR(255) NOT NULL,
    status VARCHAR(40) NOT NULL,
    tone VARCHAR(30) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_alert_history_user_id ON alert_history(user_id);
