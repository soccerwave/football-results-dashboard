PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS h2h_summary;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE matches (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  date           TEXT NOT NULL,   -- ISO date (YYYY-MM-DD)
  year           INTEGER NOT NULL,
  home_team_id   INTEGER NOT NULL,
  away_team_id   INTEGER NOT NULL,
  home_score     INTEGER NOT NULL,
  away_score     INTEGER NOT NULL,
  FOREIGN KEY(home_team_id) REFERENCES teams(id),
  FOREIGN KEY(away_team_id) REFERENCES teams(id)
);

CREATE TABLE h2h_summary (
  team_id          INTEGER NOT NULL,
  opponent_id      INTEGER NOT NULL,
  games            INTEGER NOT NULL,
  w                INTEGER NOT NULL,
  d                INTEGER NOT NULL,
  l                INTEGER NOT NULL,
  gf               INTEGER NOT NULL,
  ga               INTEGER NOT NULL,
  last_meeting_date TEXT,
  PRIMARY KEY(team_id, opponent_id),
  FOREIGN KEY(team_id)    REFERENCES teams(id),
  FOREIGN KEY(opponent_id) REFERENCES teams(id)
);

CREATE INDEX idx_matches_date ON matches(date);
CREATE INDEX idx_matches_home ON matches(home_team_id);
CREATE INDEX idx_matches_away ON matches(away_team_id);
