"""
============================================================================
ESPORTS COMPETITION ORGANIZATION AND TEAM MANAGEMENT SYSTEM - Flask Backend
============================================================================
Author: College DBMS Project
Date: October 29, 2025
Framework: Flask
Database: MySQL (esports_db)
============================================================================

This Flask application provides a complete backend for managing esports
tournaments, teams, players, matches, and leaderboards. It demonstrates
comprehensive MySQL database integration with proper error handling.

Key Features:
- User registration and authentication
- Team creation and management
- Tournament organization
- Match recording and scoring
- Real-time leaderboards
- Complex SQL queries and stored procedures
============================================================================
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime
from functools import wraps
import os

# Add dotenv loading
from dotenv import load_dotenv

# Load .env from project root (if present)
load_dotenv()

# ============================================================================
# FLASK APPLICATION CONFIGURATION
# ============================================================================

app = Flask(__name__)

# Use environment variables (with safe defaults) instead of hardcoded values
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')

# MySQL Database Configuration (read from environment)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'esports_db')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS', 'DictCursor')

# Optional: store debug flag in config
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')

# Initialize MySQL connection
mysql = MySQL(app)

# ============================================================================
# UTILITY FUNCTIONS AND DECORATORS
# ============================================================================

def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to protect routes that require admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ROUTE: HOME PAGE
# ============================================================================

@app.route('/')
def index():
    """
    Home page showing overview of tournaments and statistics.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Get upcoming tournaments
        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date, t.prize_pool
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            WHERE t.status = 'upcoming'
            ORDER BY t.start_date ASC
            LIMIT 5
        """)
        upcoming_tournaments = cursor.fetchall()
        
        # Get ongoing tournaments
        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date, t.prize_pool
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            WHERE t.status = 'ongoing'
            ORDER BY t.start_date ASC
        """)
        ongoing_tournaments = cursor.fetchall()
        
        # Get top teams
        cursor.execute("""
            SELECT team_id, team_name, total_wins, avg_score_all_time, overall_win_rate
            FROM team_performance_summary
            ORDER BY total_wins DESC, avg_score_all_time DESC
            LIMIT 5
        """)
        top_teams = cursor.fetchall()
        
        cursor.close()
        
        return render_template('index.html', 
                             upcoming=upcoming_tournaments,
                             ongoing=ongoing_tournaments,
                             top_teams=top_teams)
    except Exception as e:
        flash(f'Error loading home page: {str(e)}', 'danger')
        return render_template('index.html', upcoming=[], ongoing=[], top_teams=[])


