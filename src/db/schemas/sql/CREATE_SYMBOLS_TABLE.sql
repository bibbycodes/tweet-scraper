CREATE TABLE IF NOT EXISTS symbols
(
    symbol_id  SERIAL PRIMARY KEY,
    symbol       TEXT NOT NULL,
    tweet_id        BIGINT,
    twitter_user_id BIGINT,
    FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id),
    FOREIGN KEY (twitter_user_id) REFERENCES users (twitter_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
