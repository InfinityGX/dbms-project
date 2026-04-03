#!/usr/bin/env python3
"""
Sample data generator for Valorant Team Finder
Run this to populate the database with sample users, players, and teams.
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DATABASE = 'valorant_teams.db'

# Sample data
RANKS = ['Iron 3', 'Bronze 2', 'Silver 1', 'Silver 3', 'Gold 2', 'Gold 3', 
         'Platinum 1', 'Platinum 2', 'Diamond 1', 'Ascendant 2', 'Immortal 1']

ROLES = ['Duelist', 'Initiator', 'Controller', 'Sentinel', 'Flex']

AGENTS = {
    'Duelist': ['Jett', 'Phoenix', 'Raze', 'Reyna', 'Yoru', 'Neon', 'Iso'],
    'Initiator': ['Sova', 'Breach', 'Skye', 'KAY/O', 'Fade', 'Gekko'],
    'Controller': ['Brimstone', 'Viper', 'Omen', 'Astra', 'Harbor', 'Clove'],
    'Sentinel': ['Sage', 'Cypher', 'Killjoy', 'Chamber', 'Deadlock', 'Vyse'],
    'Flex': ['Jett', 'Sage', 'Omen', 'Sova', 'Killjoy']
}

SAMPLE_PLAYERS = [
    {'username': 'phantom_ace', 'game': 'Phantom#ACE', 'rank': 'Diamond 1', 'role': 'Duelist', 'agent': 'Jett', 'kd': 1.35},
    {'username': 'sage_healer', 'game': 'SageMain#HEAL', 'rank': 'Platinum 2', 'role': 'Sentinel', 'agent': 'Sage', 'kd': 0.95},
    {'username': 'omen_smoke', 'game': 'OmenSmoke#001', 'rank': 'Gold 3', 'role': 'Controller', 'agent': 'Omen', 'kd': 1.12},
    {'username': 'sova_arrow', 'game': 'SovaMain#DRONE', 'rank': 'Ascendant 2', 'role': 'Initiator', 'agent': 'Sova', 'kd': 1.28},
    {'username': 'reyna_fragger', 'game': 'ReynaDemon#1337', 'rank': 'Immortal 1', 'role': 'Duelist', 'agent': 'Reyna', 'kd': 1.55},
    {'username': 'kj_lockdown', 'game': 'Killjoy#TURTLE', 'rank': 'Platinum 1', 'role': 'Sentinel', 'agent': 'Killjoy', 'kd': 1.08},
    {'username': 'breach_flash', 'game': 'BreachFlash#STUN', 'rank': 'Gold 2', 'role': 'Initiator', 'agent': 'Breach', 'kd': 0.98},
    {'username': 'viper_wall', 'game': 'ViperMain#TOXIC', 'rank': 'Diamond 1', 'role': 'Controller', 'agent': 'Viper', 'kd': 1.22},
    {'username': 'clutch_king', 'game': 'ClutchKing#1v5', 'rank': 'Silver 3', 'role': 'Flex', 'agent': 'Chamber', 'kd': 1.05},
    {'username': 'raze_boom', 'game': 'RazeBlast#BOOM', 'rank': 'Gold 1', 'role': 'Duelist', 'agent': 'Raze', 'kd': 1.18},
    {'username': 'skye_heal', 'game': 'SkyeDog#GUIDE', 'rank': 'Platinum 3', 'role': 'Initiator', 'agent': 'Skye', 'kd': 1.15},
    {'username': 'cypher_cam', 'game': 'CypherInfo#CAMS', 'rank': 'Silver 1', 'role': 'Sentinel', 'agent': 'Cypher', 'kd': 0.92},
]

SAMPLE_TEAMS = [
    {'name': 'Phoenix Rising', 'tag': 'RISE', 'captain': 'phantom_ace',
     'desc': 'Competitive team looking for dedicated players. We practice 3x/week.',
     'req': 'Gold+ rank, good comms, available evenings'},
    {'name': 'Viper Strike', 'tag': 'VIPER', 'captain': 'viper_wall',
     'desc': 'Strategic team focused on coordinated plays and team tactics.',
     'req': 'Platinum+, willing to learn strats, has mic'},
    {'name': 'Iron Legion', 'tag': 'IRON', 'captain': 'clutch_king',
     'desc': 'Casual team for fun games and improvement. All ranks welcome!',
     'req': 'Any rank, good attitude, wants to improve'},
    {'name': 'Ascendant Gaming', 'tag': 'AG', 'captain': 'sova_arrow',
     'desc': 'High-level competitive team aiming for tournaments.',
     'req': 'Diamond+, serious about comp, flexible schedule'},
]

def create_sample_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Creating sample data...")
    
    # Create users and players
    for i, player_data in enumerate(SAMPLE_PLAYERS):
        email = f"{player_data['username']}@college.edu"
        password_hash = generate_password_hash('password123')
        
        # Insert user
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (player_data['username'], email, password_hash, datetime.now()))
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (player_data['username'],))
        user_id = cursor.fetchone()[0]
        
        # Insert player profile
        cursor.execute('''
            INSERT OR IGNORE INTO players 
            (user_id, game_username, rank, role, main_agent, kd_ratio, mic, 
             availability, bio, looking_for_team, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            player_data['game'],
            player_data['rank'],
            player_data['role'],
            player_data['agent'],
            player_data['kd'],
            1,  # Has mic
            'Weekdays 7PM-11PM, Weekends flexible',
            f"Hi! I'm a {player_data['rank']} {player_data['role']} main. Looking for a team to improve with!",
            1,  # Looking for team
            datetime.now()
        ))
        
        print(f"  Created player: {player_data['game']}")
    
    # Create teams
    for team_data in SAMPLE_TEAMS:
        # Get captain user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (team_data['captain'],))
        captain_user = cursor.fetchone()
        if not captain_user:
            continue
        captain_user_id = captain_user[0]
        
        # Get captain player ID
        cursor.execute('SELECT id FROM players WHERE user_id = ?', (captain_user_id,))
        captain_player = cursor.fetchone()
        if not captain_player:
            continue
        captain_player_id = captain_player[0]
        
        # Insert team
        cursor.execute('''
            INSERT OR IGNORE INTO teams 
            (captain_id, name, tag, description, requirements, looking_for_players, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            captain_user_id,
            team_data['name'],
            team_data['tag'],
            team_data['desc'],
            team_data['req'],
            1,
            datetime.now()
        ))
        
        # Get team ID
        cursor.execute('SELECT id FROM teams WHERE name = ?', (team_data['name'],))
        team_id = cursor.fetchone()[0]
        
        # Add captain as team member
        cursor.execute('''
            INSERT OR IGNORE INTO team_members (team_id, player_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (team_id, captain_player_id, 'Captain', datetime.now()))
        
        # Update captain's looking_for_team status
        cursor.execute('UPDATE players SET looking_for_team = 0 WHERE id = ?', (captain_player_id,))
        
        print(f"  Created team: {team_data['name']} [{team_data['tag']}]")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Sample data created successfully!")
    print("\nTest accounts:")
    print("  Username: phantom_ace  | Password: password123")
    print("  Username: sage_healer | Password: password123")
    print("  Username: omen_smoke  | Password: password123")
    print("  ... and 9 more players")
    print("\nYou can now login with any of these accounts to test the app!")

if __name__ == '__main__':
    create_sample_data()