# ============================================================================
# ROUTE: USER REGISTRATION
# ============================================================================

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    """
    Register a new user in the system.
    
    Method: POST
    Parameters:
        - name: User's full name
        - email: User's email address (unique)
        - password: User's password (should be hashed in production)
        - role: User role (admin, player, organizer)
    
    Returns: Success message or error
    """
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'player')
            
            # Input validation
            if not all([name, email, password]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('register_user'))
            
            if role not in ['admin', 'player', 'organizer']:
                flash('Invalid role selected!', 'danger')
                return redirect(url_for('register_user'))
            
            cursor = mysql.connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Email already registered!', 'warning')
                cursor.close()
                return redirect(url_for('register_user'))
            
            # Insert new user
            # NOTE: In production, use password hashing (bcrypt, werkzeug.security, etc.)
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (name, email, password, role))
            
            mysql.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            
            flash(f'User registered successfully! User ID: {user_id}', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error registering user: {str(e)}', 'danger')
            return redirect(url_for('register_user'))
    
    return render_template('register_user.html')


# ============================================================================
# ROUTE: USER LOGIN
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login functionality.
    Creates a session for authenticated users.
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not all([email, password]):
                flash('Email and password are required!', 'danger')
                return redirect(url_for('login'))
            
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT user_id, name, email, role 
                FROM users 
                WHERE email = %s AND password = %s
            """, (email, password))
            
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                # Create session
                session['user_id'] = user['user_id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['role'] = user['role']
                
                flash(f'Welcome, {user["name"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password!', 'danger')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


# ============================================================================
# ROUTE: USER LOGOUT
# ============================================================================

@app.route('/logout')
def logout():
    """
    Logout user and clear session.
    """
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ============================================================================
# ROUTE: CREATE TEAM
# ============================================================================

@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    """
    Create a new team with the current user as captain.
    
    Method: POST
    Parameters:
        - team_name: Name of the team (unique)
    
    Returns: Success message with team_id or error
    """
    if request.method == 'POST':
        try:
            team_name = request.form.get('team_name')
            
            if not team_name:
                flash('Team name is required!', 'danger')
                return redirect(url_for('create_team'))
            
            cursor = mysql.connection.cursor()
            
            # Check if team name already exists
            cursor.execute("SELECT team_id FROM teams WHERE team_name = %s", (team_name,))
            existing_team = cursor.fetchone()
            
            if existing_team:
                flash('Team name already exists!', 'warning')
                cursor.close()
                return redirect(url_for('create_team'))
            
            # Create team with current user as captain
            captain_id = session['user_id']
            cursor.execute("""
                INSERT INTO teams (team_name, captain_id)
                VALUES (%s, %s)
            """, (team_name, captain_id))
            
            mysql.connection.commit()
            team_id = cursor.lastrowid
            cursor.close()
            
            flash(f'Team "{team_name}" created successfully! Team ID: {team_id}', 'success')
            return redirect(url_for('view_teams'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating team: {str(e)}', 'danger')
            return redirect(url_for('create_team'))
    
    return render_template('create_team.html')


# ============================================================================
# ROUTE: ADD PLAYER TO TEAM
# ============================================================================

@app.route('/add_player', methods=['GET', 'POST'])
@login_required
def add_player():
    """
    Add a player to a team.
    
    Method: POST
    Parameters:
        - user_id: ID of user to add as player
        - team_id: ID of team to join
        - game_tag: Player's in-game username/tag
    
    Returns: Success message or error
    """
    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id')
            team_id = request.form.get('team_id')
            game_tag = request.form.get('game_tag')
            
            if not all([user_id, team_id, game_tag]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('add_player'))
            
            cursor = mysql.connection.cursor()
            
            # Verify user exists and is a player
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                flash('User not found!', 'danger')
                cursor.close()
                return redirect(url_for('add_player'))
            
            # Verify team exists
            cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (team_id,))
            team = cursor.fetchone()
            
            if not team:
                flash('Team not found!', 'danger')
                cursor.close()
                return redirect(url_for('add_player'))
            
            # Check if player already in this team
            cursor.execute("""
                SELECT player_id FROM players 
                WHERE user_id = %s AND team_id = %s
            """, (user_id, team_id))
            existing = cursor.fetchone()
            
            if existing:
                flash('Player already in this team!', 'warning')
                cursor.close()
                return redirect(url_for('add_player'))
            
            # Add player to team
            cursor.execute("""
                INSERT INTO players (user_id, team_id, game_tag)
                VALUES (%s, %s, %s)
            """, (user_id, team_id, game_tag))
            
            mysql.connection.commit()
            player_id = cursor.lastrowid
            cursor.close()
            
            flash(f'Player added to team successfully! Player ID: {player_id}', 'success')
            return redirect(url_for('view_teams'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error adding player: {str(e)}', 'danger')
            return redirect(url_for('add_player'))
    
    # GET request - fetch teams and users for form
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT team_id, team_name FROM teams ORDER BY team_name")
        teams = cursor.fetchall()
        
        cursor.execute("""
            SELECT user_id, name, email 
            FROM users 
            WHERE role = 'player'
            ORDER BY name
        """)
        users = cursor.fetchall()
        
        cursor.close()
        
        return render_template('add_player.html', teams=teams, users=users)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'danger')
        return render_template('add_player.html', teams=[], users=[])


# ============================================================================
# ROUTE: CREATE TOURNAMENT
# ============================================================================

@app.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    """
    Create a new tournament.
    
    Method: POST
    Parameters:
        - name: Tournament name
        - game_id: ID of the game
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - prize_pool: Prize money (optional)
    
    Returns: Success message with tournament_id or error
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            game_id = request.form.get('game_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            prize_pool = request.form.get('prize_pool', 0)
            
            if not all([name, game_id, start_date, end_date]):
                flash('All required fields must be filled!', 'danger')
                return redirect(url_for('create_tournament'))
            
            # Validate dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end < start:
                flash('End date must be after start date!', 'danger')
                return redirect(url_for('create_tournament'))
            
            cursor = mysql.connection.cursor()
            
            # Insert tournament
            cursor.execute("""
                INSERT INTO tournaments (name, game_id, start_date, end_date, prize_pool)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, game_id, start_date, end_date, prize_pool))
            
            mysql.connection.commit()
            tournament_id = cursor.lastrowid
            cursor.close()
            
            flash(f'Tournament "{name}" created successfully! Tournament ID: {tournament_id}', 'success')
            return redirect(url_for('view_tournaments'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating tournament: {str(e)}', 'danger')
            return redirect(url_for('create_tournament'))
    
    # GET request - fetch games for dropdown
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT game_id, title, genre FROM games ORDER BY title")
        games = cursor.fetchall()
        cursor.close()
        
        return render_template('create_tournament.html', games=games)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'danger')
        return render_template('create_tournament.html', games=[])


# ============================================================================
# ROUTE: REGISTER TEAM FOR TOURNAMENT
# ============================================================================

@app.route('/register_team', methods=['GET', 'POST'])
@login_required
def register_team():
    """
    Register a team for a tournament.
    
    Method: POST
    Parameters:
        - team_id: ID of the team
        - tournament_id: ID of the tournament
    
    Returns: Success message or error
    Note: Trigger prevents duplicate registrations
    """
    if request.method == 'POST':
        try:
            team_id = request.form.get('team_id')
            tournament_id = request.form.get('tournament_id')
            
            if not all([team_id, tournament_id]):
                flash('Team and tournament must be selected!', 'danger')
                return redirect(url_for('register_team'))
            
            cursor = mysql.connection.cursor()
            
            # The trigger 'prevent_duplicate_registration' will handle duplicate check
            cursor.execute("""
                INSERT INTO registrations (team_id, tournament_id)
                VALUES (%s, %s)
            """, (team_id, tournament_id))
            
            mysql.connection.commit()
            reg_id = cursor.lastrowid
            cursor.close()
            
            flash(f'Team registered for tournament successfully! Registration ID: {reg_id}', 'success')
            return redirect(url_for('view_tournaments'))
            
        except Exception as e:
            mysql.connection.rollback()
            error_msg = str(e)
            
            # Check if it's our custom trigger error
            if 'already registered' in error_msg.lower():
                flash('This team is already registered for this tournament!', 'warning')
            else:
                flash(f'Error registering team: {error_msg}', 'danger')
            
            return redirect(url_for('register_team'))
    
    # GET request - fetch teams and tournaments
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT team_id, team_name FROM teams ORDER BY team_name")
        teams = cursor.fetchall()
        
        cursor.execute("""
            SELECT tournament_id, name, start_date, end_date 
            FROM tournaments 
            WHERE status IN ('upcoming', 'ongoing')
            ORDER BY start_date
        """)
        tournaments = cursor.fetchall()
        
        cursor.close()
        
        return render_template('register_team.html', teams=teams, tournaments=tournaments)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'danger')
        return render_template('register_team.html', teams=[], tournaments=[])


# ============================================================================
# ROUTE: RECORD MATCH RESULT
# ============================================================================

@app.route('/record_match', methods=['GET', 'POST'])
@login_required
def record_match():
    """
    Record a match result using stored procedure.
    
    Method: POST
    Parameters:
        - tournament_id: Tournament ID
        - team1_id: First team ID
        - team2_id: Second team ID
        - team1_score: Score for team 1
        - team2_score: Score for team 2
        - match_time: Match date/time
        - round_number: Round number
    
    Uses: Stored procedure 'record_match_result'
    Returns: Success message or error
    """
    if request.method == 'POST':
        try:
            tournament_id = request.form.get('tournament_id')
            team1_id = request.form.get('team1_id')
            team2_id = request.form.get('team2_id')
            team1_score = request.form.get('team1_score')
            team2_score = request.form.get('team2_score')
            match_time = request.form.get('match_time')
            round_number = request.form.get('round_number', 1)
            
            if not all([tournament_id, team1_id, team2_id, team1_score, team2_score, match_time]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('record_match'))
            
            # Validate teams are different
            if team1_id == team2_id:
                flash('Teams must be different!', 'danger')
                return redirect(url_for('record_match'))
            
            # Convert match_time to proper datetime format
            match_datetime = datetime.strptime(match_time, '%Y-%m-%dT%H:%M')
            
            cursor = mysql.connection.cursor()
            
            # Call stored procedure to record match
            # This procedure handles match insertion and score recording in a transaction
            cursor.callproc('record_match_result', [
                tournament_id,
                team1_id,
                team2_id,
                int(team1_score),
                int(team2_score),
                match_datetime,
                int(round_number)
            ])
            
            # Fetch result from stored procedure
            result = cursor.fetchone()
            
            mysql.connection.commit()
            cursor.close()
            
            if result and 'match_id' in result:
                flash(f'Match recorded successfully! Match ID: {result["match_id"]}', 'success')
            else:
                flash('Match recorded successfully!', 'success')
            
            return redirect(url_for('view_matches'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error recording match: {str(e)}', 'danger')
            return redirect(url_for('record_match'))
    
    # GET request - fetch tournaments and teams
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT tournament_id, name, start_date 
            FROM tournaments 
            WHERE status IN ('ongoing', 'upcoming')
            ORDER BY start_date
        """)
        tournaments = cursor.fetchall()
        
        cursor.execute("SELECT team_id, team_name FROM teams ORDER BY team_name")
        teams = cursor.fetchall()
        
        cursor.close()
        
        return render_template('record_match.html', tournaments=tournaments, teams=teams)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'danger')
        return render_template('record_match.html', tournaments=[], teams=[])


# ============================================================================
# ROUTE: VIEW TOURNAMENT LEADERBOARD
# ============================================================================

@app.route('/leaderboard/<int:tournament_id>')
def leaderboard(tournament_id):
    """
    Display tournament leaderboard using the view 'tournament_leaderboard'.
    
    Method: GET
    URL Parameter: tournament_id
    
    Shows:
        - Team rankings
        - Wins, losses, draws
        - Average scores
        - Win rate percentage
    
    Uses: tournament_leaderboard VIEW
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Get tournament details
        cursor.execute("""
            SELECT t.name, t.start_date, t.end_date, t.prize_pool, t.status, g.title as game
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            WHERE t.tournament_id = %s
        """, (tournament_id,))
        tournament = cursor.fetchone()
        
        if not tournament:
            flash('Tournament not found!', 'danger')
            cursor.close()
            return redirect(url_for('view_tournaments'))
        
        # Get leaderboard data from VIEW
        cursor.execute("""
            SELECT team_id, team_name, matches_played, wins, losses, draws,
                   total_score, avg_score, win_rate_percentage
            FROM tournament_leaderboard
            WHERE tournament_id = %s
            ORDER BY wins DESC, avg_score DESC, total_score DESC
        """, (tournament_id,))
        leaderboard_data = cursor.fetchall()
        
        # Get recent matches for this tournament
        cursor.execute("""
            SELECT m.match_id, t1.team_name as team1, t2.team_name as team2,
                   tw.team_name as winner, m.match_time,
                   s1.score as team1_score, s2.score as team2_score
            FROM matches m
            INNER JOIN teams t1 ON m.team1_id = t1.team_id
            INNER JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN teams tw ON m.winner_id = tw.team_id
            LEFT JOIN scores s1 ON m.match_id = s1.match_id AND s1.team_id = t1.team_id
            LEFT JOIN scores s2 ON m.match_id = s2.match_id AND s2.team_id = t2.team_id
            WHERE m.tournament_id = %s AND m.status = 'completed'
            ORDER BY m.match_time DESC
            LIMIT 10
        """, (tournament_id,))
        recent_matches = cursor.fetchall()
        
        cursor.close()
        
        return render_template('leaderboard.html',
                             tournament=tournament,
                             leaderboard=leaderboard_data,
                             recent_matches=recent_matches,
                             tournament_id=tournament_id)
    except Exception as e:
        flash(f'Error loading leaderboard: {str(e)}', 'danger')
        return redirect(url_for('view_tournaments'))


# ============================================================================
# ROUTE: VIEW ALL TEAMS
# ============================================================================

@app.route('/teams')
def view_teams():
    """
    Display all teams with their statistics.
    Uses: team_performance_summary VIEW
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Get team performance data from VIEW
        cursor.execute("""
            SELECT team_id, team_name, captain_name, tournaments_participated,
                   total_matches, total_wins, total_losses, avg_score_all_time,
                   overall_win_rate
            FROM team_performance_summary
            ORDER BY total_wins DESC, avg_score_all_time DESC
        """)
        teams = cursor.fetchall()
        
        cursor.close()
        
        return render_template('teams.html', teams=teams)
    except Exception as e:
        flash(f'Error loading teams: {str(e)}', 'danger')
        return render_template('teams.html', teams=[])


# ============================================================================
# ROUTE: VIEW TEAM DETAILS
# ============================================================================

@app.route('/team/<int:team_id>')
def team_details(team_id):
    """
    Display detailed information about a specific team.
    Shows roster, statistics, and tournament history.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Get team basic info
        cursor.execute("""
            SELECT t.team_id, t.team_name, u.name as captain_name, t.created_at
            FROM teams t
            INNER JOIN users u ON t.captain_id = u.user_id
            WHERE t.team_id = %s
        """, (team_id,))
        team = cursor.fetchone()
        
        if not team:
            flash('Team not found!', 'danger')
            cursor.close()
            return redirect(url_for('view_teams'))
        
        # Get team roster
        cursor.execute("""
            SELECT p.player_id, u.name, u.email, p.game_tag, p.joined_at
            FROM players p
            INNER JOIN users u ON p.user_id = u.user_id
            WHERE p.team_id = %s
            ORDER BY p.joined_at
        """, (team_id,))
        roster = cursor.fetchall()
        
        # Get team statistics using stored procedure
        cursor.callproc('get_team_statistics', [team_id])
        stats = cursor.fetchone()
        
        # Get tournament history
        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date,
                   COUNT(DISTINCT m.match_id) as matches_played,
                   SUM(CASE WHEN m.winner_id = %s THEN 1 ELSE 0 END) as wins
            FROM tournaments t
            INNER JOIN registrations r ON t.tournament_id = r.tournament_id
            INNER JOIN games g ON t.game_id = g.game_id
            LEFT JOIN matches m ON t.tournament_id = m.tournament_id 
                AND (m.team1_id = %s OR m.team2_id = %s)
                AND m.status = 'completed'
            WHERE r.team_id = %s
            GROUP BY t.tournament_id, t.name, g.title, t.start_date, t.end_date
            ORDER BY t.start_date DESC
        """, (team_id, team_id, team_id, team_id))
        tournaments = cursor.fetchall()
        
        cursor.close()
        
        return render_template('team_details.html',
                             team=team,
                             roster=roster,
                             stats=stats,
                             tournaments=tournaments)
    except Exception as e:
        flash(f'Error loading team details: {str(e)}', 'danger')
        return redirect(url_for('view_teams'))


