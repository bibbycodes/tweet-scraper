CREATE TABLE IF NOT EXISTS mentions
(
    tweet_id        BIGINT,
    twitter_user_id BIGINT,
    twitter_user_id_mentioned BIGINT,
    username_mentioned        VARCHAR(255),
    FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id),
    FOREIGN KEY (twitter_user_id) REFERENCES users (twitter_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
