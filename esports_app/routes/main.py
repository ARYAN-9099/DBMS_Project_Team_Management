from flask import Blueprint, render_template, flash
from ..extensions import mysql

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date, t.prize_pool
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            WHERE t.status = 'upcoming'
            ORDER BY t.start_date ASC
            LIMIT 5
        """)
        upcoming_tournaments = cursor.fetchall()

        cursor.execute("""
            SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date, t.prize_pool
            FROM tournaments t
            INNER JOIN games g ON t.game_id = g.game_id
            WHERE t.status = 'ongoing'
            ORDER BY t.start_date ASC
        """)
        ongoing_tournaments = cursor.fetchall()

        cursor.execute("""
            SELECT team_id, team_name, total_wins, avg_score_all_time, overall_win_rate
            FROM team_performance_summary
            ORDER BY total_wins DESC, avg_score_all_time DESC
            LIMIT 5
        """)
        top_teams = cursor.fetchall()

        cursor.close()

        return render_template(
            'index.html',
            upcoming=upcoming_tournaments,
            ongoing=ongoing_tournaments,
            top_teams=top_teams
        )
    except Exception as e:
        flash(f'Error loading home page: {str(e)}', 'danger')
        return render_template('index.html', upcoming=[], ongoing=[], top_teams=[])
