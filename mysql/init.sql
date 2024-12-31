CREATE TABLE IF NOT EXISTS players (
    player_id BIGINT PRIMARY KEY,
    personal_name VARCHAR(255),
    discord_id BIGINT,
    auto_analyze_end_datetime TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS player_match (
    player_id BIGINT,
    match_id BIGINT,
    start_time TIMESTAMP,
    PRIMARY KEY (player_id, match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Optionally add indexing for performance
CREATE INDEX idx_player_id ON player_match(player_id);
CREATE INDEX idx_match_id ON player_match(match_id);
