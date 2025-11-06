from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import mysql
from ..decorators import login_required
from MySQLdb import ProgrammingError

matches_bp = Blueprint('matches', __name__)


@matches_bp.route('/record_match', methods=['GET', 'POST'])
@login_required
def record_match():
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
                return redirect(url_for('matches.record_match'))

            if team1_id == team2_id:
                flash('Teams must be different!', 'danger')
                return redirect(url_for('matches.record_match'))

            match_datetime = datetime.strptime(match_time, '%Y-%m-%dT%H:%M')

            cursor = mysql.connection.cursor()
            cursor.callproc('record_match_result', [
                tournament_id,
                team1_id,
                team2_id,
                int(team1_score),
                int(team2_score),
                match_datetime,
                int(round_number)
            ])

            # Fetch the result from the stored procedure
            result = cursor.fetchone()
            
            # Consume all result sets to avoid "Commands out of sync" error
            cursor.nextset()
            
            mysql.connection.commit()
            cursor.close()

            if result and 'match_id' in result:
                flash(f'Match recorded successfully! Match ID: {result["match_id"]}', 'success')
            else:
                flash('Match recorded successfully!', 'success')

            return redirect(url_for('matches.view_matches'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error recording match: {str(e)}', 'danger')
            return redirect(url_for('matches.record_match'))

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


@matches_bp.route('/matches')
def view_matches():
    try:
        cursor = mysql.connection.cursor()

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

        return render_template(
            'matches.html',
            completed=completed_matches,
            scheduled=scheduled_matches
        )
    except Exception as e:
        flash(f'Error loading matches: {str(e)}', 'danger')
        return render_template('matches.html', completed=[], scheduled=[])
