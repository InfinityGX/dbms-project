-- Valorant Team Finder Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players table (extends users with game-specific info)
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    game_username TEXT NOT NULL,
    rank TEXT NOT NULL CHECK(rank IN ('Iron 1', 'Iron 2', 'Iron 3', 
                                      'Bronze 1', 'Bronze 2', 'Bronze 3',
                                      'Silver 1', 'Silver 2', 'Silver 3',
                                      'Gold 1', 'Gold 2', 'Gold 3',
                                      'Platinum 1', 'Platinum 2', 'Platinum 3',
                                      'Diamond 1', 'Diamond 2', 'Diamond 3',
                                      'Ascendant 1', 'Ascendant 2', 'Ascendant 3',
                                      'Immortal 1', 'Immortal 2', 'Immortal 3',
                                      'Radiant')),
    role TEXT NOT NULL CHECK(role IN ('Duelist', 'Initiator', 'Controller', 'Sentinel', 'Flex')),
    main_agent TEXT,
    kd_ratio REAL,
    mic INTEGER DEFAULT 0, -- 0 = no mic, 1 = has mic
    availability TEXT, -- e.g., "Weekdays 6PM-10PM, Weekends all day"
    bio TEXT,
    looking_for_team INTEGER DEFAULT 1, -- 0 = not looking, 1 = looking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captain_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    tag TEXT, -- Team tag like "TSM" or "SEN"
    description TEXT,
    requirements TEXT, -- Requirements for joining
    looking_for_players INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (captain_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Team members junction table
CREATE TABLE IF NOT EXISTS team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL UNIQUE, -- A player can only be in one team
    role TEXT DEFAULT 'Member', -- Role within the team (Captain, Member, etc.)
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
);

-- Team applications table
CREATE TABLE IF NOT EXISTS team_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_players_looking ON players(looking_for_team);
CREATE INDEX IF NOT EXISTS idx_players_rank ON players(rank);
CREATE INDEX IF NOT EXISTS idx_players_role ON players(role);
CREATE INDEX IF NOT EXISTS idx_teams_looking ON teams(looking_for_players);
CREATE INDEX IF NOT EXISTS idx_applications_status ON team_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_team ON team_applications(team_id);
