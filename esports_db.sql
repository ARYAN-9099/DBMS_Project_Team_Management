-- ============================================================================
-- ESPORTS COMPETITION ORGANIZATION AND TEAM MANAGEMENT SYSTEM
-- Database Schema, Sample Data, Stored Procedures, Triggers, and Views
-- ============================================================================
-- ============================================================================

-- Drop database if exists and create fresh
DROP DATABASE IF EXISTS esports_db;
CREATE DATABASE esports_db;
USE esports_db;

-- ============================================================================
-- TABLE DEFINITIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: users
-- Purpose: Store all system users (admins, players, organizers)
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- In production, use hashed passwords
    role ENUM('admin', 'player', 'organizer') NOT NULL DEFAULT 'player',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: teams
-- Purpose: Store team information with captain reference
-- ----------------------------------------------------------------------------
CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    captain_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (captain_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    INDEX idx_captain (captain_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: players
-- Purpose: Link users to teams with their gaming tag
-- ----------------------------------------------------------------------------
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    team_id INT,
    game_tag VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL,
    UNIQUE KEY unique_user_team (user_id, team_id),
    INDEX idx_team (team_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: games
-- Purpose: Store available esports games
-- ----------------------------------------------------------------------------
CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    genre VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: tournaments
-- Purpose: Store tournament information
-- ----------------------------------------------------------------------------
CREATE TABLE tournaments (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    game_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    prize_pool DECIMAL(10, 2) DEFAULT 0.00,
    status ENUM('upcoming', 'ongoing', 'completed') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE RESTRICT,
    INDEX idx_game (game_id),
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: registrations
-- Purpose: Track team registrations for tournaments
-- ----------------------------------------------------------------------------
CREATE TABLE registrations (
    reg_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    tournament_id INT NOT NULL,
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'confirmed', 'rejected') DEFAULT 'confirmed',
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
    UNIQUE KEY unique_team_tournament (team_id, tournament_id),
    INDEX idx_tournament (tournament_id),
    INDEX idx_team (team_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: matches
-- Purpose: Store match details and results
-- ----------------------------------------------------------------------------
CREATE TABLE matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    winner_id INT,  -- NULL if match not completed
    match_time DATETIME NOT NULL,
    round_number INT DEFAULT 1,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
    FOREIGN KEY (team1_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
    FOREIGN KEY (team2_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
    FOREIGN KEY (winner_id) REFERENCES teams(team_id) ON DELETE SET NULL,
    INDEX idx_tournament (tournament_id),
    INDEX idx_teams (team1_id, team2_id),
    INDEX idx_match_time (match_time)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table: scores
-- Purpose: Store detailed scores for each team in a match
-- ----------------------------------------------------------------------------
CREATE TABLE scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    team_id INT NOT NULL,
    score INT NOT NULL DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    UNIQUE KEY unique_match_team (match_id, team_id),
    INDEX idx_match (match_id)
) ENGINE=InnoDB;

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert Users (10+ records as required)
INSERT INTO users (name, email, password, role) VALUES
('Admin User', 'admin@esports.com', 'admin123', 'admin'),
('John Smith', 'john@example.com', 'pass123', 'organizer'),
('Alice Johnson', 'alice@example.com', 'pass123', 'player'),
('Bob Williams', 'bob@example.com', 'pass123', 'player'),
('Charlie Brown', 'charlie@example.com', 'pass123', 'player'),
('David Lee', 'david@example.com', 'pass123', 'player'),
('Emma Davis', 'emma@example.com', 'pass123', 'player'),
('Frank Miller', 'frank@example.com', 'pass123', 'player'),
('Grace Wilson', 'grace@example.com', 'pass123', 'player'),
('Henry Taylor', 'henry@example.com', 'pass123', 'player'),
('Ivy Martinez', 'ivy@example.com', 'pass123', 'player'),
('Jack Anderson', 'jack@example.com', 'pass123', 'player'),
('Kate Thomas', 'kate@example.com', 'pass123', 'player'),
('Leo Garcia', 'leo@example.com', 'pass123', 'player'),
('Maya Rodriguez', 'maya@example.com', 'pass123', 'player');

-- Insert Games
INSERT INTO games (title, genre) VALUES
('Counter-Strike 2', 'FPS'),
('League of Legends', 'MOBA'),
('Valorant', 'FPS'),
('Dota 2', 'MOBA'),
('Rocket League', 'Sports');

-- Insert Teams (using player user_ids as captains)
INSERT INTO teams (team_name, captain_id) VALUES
('Thunder Strikers', 3),  -- Alice is captain
('Phoenix Rising', 4),    -- Bob is captain
('Shadow Legends', 5),    -- Charlie is captain
('Cyber Warriors', 6),    -- David is captain
('Elite Force', 7);       -- Emma is captain

-- Insert Players (linking users to teams)
INSERT INTO players (user_id, team_id, game_tag) VALUES
(3, 1, 'Alice_Thunder'),
(4, 2, 'Bob_Phoenix'),
(5, 3, 'Charlie_Shadow'),
(6, 4, 'David_Cyber'),
(7, 5, 'Emma_Elite'),
(8, 1, 'Frank_Thunder'),
(9, 2, 'Grace_Phoenix'),
(10, 3, 'Henry_Shadow'),
(11, 4, 'Ivy_Cyber'),
(12, 5, 'Jack_Elite'),
(13, 1, 'Kate_Thunder'),
(14, 2, 'Leo_Phoenix'),
(15, 3, 'Maya_Shadow');

-- Insert Tournaments
INSERT INTO tournaments (name, game_id, start_date, end_date, prize_pool, status) VALUES
('Winter Championship 2025', 1, '2025-12-01', '2025-12-15', 50000.00, 'upcoming'),
('Spring League', 2, '2025-11-01', '2025-11-10', 30000.00, 'ongoing'),
('Valorant Masters', 3, '2025-10-15', '2025-10-25', 40000.00, 'ongoing'),
('Dota Pro Circuit', 4, '2025-09-01', '2025-09-20', 100000.00, 'completed'),
('Rocket League Open', 5, '2025-11-15', '2025-11-30', 25000.00, 'upcoming');

-- Insert Registrations
INSERT INTO registrations (team_id, tournament_id, status) VALUES
(1, 1, 'confirmed'),
(2, 1, 'confirmed'),
(3, 1, 'confirmed'),
(4, 1, 'confirmed'),
(5, 1, 'confirmed'),
(1, 2, 'confirmed'),
(2, 2, 'confirmed'),
(3, 2, 'confirmed'),
(1, 3, 'confirmed'),
(2, 3, 'confirmed'),
(3, 3, 'confirmed'),
(4, 3, 'confirmed'),
(1, 4, 'confirmed'),
(2, 4, 'confirmed'),
(3, 4, 'confirmed'),
(4, 4, 'confirmed'),
(5, 4, 'confirmed');

-- Insert Matches
INSERT INTO matches (tournament_id, team1_id, team2_id, winner_id, match_time, round_number, status) VALUES
-- Tournament 2 (Spring League) - Completed matches
(2, 1, 2, 1, '2025-11-02 14:00:00', 1, 'completed'),
(2, 3, 1, 1, '2025-11-04 16:00:00', 2, 'completed'),
(2, 2, 3, 3, '2025-11-03 15:00:00', 1, 'completed'),
-- Tournament 3 (Valorant Masters) - Some completed
(3, 1, 2, 2, '2025-10-16 10:00:00', 1, 'completed'),
(3, 3, 4, 3, '2025-10-17 12:00:00', 1, 'completed'),
(3, 2, 3, 2, '2025-10-20 14:00:00', 2, 'completed'),
(3, 1, 4, NULL, '2025-10-22 16:00:00', 1, 'scheduled'),
-- Tournament 4 (Dota Pro Circuit) - Completed tournament
(4, 1, 2, 2, '2025-09-05 11:00:00', 1, 'completed'),
(4, 3, 4, 3, '2025-09-06 13:00:00', 1, 'completed'),
(4, 5, 1, 5, '2025-09-07 15:00:00', 1, 'completed'),
(4, 2, 3, 2, '2025-09-10 10:00:00', 2, 'completed'),
(4, 5, 4, 4, '2025-09-11 12:00:00', 2, 'completed'),
(4, 2, 4, 2, '2025-09-15 14:00:00', 3, 'completed');

-- Insert Scores for completed matches
INSERT INTO scores (match_id, team_id, score) VALUES
-- Match 1: Team 1 (Thunder) vs Team 2 (Phoenix) - Thunder wins
(1, 1, 16),
(1, 2, 12),
-- Match 2: Team 3 vs Team 1 - Thunder wins
(2, 3, 10),
(2, 1, 16),
-- Match 3: Team 2 vs Team 3 - Shadow wins
(3, 2, 11),
(3, 3, 16),
-- Match 4: Team 1 vs Team 2 - Phoenix wins
(4, 1, 8),
(4, 2, 13),
-- Match 5: Team 3 vs Team 4 - Shadow wins
(5, 3, 15),
(5, 4, 12),
-- Match 6: Team 2 vs Team 3 - Phoenix wins
(6, 2, 14),
(6, 3, 11),
-- Match 8: Team 1 vs Team 2 - Phoenix wins
(8, 1, 25),
(8, 2, 32),
-- Match 9: Team 3 vs Team 4 - Shadow wins
(9, 3, 28),
(9, 4, 22),
-- Match 10: Team 5 vs Team 1 - Elite wins
(10, 5, 30),
(10, 1, 18),
-- Match 11: Team 2 vs Team 3 - Phoenix wins
(11, 2, 35),
(11, 3, 26),
-- Match 12: Team 5 vs Team 4 - Cyber wins
(12, 5, 20),
(12, 4, 28),
-- Match 13: Team 2 vs Team 4 - Phoenix wins (Finals)
(13, 2, 40),
(13, 4, 35);

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Stored Procedure: record_match_result
-- Purpose: Insert a match result and automatically update scores table
-- Parameters:
--   - p_tournament_id: Tournament ID
--   - p_team1_id: First team ID
--   - p_team2_id: Second team ID
--   - p_team1_score: Score for team 1
--   - p_team2_score: Score for team 2
--   - p_match_time: When the match takes place
--   - p_round_number: Round number in tournament
-- Returns: Success message or error
-- ----------------------------------------------------------------------------
DELIMITER //

CREATE PROCEDURE record_match_result(
    IN p_tournament_id INT,
    IN p_team1_id INT,
    IN p_team2_id INT,
    IN p_team1_score INT,
    IN p_team2_score INT,
    IN p_match_time DATETIME,
    IN p_round_number INT
)
BEGIN
    DECLARE v_match_id INT;
    DECLARE v_winner_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error: Transaction failed' AS message;
    END;
    
    -- Start transaction to ensure data consistency
    START TRANSACTION;
    
    -- Determine winner based on scores
    IF p_team1_score > p_team2_score THEN
        SET v_winner_id = p_team1_id;
    ELSEIF p_team2_score > p_team1_score THEN
        SET v_winner_id = p_team2_id;
    ELSE
        SET v_winner_id = NULL; -- Draw
    END IF;
    
    -- Insert match record
    INSERT INTO matches (tournament_id, team1_id, team2_id, winner_id, match_time, round_number, status)
    VALUES (p_tournament_id, p_team1_id, p_team2_id, v_winner_id, p_match_time, p_round_number, 'completed');
    
    SET v_match_id = LAST_INSERT_ID();
    
    -- Insert scores for both teams
    INSERT INTO scores (match_id, team_id, score)
    VALUES (v_match_id, p_team1_id, p_team1_score);
    
    INSERT INTO scores (match_id, team_id, score)
    VALUES (v_match_id, p_team2_id, p_team2_score);
    
    COMMIT;
    
    SELECT 'Match recorded successfully' AS message, v_match_id AS match_id;
END //

DELIMITER ;

-- ----------------------------------------------------------------------------
-- Stored Procedure: get_team_statistics
-- Purpose: Get comprehensive statistics for a team
-- Parameters:
--   - p_team_id: Team ID
-- Returns: Total matches, wins, losses, draws, win rate
-- ----------------------------------------------------------------------------
DELIMITER //

CREATE PROCEDURE get_team_statistics(
    IN p_team_id INT
)
BEGIN
    SELECT 
        t.team_name,
        COUNT(DISTINCT m.match_id) AS total_matches,
        SUM(CASE WHEN m.winner_id = p_team_id THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != p_team_id THEN 1 ELSE 0 END) AS losses,
        SUM(CASE WHEN m.winner_id IS NULL THEN 1 ELSE 0 END) AS draws,
        ROUND(
            SUM(CASE WHEN m.winner_id = p_team_id THEN 1 ELSE 0 END) * 100.0 / 
            NULLIF(COUNT(DISTINCT m.match_id), 0), 
            2
        ) AS win_rate_percentage
    FROM teams t
    LEFT JOIN matches m ON (m.team1_id = p_team_id OR m.team2_id = p_team_id)
        AND m.status = 'completed'
    WHERE t.team_id = p_team_id
    GROUP BY t.team_id, t.team_name;
END //

DELIMITER ;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Trigger: prevent_duplicate_registration
-- Purpose: Prevent a team from registering twice for the same tournament
-- Type: BEFORE INSERT on registrations
-- Note: MySQL will handle this via UNIQUE constraint, but we add validation
-- ----------------------------------------------------------------------------
DELIMITER //

CREATE TRIGGER prevent_duplicate_registration
BEFORE INSERT ON registrations
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    
    -- Check if team is already registered for this tournament
    SELECT COUNT(*) INTO v_count
    FROM registrations
    WHERE team_id = NEW.team_id AND tournament_id = NEW.tournament_id;
    
    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Team is already registered for this tournament';
    END IF;
END //

DELIMITER ;

-- ----------------------------------------------------------------------------
-- Trigger: validate_match_teams
-- Purpose: Ensure team1 and team2 are different in a match
-- Type: BEFORE INSERT on matches
-- ----------------------------------------------------------------------------
DELIMITER //

CREATE TRIGGER validate_match_teams
BEFORE INSERT ON matches
FOR EACH ROW
BEGIN
    IF NEW.team1_id = NEW.team2_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A team cannot play against itself';
    END IF;
END //

DELIMITER ;

-- ----------------------------------------------------------------------------
-- Trigger: validate_match_winner
-- Purpose: Ensure winner is one of the participating teams
-- Type: BEFORE UPDATE on matches
-- ----------------------------------------------------------------------------
DELIMITER //

CREATE TRIGGER validate_match_winner
BEFORE UPDATE ON matches
FOR EACH ROW
BEGIN
    IF NEW.winner_id IS NOT NULL AND 
       NEW.winner_id != NEW.team1_id AND 
       NEW.winner_id != NEW.team2_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Winner must be one of the participating teams';
    END IF;
END //

DELIMITER ;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- View: tournament_leaderboard
-- Purpose: Display comprehensive tournament standings with wins, losses, scores
-- Columns: tournament_id, team_id, team_name, matches_played, wins, losses,
--          draws, total_score, avg_score, win_rate
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW tournament_leaderboard AS
SELECT 
    t.tournament_id,
    t.name AS tournament_name,
    tm.team_id,
    tm.team_name,
    COUNT(DISTINCT m.match_id) AS matches_played,
    SUM(CASE WHEN m.winner_id = tm.team_id THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != tm.team_id THEN 1 ELSE 0 END) AS losses,
    SUM(CASE WHEN m.winner_id IS NULL THEN 1 ELSE 0 END) AS draws,
    COALESCE(SUM(s.score), 0) AS total_score,
    COALESCE(ROUND(AVG(s.score), 2), 0) AS avg_score,
    ROUND(
        SUM(CASE WHEN m.winner_id = tm.team_id THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(DISTINCT m.match_id), 0), 
        2
    ) AS win_rate_percentage
FROM tournaments t
INNER JOIN registrations r ON t.tournament_id = r.tournament_id
INNER JOIN teams tm ON r.team_id = tm.team_id
LEFT JOIN matches m ON t.tournament_id = m.tournament_id 
    AND (m.team1_id = tm.team_id OR m.team2_id = tm.team_id)
    AND m.status = 'completed'
LEFT JOIN scores s ON m.match_id = s.match_id AND s.team_id = tm.team_id
GROUP BY t.tournament_id, t.name, tm.team_id, tm.team_name
ORDER BY t.tournament_id, wins DESC, avg_score DESC;

-- ----------------------------------------------------------------------------
-- View: team_performance_summary
-- Purpose: Overall team performance across all tournaments
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW team_performance_summary AS
SELECT 
    t.team_id,
    t.team_name,
    u.name AS captain_name,
    COUNT(DISTINCT r.tournament_id) AS tournaments_participated,
    COUNT(DISTINCT m.match_id) AS total_matches,
    SUM(CASE WHEN m.winner_id = t.team_id THEN 1 ELSE 0 END) AS total_wins,
    SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != t.team_id THEN 1 ELSE 0 END) AS total_losses,
    COALESCE(ROUND(AVG(s.score), 2), 0) AS avg_score_all_time,
    ROUND(
        SUM(CASE WHEN m.winner_id = t.team_id THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(DISTINCT m.match_id), 0), 
        2
    ) AS overall_win_rate
FROM teams t
INNER JOIN users u ON t.captain_id = u.user_id
LEFT JOIN registrations r ON t.team_id = r.team_id
LEFT JOIN matches m ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
    AND m.status = 'completed'
LEFT JOIN scores s ON m.match_id = s.match_id AND s.team_id = t.team_id
GROUP BY t.team_id, t.team_name, u.name
ORDER BY total_wins DESC, avg_score_all_time DESC;

-- ============================================================================
-- COMPLEX SQL QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Top 5 Teams by Average Score
-- Purpose: Find the best performing teams based on average score
-- Demonstrates: Aggregation, JOIN, LIMIT, ORDER BY
-- ----------------------------------------------------------------------------
-- Top 5 teams by average score across all matches
SELECT 
    t.team_id,
    t.team_name,
    COUNT(DISTINCT s.match_id) AS matches_played,
    ROUND(AVG(s.score), 2) AS avg_score,
    SUM(s.score) AS total_score
FROM teams t
INNER JOIN scores s ON t.team_id = s.team_id
INNER JOIN matches m ON s.match_id = m.match_id
WHERE m.status = 'completed'
GROUP BY t.team_id, t.team_name
HAVING matches_played > 0
ORDER BY avg_score DESC, total_score DESC
LIMIT 5;

-- ----------------------------------------------------------------------------
-- QUERY 2: Tournament Leaderboard with Win/Loss Ratio
-- Purpose: Show detailed standings for a specific tournament
-- Demonstrates: Complex JOIN, CASE statements, Calculations
-- ----------------------------------------------------------------------------
-- Tournament leaderboard with win/loss ratio (example for tournament_id = 4)
SELECT 
    tm.team_id,
    tm.team_name,
    COUNT(DISTINCT m.match_id) AS matches_played,
    SUM(CASE WHEN m.winner_id = tm.team_id THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != tm.team_id THEN 1 ELSE 0 END) AS losses,
    CASE 
        WHEN SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != tm.team_id THEN 1 ELSE 0 END) = 0 THEN 
            SUM(CASE WHEN m.winner_id = tm.team_id THEN 1 ELSE 0 END)
        ELSE 
            ROUND(SUM(CASE WHEN m.winner_id = tm.team_id THEN 1 ELSE 0 END) * 1.0 / 
                  SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != tm.team_id THEN 1 ELSE 0 END), 2)
    END AS win_loss_ratio,
    COALESCE(ROUND(AVG(s.score), 2), 0) AS avg_score
FROM teams tm
INNER JOIN registrations r ON tm.team_id = r.team_id
INNER JOIN tournaments t ON r.tournament_id = t.tournament_id
LEFT JOIN matches m ON t.tournament_id = m.tournament_id 
    AND (m.team1_id = tm.team_id OR m.team2_id = tm.team_id)
    AND m.status = 'completed'
LEFT JOIN scores s ON m.match_id = s.match_id AND s.team_id = tm.team_id
WHERE t.tournament_id = 4
GROUP BY tm.team_id, tm.team_name
ORDER BY wins DESC, avg_score DESC;

-- ----------------------------------------------------------------------------
-- QUERY 3: List All Tournaments a Team Has Joined
-- Purpose: Show tournament participation history for a team
-- Demonstrates: JOIN, Subqueries, Date functions
-- ----------------------------------------------------------------------------
-- All tournaments for a specific team (example: team_id = 1)
SELECT 
    t.tournament_id,
    t.name AS tournament_name,
    g.title AS game_title,
    t.start_date,
    t.end_date,
    t.prize_pool,
    t.status,
    r.reg_date,
    COUNT(DISTINCT m.match_id) AS matches_played,
    SUM(CASE WHEN m.winner_id = 1 THEN 1 ELSE 0 END) AS wins
FROM tournaments t
INNER JOIN registrations r ON t.tournament_id = r.tournament_id
INNER JOIN games g ON t.game_id = g.game_id
LEFT JOIN matches m ON t.tournament_id = m.tournament_id 
    AND (m.team1_id = 1 OR m.team2_id = 1)
    AND m.status = 'completed'
WHERE r.team_id = 1
GROUP BY t.tournament_id, t.name, g.title, t.start_date, t.end_date, t.prize_pool, t.status, r.reg_date
ORDER BY t.start_date DESC;

-- ----------------------------------------------------------------------------
-- QUERY 4: Win/Loss Ratio Per Team
-- Purpose: Calculate comprehensive win rate statistics
-- Demonstrates: Complex aggregation, CASE, Mathematical operations
-- ----------------------------------------------------------------------------
-- Win/Loss ratio and percentage for all teams
SELECT 
    t.team_id,
    t.team_name,
    COUNT(DISTINCT m.match_id) AS total_matches,
    SUM(CASE WHEN m.winner_id = t.team_id THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != t.team_id THEN 1 ELSE 0 END) AS losses,
    SUM(CASE WHEN m.winner_id IS NULL THEN 1 ELSE 0 END) AS draws,
    CASE 
        WHEN SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != t.team_id THEN 1 ELSE 0 END) = 0 THEN 
            CASE 
                WHEN SUM(CASE WHEN m.winner_id = t.team_id THEN 1 ELSE 0 END) > 0 THEN 999.99
                ELSE 0.00
            END
        ELSE 
            ROUND(SUM(CASE WHEN m.winner_id = t.team_id THEN 1 ELSE 0 END) * 1.0 / 
                  SUM(CASE WHEN m.winner_id IS NOT NULL AND m.winner_id != t.team_id THEN 1 ELSE 0 END), 2)
    END AS win_loss_ratio,
    ROUND(
        SUM(CASE WHEN m.winner_id = t.team_id THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(DISTINCT m.match_id), 0), 
        2
    ) AS win_percentage
FROM teams t
LEFT JOIN matches m ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
    AND m.status = 'completed'
GROUP BY t.team_id, t.team_name
ORDER BY win_percentage DESC, wins DESC;

-- ----------------------------------------------------------------------------
-- QUERY 5: Upcoming Matches Schedule
-- Purpose: Show scheduled matches with team details
-- Demonstrates: JOIN, Date filtering, String formatting
-- ----------------------------------------------------------------------------
SELECT 
    m.match_id,
    t.name AS tournament_name,
    g.title AS game,
    t1.team_name AS team1,
    t2.team_name AS team2,
    m.match_time,
    m.round_number,
    DATEDIFF(m.match_time, CURDATE()) AS days_until_match
FROM matches m
INNER JOIN tournaments t ON m.tournament_id = t.tournament_id
INNER JOIN games g ON t.game_id = g.game_id
INNER JOIN teams t1 ON m.team1_id = t1.team_id
INNER JOIN teams t2 ON m.team2_id = t2.team_id
WHERE m.status = 'scheduled' AND m.match_time > NOW()
ORDER BY m.match_time ASC;

-- ----------------------------------------------------------------------------
-- QUERY 6: Player Statistics in Teams
-- Purpose: Show player distribution and team roster details
-- Demonstrates: GROUP BY, COUNT, Multiple JOINs
-- ----------------------------------------------------------------------------
SELECT 
    t.team_id,
    t.team_name,
    u.name AS captain_name,
    COUNT(p.player_id) AS total_players,
    GROUP_CONCAT(CONCAT(u2.name, ' (', p.game_tag, ')') SEPARATOR ', ') AS player_list
FROM teams t
INNER JOIN users u ON t.captain_id = u.user_id
LEFT JOIN players p ON t.team_id = p.team_id
LEFT JOIN users u2 ON p.user_id = u2.user_id
GROUP BY t.team_id, t.team_name, u.name
ORDER BY total_players DESC;

-- ----------------------------------------------------------------------------
-- QUERY 7: Most Popular Games by Tournament Count
-- Purpose: Identify which games have most tournaments
-- Demonstrates: Aggregation, JOIN, Statistical analysis
-- ----------------------------------------------------------------------------
SELECT 
    g.game_id,
    g.title,
    g.genre,
    COUNT(t.tournament_id) AS tournament_count,
    SUM(t.prize_pool) AS total_prize_money,
    COUNT(DISTINCT r.team_id) AS unique_teams_participated,
    COUNT(DISTINCT m.match_id) AS total_matches_played
FROM games g
LEFT JOIN tournaments t ON g.game_id = t.game_id
LEFT JOIN registrations r ON t.tournament_id = r.tournament_id
LEFT JOIN matches m ON t.tournament_id = m.tournament_id AND m.status = 'completed'
GROUP BY g.game_id, g.title, g.genre
ORDER BY tournament_count DESC, total_prize_money DESC;

-- ============================================================================
-- UTILITY QUERIES FOR TESTING AND VERIFICATION
-- ============================================================================

-- Verify all tables have data
SELECT 'users' AS table_name, COUNT(*) AS record_count FROM users
UNION ALL
SELECT 'teams', COUNT(*) FROM teams
UNION ALL
SELECT 'players', COUNT(*) FROM players
UNION ALL
SELECT 'games', COUNT(*) FROM games
UNION ALL
SELECT 'tournaments', COUNT(*) FROM tournaments
UNION ALL
SELECT 'registrations', COUNT(*) FROM registrations
UNION ALL
SELECT 'matches', COUNT(*) FROM matches
UNION ALL
SELECT 'scores', COUNT(*) FROM scores;

-- ============================================================================
-- END OF SQL SCHEMA
-- ============================================================================