# ============================================================================
# ROUTE: VIEW ALL TOURNAMENTS
# ============================================================================

@app.route('/tournaments')
def view_tournaments():
    """
    Display all tournaments grouped by status.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Get upcoming tournaments
        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, 
                   t.end_date, t.prize_pool, COUNT(r.reg_id) as team_count
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            LEFT JOIN registrations r ON t.tournament_id = r.tournament_id
            WHERE t.status = 'upcoming'
            GROUP BY t.tournament_id, t.name, g.title, t.start_date, t.end_date, t.prize_pool
            ORDER BY t.start_date ASC
        """)
        upcoming = cursor.fetchall()
        
        # Get ongoing tournaments
        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, 
                   t.end_date, t.prize_pool, COUNT(r.reg_id) as team_count
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            LEFT JOIN registrations r ON t.tournament_id = r.tournament_id
            WHERE t.status = 'ongoing'
            GROUP BY t.tournament_id, t.name, g.title, t.start_date, t.end_date, t.prize_pool
            ORDER BY t.start_date ASC
        """)
        ongoing = cursor.fetchall()
        
        # Get completed tournaments
        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, 
                   t.end_date, t.prize_pool, COUNT(r.reg_id) as team_count
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            LEFT JOIN registrations r ON t.tournament_id = r.tournament_id
            WHERE t.status = 'completed'
            GROUP BY t.tournament_id, t.name, g.title, t.start_date, t.end_date, t.prize_pool
            ORDER BY t.start_date DESC
        """)
        completed = cursor.fetchall()
        
        cursor.close()
        
        return render_template('tournaments.html',
                             upcoming=upcoming,
                             ongoing=ongoing,
                             completed=completed)
    except Exception as e:
        flash(f'Error loading tournaments: {str(e)}', 'danger')
        return render_template('tournaments.html', upcoming=[], ongoing=[], completed=[])


