# Valorant Team Finder

A web application to help Valorant players in a closed college environment find teammates and form competitive teams.

## Features

- ✅ **User Authentication** - Register/Login with secure password hashing
- ✅ **Player Profiles** - Create profiles with rank, role, main agent, K/D ratio, and availability
- ✅ **Team Management** - Create and manage teams, recruit players
- ✅ **Search & Filter** - Find players by rank, role, and availability
- ✅ **Applications System** - Players can apply to teams, captains can approve/reject
- ✅ **Valorant Theme** - Dark UI with red accents matching Valorant aesthetic

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS (Jinja2 templates)
- **Authentication**: Session-based with Werkzeug security

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python app.py
```

The database will be created automatically on first run.

### 3. Add Sample Data (Optional)

```bash
python create_sample_data.py
```

This creates 12 sample players and 4 teams for testing.

### 4. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

### 5. Test Login Credentials (if using sample data)

- Username: `phantom_ace` | Password: `password123`
- Username: `sage_healer` | Password: `password123`
- Username: `reyna_fragger` | Password: `password123`

## Database Schema

### Tables

1. **users** - User accounts
   - id, username, email, password_hash, created_at

2. **players** - Player profiles
   - id, user_id, game_username, rank, role, main_agent, kd_ratio, mic, availability, bio, looking_for_team

3. **teams** - Team information
   - id, captain_id, name, tag, description, requirements, looking_for_players

4. **team_members** - Team roster
   - id, team_id, player_id, role, joined_at

5. **team_applications** - Player applications to teams
   - id, team_id, user_id, player_id, message, status, created_at

## Features for College Environment

1. **Closed System** - Email-based registration (recommend college email validation)
2. **Skill Matching** - Filter by rank and role
3. **Availability** - See when players are free to play
4. **Team Building** - Easy application and recruitment system

## Customization Ideas

- Add Discord integration for team communication
- Add scrimmage scheduling feature
- Add tournament bracket system
- Add player statistics tracking
- Add review/rating system for players

## Screenshots

The application features a dark Valorant-themed UI with:
- Red accent colors matching Valorant branding
- Card-based layouts for players and teams
- Responsive design for mobile and desktop
- Clean navigation and user flows

