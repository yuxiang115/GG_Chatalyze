CREATE TABLE IF NOT EXISTS players (
    player_id BIGINT PRIMARY KEY,
    personal_name VARCHAR(255),
    discord_id BIGINT,
    auto_analyze_end_datetime TIMESTAMP DEFAULT NOW() NOT NULL
);

# CREATE INDEX discord_id_index ON players (discord_id);
# CREATE INDEX auto_analyze_end_datetime_index ON players (auto_analyze_end_datetime);
