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
