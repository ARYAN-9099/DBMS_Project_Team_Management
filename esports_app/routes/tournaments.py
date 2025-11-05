from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import mysql
from ..decorators import login_required

tournaments_bp = Blueprint('tournaments', __name__)


@tournaments_bp.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            game_id = request.form.get('game_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            prize_pool = request.form.get('prize_pool', 0)

            if not all([name, game_id, start_date, end_date]):
                flash('All required fields must be filled!', 'danger')
                return redirect(url_for('tournaments.create_tournament'))

            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            if end < start:
                flash('End date must be after start date!', 'danger')
                return redirect(url_for('tournaments.create_tournament'))

            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO tournaments (name, game_id, start_date, end_date, prize_pool)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, game_id, start_date, end_date, prize_pool))

            mysql.connection.commit()
            tournament_id = cursor.lastrowid
            cursor.close()

            flash(f'Tournament "{name}" created successfully! Tournament ID: {tournament_id}', 'success')
            return redirect(url_for('tournaments.view_tournaments'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating tournament: {str(e)}', 'danger')
            return redirect(url_for('tournaments.create_tournament'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT game_id, title, genre FROM games ORDER BY title")
        games = cursor.fetchall()
        cursor.close()

        return render_template('create_tournament.html', games=games)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'danger')
        return render_template('create_tournament.html', games=[])


@tournaments_bp.route('/register_team', methods=['GET', 'POST'])
@login_required
def register_team():
    if request.method == 'POST':
        try:
            team_id = request.form.get('team_id')
            tournament_id = request.form.get('tournament_id')

            if not all([team_id, tournament_id]):
                flash('Team and tournament must be selected!', 'danger')
                return redirect(url_for('tournaments.register_team'))

            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO registrations (team_id, tournament_id)
                VALUES (%s, %s)
            """, (team_id, tournament_id))

            mysql.connection.commit()
            reg_id = cursor.lastrowid
            cursor.close()

            flash(f'Team registered for tournament successfully! Registration ID: {reg_id}', 'success')
            return redirect(url_for('tournaments.view_tournaments'))

        except Exception as e:
            mysql.connection.rollback()
            error_msg = str(e)

            if 'already registered' in error_msg.lower():
                flash('This team is already registered for this tournament!', 'warning')
            else:
                flash(f'Error registering team: {error_msg}', 'danger')

            return redirect(url_for('tournaments.register_team'))

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


@tournaments_bp.route('/leaderboard/<int:tournament_id>')
def leaderboard(tournament_id):
    try:
        cursor = mysql.connection.cursor()

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
            return redirect(url_for('tournaments.view_tournaments'))

        cursor.execute("""
            SELECT team_id, team_name, matches_played, wins, losses, draws,
                   total_score, avg_score, win_rate_percentage
            FROM tournament_leaderboard
            WHERE tournament_id = %s
            ORDER BY wins DESC, avg_score DESC, total_score DESC
        """, (tournament_id,))
        leaderboard_data = cursor.fetchall()

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

        return render_template(
            'leaderboard.html',
            tournament=tournament,
            leaderboard=leaderboard_data,
            recent_matches=recent_matches,
            tournament_id=tournament_id
        )
    except Exception as e:
        flash(f'Error loading leaderboard: {str(e)}', 'danger')
        return redirect(url_for('tournaments.view_tournaments'))


@tournaments_bp.route('/tournaments')
def view_tournaments():
    try:
        cursor = mysql.connection.cursor()

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

        return render_template(
            'tournaments.html',
            upcoming=upcoming,
            ongoing=ongoing,
            completed=completed
        )
    except Exception as e:
        flash(f'Error loading tournaments: {str(e)}', 'danger')
        return render_template('tournaments.html', upcoming=[], ongoing=[], completed=[])
