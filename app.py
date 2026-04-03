from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'valorant-team-finder-secret-key-change-in-production'

DATABASE = 'valorant_teams.db'

# Database connection helper
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize database
def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

# Routes
@app.route('/')
def index():
    db = get_db()
    
    # Get featured players (looking for team)
    players = db.execute('''
        SELECT p.*, u.username 
        FROM players p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.looking_for_team = 1 
        ORDER BY p.created_at DESC 
        LIMIT 6
    ''').fetchall()
    
    # Get featured teams (looking for players)
    teams = db.execute('''
        SELECT * FROM teams 
        WHERE looking_for_players = 1 
        ORDER BY created_at DESC 
        LIMIT 6
    ''').fetchall()
    
    return render_template('index.html', players=players, teams=teams)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            error = f'User {username} is already registered.'
        elif db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
            error = f'Email {email} is already registered.'
            
        if error is None:
            db.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        flash(error, 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash(error, 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Check if user has a player profile
    player = db.execute('SELECT * FROM players WHERE user_id = ?', (user_id,)).fetchone()
    
    # Check if user owns a team
    team = db.execute('SELECT * FROM teams WHERE captain_id = ?', (user_id,)).fetchone()
    
    # Get team applications if user owns a team
    applications = []
    if team:
        applications = db.execute('''
            SELECT a.*, p.game_username, p.rank, p.role, p.main_agent, u.username
            FROM team_applications a
            JOIN players p ON a.player_id = p.id
            JOIN users p_user ON p.user_id = p_user.id
            JOIN users u ON a.user_id = u.id
            WHERE a.team_id = ? AND a.status = 'pending'
            ORDER BY a.created_at DESC
        ''', (team['id'],)).fetchall()
    
    # Get user's applications
    my_applications = db.execute('''
        SELECT a.*, t.name as team_name, t.tag as team_tag
        FROM team_applications a
        JOIN teams t ON a.team_id = t.id
        WHERE a.user_id = ?
        ORDER BY a.created_at DESC
    ''', (user_id,)).fetchall()
    
    return render_template('dashboard.html', player=player, team=team, 
                          applications=applications, my_applications=my_applications)

@app.route('/player/create', methods=['GET', 'POST'])
def create_player():
    if 'user_id' not in session:
        flash('Please log in to create a profile.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Check if profile already exists
    existing = db.execute('SELECT id FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if existing:
        flash('You already have a player profile. Edit it instead.', 'info')
        return redirect(url_for('edit_player'))
    
    if request.method == 'POST':
        game_username = request.form['game_username']
        rank = request.form['rank']
        role = request.form['role']
        main_agent = request.form['main_agent']
        kd_ratio = request.form.get('kd_ratio', '')
        mic = 1 if request.form.get('mic') else 0
        availability = request.form.get('availability', '')
        bio = request.form.get('bio', '')
        looking_for_team = 1 if request.form.get('looking_for_team') else 0
        
        db.execute('''
            INSERT INTO players (user_id, game_username, rank, role, main_agent, 
                               kd_ratio, mic, availability, bio, looking_for_team)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, game_username, rank, role, main_agent, 
              kd_ratio if kd_ratio else None, mic, availability, bio, looking_for_team))
        db.commit()
        
        flash('Player profile created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_player.html')

@app.route('/player/edit', methods=['GET', 'POST'])
def edit_player():
    if 'user_id' not in session:
        flash('Please log in to edit your profile.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    player = db.execute('SELECT * FROM players WHERE user_id = ?', (user_id,)).fetchone()
    
    if not player:
        flash('You need to create a profile first.', 'info')
        return redirect(url_for('create_player'))
    
    if request.method == 'POST':
        game_username = request.form['game_username']
        rank = request.form['rank']
        role = request.form['role']
        main_agent = request.form['main_agent']
        kd_ratio = request.form.get('kd_ratio', '')
        mic = 1 if request.form.get('mic') else 0
        availability = request.form.get('availability', '')
        bio = request.form.get('bio', '')
        looking_for_team = 1 if request.form.get('looking_for_team') else 0
        
        db.execute('''
            UPDATE players 
            SET game_username = ?, rank = ?, role = ?, main_agent = ?, 
                kd_ratio = ?, mic = ?, availability = ?, bio = ?, looking_for_team = ?
            WHERE user_id = ?
        ''', (game_username, rank, role, main_agent, 
              kd_ratio if kd_ratio else None, mic, availability, bio, looking_for_team, user_id))
        db.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_player.html', player=player)

@app.route('/players')
def list_players():
    db = get_db()
    
    # Get filter parameters
    rank_filter = request.args.get('rank', '')
    role_filter = request.args.get('role', '')
    looking_only = request.args.get('looking', '')
    
    query = '''
        SELECT p.*, u.username 
        FROM players p 
        JOIN users u ON p.user_id = u.id 
        WHERE 1=1
    '''
    params = []
    
    if rank_filter:
        query += ' AND p.rank = ?'
        params.append(rank_filter)
    
    if role_filter:
        query += ' AND p.role = ?'
        params.append(role_filter)
    
    if looking_only:
        query += ' AND p.looking_for_team = 1'
    
    query += ' ORDER BY p.created_at DESC'
    
    players = db.execute(query, params).fetchall()
    
    # Get unique ranks and roles for filters
    ranks = db.execute('SELECT DISTINCT rank FROM players ORDER BY rank').fetchall()
    roles = db.execute('SELECT DISTINCT role FROM players ORDER BY role').fetchall()
    
    return render_template('players.html', players=players, ranks=ranks, roles=roles,
                          rank_filter=rank_filter, role_filter=role_filter, looking_only=looking_only)

@app.route('/player/<int:player_id>')
def view_player(player_id):
    db = get_db()
    player = db.execute('''
        SELECT p.*, u.username, u.email 
        FROM players p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.id = ?
    ''', (player_id,)).fetchone()
    
    if not player:
        flash('Player not found.', 'error')
        return redirect(url_for('list_players'))
    
    # Get player's team if any
    team = db.execute('''
        SELECT t.* FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.player_id = ?
    ''', (player_id,)).fetchone()
    
    return render_template('view_player.html', player=player, team=team)

@app.route('/team/create', methods=['GET', 'POST'])
def create_team():
    if 'user_id' not in session:
        flash('Please log in to create a team.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Check if user already owns a team
    existing = db.execute('SELECT id FROM teams WHERE captain_id = ?', (user_id,)).fetchone()
    if existing:
        flash('You already own a team.', 'info')
        return redirect(url_for('edit_team'))
    
    # Check if user has a player profile
    player = db.execute('SELECT id FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if not player:
        flash('You need to create a player profile first.', 'info')
        return redirect(url_for('create_player'))
    
    if request.method == 'POST':
        name = request.form['name']
        tag = request.form['tag']
        description = request.form.get('description', '')
        requirements = request.form.get('requirements', '')
        looking_for_players = 1 if request.form.get('looking_for_players') else 0
        
        db.execute('''
            INSERT INTO teams (captain_id, name, tag, description, requirements, looking_for_players)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, tag, description, requirements, looking_for_players))
        
        team_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # Add captain as team member
        db.execute('INSERT INTO team_members (team_id, player_id, role) VALUES (?, ?, ?)',
                  (team_id, player['id'], 'Captain'))
        db.commit()
        
        flash('Team created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_team.html')

@app.route('/team/edit', methods=['GET', 'POST'])
def edit_team():
    if 'user_id' not in session:
        flash('Please log in to edit your team.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    team = db.execute('SELECT * FROM teams WHERE captain_id = ?', (user_id,)).fetchone()
    
    if not team:
        flash('You do not own a team.', 'info')
        return redirect(url_for('create_team'))
    
    if request.method == 'POST':
        name = request.form['name']
        tag = request.form['tag']
        description = request.form.get('description', '')
        requirements = request.form.get('requirements', '')
        looking_for_players = 1 if request.form.get('looking_for_players') else 0
        
        db.execute('''
            UPDATE teams 
            SET name = ?, tag = ?, description = ?, requirements = ?, looking_for_players = ?
            WHERE captain_id = ?
        ''', (name, tag, description, requirements, looking_for_players, user_id))
        db.commit()
        
        flash('Team updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get team members
    members = db.execute('''
        SELECT tm.*, p.game_username, p.rank, p.role, p.main_agent
        FROM team_members tm
        JOIN players p ON tm.player_id = p.id
        WHERE tm.team_id = ?
    ''', (team['id'],)).fetchall()
    
    return render_template('edit_team.html', team=team, members=members)

@app.route('/teams')
def list_teams():
    db = get_db()
    
    # Get filter parameters
    looking_only = request.args.get('looking', '')
    
    query = '''
        SELECT t.*, u.username as captain_name
        FROM teams t
        JOIN users u ON t.captain_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if looking_only:
        query += ' AND t.looking_for_players = 1'
    
    query += ' ORDER BY t.created_at DESC'
    
    teams = db.execute(query, params).fetchall()
    
    return render_template('teams.html', teams=teams, looking_only=looking_only)

@app.route('/team/<int:team_id>')
def view_team(team_id):
    db = get_db()
    team = db.execute('''
        SELECT t.*, u.username as captain_name
        FROM teams t
        JOIN users u ON t.captain_id = u.id
        WHERE t.id = ?
    ''', (team_id,)).fetchone()
    
    if not team:
        flash('Team not found.', 'error')
        return redirect(url_for('list_teams'))
    
    # Get team members
    members = db.execute('''
        SELECT tm.*, p.game_username, p.rank, p.role, p.main_agent, p.id as player_id
        FROM team_members tm
        JOIN players p ON tm.player_id = p.id
        WHERE tm.team_id = ?
    ''', (team_id,)).fetchall()
    
    # Check if current user is captain
    is_captain = 'user_id' in session and team['captain_id'] == session['user_id']
    
    # Check if current user has a player profile and can apply
    can_apply = False
    already_applied = False
    if 'user_id' in session:
        player = db.execute('SELECT id FROM players WHERE user_id = ?', 
                          (session['user_id'],)).fetchone()
        if player:
            can_apply = True
            # Check if already applied
            existing_app = db.execute(
                'SELECT id FROM team_applications WHERE team_id = ? AND user_id = ? AND status = "pending"',
                (team_id, session['user_id'])
            ).fetchone()
            if existing_app:
                already_applied = True
    
    return render_template('view_team.html', team=team, members=members, 
                          is_captain=is_captain, can_apply=can_apply, already_applied=already_applied)

@app.route('/team/<int:team_id>/apply', methods=['POST'])
def apply_to_team(team_id):
    if 'user_id' not in session:
        flash('Please log in to apply.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Get player profile
    player = db.execute('SELECT id FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if not player:
        flash('You need to create a player profile first.', 'info')
        return redirect(url_for('create_player'))
    
    # Check if already applied
    existing = db.execute(
        'SELECT id FROM team_applications WHERE team_id = ? AND user_id = ? AND status = "pending"',
        (team_id, user_id)
    ).fetchone()
    
    if existing:
        flash('You have already applied to this team.', 'info')
        return redirect(url_for('view_team', team_id=team_id))
    
    message = request.form.get('message', '')
    
    db.execute('''
        INSERT INTO team_applications (team_id, user_id, player_id, message, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
    ''', (team_id, user_id, player['id'], message, datetime.now()))
    db.commit()
    
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('view_team', team_id=team_id))

@app.route('/application/<int:app_id>/<action>')
def handle_application(app_id, action):
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))
    
    if action not in ['accept', 'reject']:
        flash('Invalid action.', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Get the application and verify the user is the team captain
    application = db.execute('''
        SELECT a.*, t.captain_id
        FROM team_applications a
        JOIN teams t ON a.team_id = t.id
        WHERE a.id = ?
    ''', (app_id,)).fetchone()
    
    if not application or application['captain_id'] != user_id:
        flash('You are not authorized to handle this application.', 'error')
        return redirect(url_for('dashboard'))
    
    status = 'accepted' if action == 'accept' else 'rejected'
    db.execute('UPDATE team_applications SET status = ? WHERE id = ?', (status, app_id))
    
    # If accepted, add player to team
    if action == 'accept':
        db.execute('''
            INSERT INTO team_members (team_id, player_id, role)
            VALUES (?, ?, 'Member')
        ''', (application['team_id'], application['player_id']))
        
        # Update player's looking_for_team status
        db.execute('UPDATE players SET looking_for_team = 0 WHERE id = ?', 
                  (application['player_id'],))
    
    db.commit()
    
    flash(f'Application {status}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/team/leave', methods=['POST'])
def leave_team():
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Get player profile
    player = db.execute('SELECT id FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if not player:
        flash('Player profile not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Remove from team
    db.execute('DELETE FROM team_members WHERE player_id = ?', (player['id'],))
    
    # Update player status to looking for team
    db.execute('UPDATE players SET looking_for_team = 1 WHERE id = ?', (player['id'],))
    db.commit()
    
    flash('You have left the team.', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DATABASE):
        init_db()
    
    app.run(debug=True, port=5000)
