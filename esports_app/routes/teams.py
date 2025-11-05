from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..extensions import mysql
from ..decorators import login_required

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        try:
            team_name = request.form.get('team_name')

            if not team_name:
                flash('Team name is required!', 'danger')
                return redirect(url_for('teams.create_team'))

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT team_id FROM teams WHERE team_name = %s", (team_name,))
            existing_team = cursor.fetchone()

            if existing_team:
                flash('Team name already exists!', 'warning')
                cursor.close()
                return redirect(url_for('teams.create_team'))

            captain_id = session['user_id']
            cursor.execute("""
                INSERT INTO teams (team_name, captain_id)
                VALUES (%s, %s)
            """, (team_name, captain_id))

            mysql.connection.commit()
            team_id = cursor.lastrowid
            cursor.close()

            flash(f'Team "{team_name}" created successfully! Team ID: {team_id}', 'success')
            return redirect(url_for('teams.view_teams'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating team: {str(e)}', 'danger')
            return redirect(url_for('teams.create_team'))

    return render_template('create_team.html')


@teams_bp.route('/add_player', methods=['GET', 'POST'])
@login_required
def add_player():
    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id')
            team_id = request.form.get('team_id')
            game_tag = request.form.get('game_tag')

            if not all([user_id, team_id, game_tag]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('teams.add_player'))

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                flash('User not found!', 'danger')
                cursor.close()
                return redirect(url_for('teams.add_player'))

            cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (team_id,))
            team = cursor.fetchone()

            if not team:
                flash('Team not found!', 'danger')
                cursor.close()
                return redirect(url_for('teams.add_player'))

            cursor.execute("""
                SELECT player_id FROM players 
                WHERE user_id = %s AND team_id = %s
            """, (user_id, team_id))
            existing = cursor.fetchone()

            if existing:
                flash('Player already in this team!', 'warning')
                cursor.close()
                return redirect(url_for('teams.add_player'))

            cursor.execute("""
                INSERT INTO players (user_id, team_id, game_tag)
                VALUES (%s, %s, %s)
            """, (user_id, team_id, game_tag))

            mysql.connection.commit()
            player_id = cursor.lastrowid
            cursor.close()

            flash(f'Player added to team successfully! Player ID: {player_id}', 'success')
            return redirect(url_for('teams.view_teams'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error adding player: {str(e)}', 'danger')
            return redirect(url_for('teams.add_player'))

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


@teams_bp.route('/teams')
def view_teams():
    try:
        cursor = mysql.connection.cursor()
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


@teams_bp.route('/team/<int:team_id>')
def team_details(team_id):
    try:
        cursor = mysql.connection.cursor()

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
            return redirect(url_for('teams.view_teams'))

        cursor.execute("""
            SELECT p.player_id, u.name, u.email, p.game_tag, p.joined_at
            FROM players p
            INNER JOIN users u ON p.user_id = u.user_id
            WHERE p.team_id = %s
            ORDER BY p.joined_at
        """, (team_id,))
        roster = cursor.fetchall()

        cursor.callproc('get_team_statistics', [team_id])
        stats = cursor.fetchone()

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

        return render_template(
            'team_details.html',
            team=team,
            roster=roster,
            stats=stats,
            tournaments=tournaments
        )
    except Exception as e:
        flash(f'Error loading team details: {str(e)}', 'danger')
        return redirect(url_for('teams.view_teams'))