# ============================================================================
# ROUTE: VIEW ALL MATCHES
# ============================================================================

@app.route('/matches')
def view_matches():
    """
    Display all matches with filters.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Get recent completed matches
        cursor.execute("""
            SELECT m.match_id, t.name as tournament, g.title as game,
                   t1.team_name as team1, t2.team_name as team2,
                   tw.team_name as winner, m.match_time,
                   s1.score as team1_score, s2.score as team2_score
            FROM matches m
            INNER JOIN tournaments t ON m.tournament_id = t.tournament_id
            INNER JOIN games g ON t.game_id = g.game_id
            INNER JOIN teams t1 ON m.team1_id = t1.team_id
            INNER JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN teams tw ON m.winner_id = tw.team_id
            LEFT JOIN scores s1 ON m.match_id = s1.match_id AND s1.team_id = t1.team_id
            LEFT JOIN scores s2 ON m.match_id = s2.match_id AND s2.team_id = t2.team_id
            WHERE m.status = 'completed'
            ORDER BY m.match_time DESC
            LIMIT 20
        """)
        completed_matches = cursor.fetchall()
        
        # Get upcoming scheduled matches
        cursor.execute("""
            SELECT m.match_id, t.name as tournament, g.title as game,
                   t1.team_name as team1, t2.team_name as team2,
                   m.match_time, m.round_number
            FROM matches m
            INNER JOIN tournaments t ON m.tournament_id = t.tournament_id
            INNER JOIN games g ON t.game_id = g.game_id
            INNER JOIN teams t1 ON m.team1_id = t1.team_id
            INNER JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE m.status = 'scheduled' AND m.match_time > NOW()
            ORDER BY m.match_time ASC
            LIMIT 20
        """)
        scheduled_matches = cursor.fetchall()
        
        cursor.close()
        
        return render_template('matches.html',
                             completed=completed_matches,
                             scheduled=scheduled_matches)
    except Exception as e:
        flash(f'Error loading matches: {str(e)}', 'danger')
        return render_template('matches.html', completed=[], scheduled=[])


# ============================================================================
# API ROUTES (JSON Responses for AJAX/External Apps)
# ============================================================================

@app.route('/api/top_teams')
def api_top_teams():
    """
    API endpoint to get top 5 teams by average score.
    Returns JSON data.
    
    Complex Query: Top 5 teams by average score
    """
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
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
            LIMIT 5
        """)
        
        teams = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': teams
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tournament/<int:tournament_id>/leaderboard')
def api_tournament_leaderboard(tournament_id):
    """
    API endpoint to get tournament leaderboard.
    Returns JSON data.
    """
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT team_id, team_name, matches_played, wins, losses, draws,
                   total_score, avg_score, win_rate_percentage
            FROM tournament_leaderboard
            WHERE tournament_id = %s
            ORDER BY wins DESC, avg_score DESC
        """, (tournament_id,))
        
        leaderboard = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'tournament_id': tournament_id,
            'data': leaderboard
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500


# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Run the Flask development server.
    
    Production Deployment Notes:
    - Change secret_key to a secure random value
    - Use environment variables for database credentials
    - Implement proper password hashing (bcrypt)
    - Enable HTTPS
    - Use a production WSGI server (gunicorn, uWSGI)
    - Set debug=False
    """
    # Respect FLASK_DEBUG and PORT from environment
    port = int(os.getenv('PORT', 5000))
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=port)
