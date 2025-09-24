-- name: last_5_matches_h2h
SELECT m.date,
       ht.name AS home_team,
       at.name AS away_team,
       m.home_score,
       m.away_score
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id
WHERE (ht.name = :team_a AND at.name = :team_b)
   OR (ht.name = :team_b AND at.name = :team_a)
ORDER BY m.date DESC
LIMIT :limit;

-- name: recent_form_10
WITH team_matches AS (
  SELECT m.date AS date, at.name AS opponent, 1 AS is_home,
         m.home_score AS gf, m.away_score AS ga
  FROM matches m
  JOIN teams ht ON m.home_team_id = ht.id
  JOIN teams at ON m.away_team_id = at.id
  WHERE ht.name = :team_name
  UNION ALL
  SELECT m.date, ht.name, 0 AS is_home,
         m.away_score, m.home_score
  FROM matches m
  JOIN teams ht ON m.home_team_id = ht.id
  JOIN teams at ON m.away_team_id = at.id
  WHERE at.name = :team_name
)
SELECT date, opponent, is_home,
       gf, ga,
       CASE WHEN gf > ga THEN 'W'
            WHEN gf = ga THEN 'D'
            ELSE 'L' END AS result
FROM team_matches
ORDER BY date DESC
LIMIT :limit;

-- name: h2h_summary
SELECT ta.name AS team,
       tb.name AS opponent,
       s.games, s.w, s.d, s.l,
       s.gf, s.ga,
       s.last_meeting_date
FROM h2h_summary s
JOIN teams ta ON s.team_id = ta.id
JOIN teams tb ON s.opponent_id = tb.id
WHERE ta.name = :team_a AND tb.name = :team_b;

-- name: team_top_opponents
SELECT tb.name AS opponent,
       s.games, s.w, s.d, s.l, s.gf, s.ga
FROM h2h_summary s
JOIN teams ta ON s.team_id = ta.id
JOIN teams tb ON s.opponent_id = tb.id
WHERE ta.name = :team_name
ORDER BY s.games DESC, opponent ASC
LIMIT :limit;

-- name: team_recent_goal_diff
WITH tm AS (
  SELECT m.date AS date, (m.home_score - m.away_score) AS gd
  FROM matches m
  JOIN teams ht ON m.home_team_id = ht.id
  WHERE ht.name = :team_name
  UNION ALL
  SELECT m.date, (m.away_score - m.home_score) AS gd
  FROM matches m
  JOIN teams at ON m.away_team_id = at.id
  WHERE at.name = :team_name
)
SELECT date, gd
FROM tm
ORDER BY date DESC
LIMIT :limit;
