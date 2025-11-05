from flask import Blueprint, render_template, flash, send_from_directory
from ..extensions import mysql
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    upcoming_tournaments = []
    ongoing_tournaments = []
    top_teams = []
    
    try:
        cursor = mysql.connection.cursor()

        # Get upcoming tournaments
        try:
            cursor.execute("""
                SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date, t.prize_pool
                FROM tournaments t
                INNER JOIN games g ON t.game_id = g.game_id
                WHERE t.status = 'upcoming'
                ORDER BY t.start_date ASC
                LIMIT 5
            """)
            upcoming_tournaments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching upcoming tournaments: {e}")

        # Get ongoing tournaments
        try:
            cursor.execute("""
                SELECT t.tournament_id, t.name, g.title as game, t.start_date, t.end_date, t.prize_pool
                FROM tournaments t
                INNER JOIN games g ON t.game_id = g.game_id
                WHERE t.status = 'ongoing'
                ORDER BY t.start_date ASC
            """)
            ongoing_tournaments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching ongoing tournaments: {e}")

        # Get top teams - try view first, fallback to basic query
        try:
            cursor.execute("""
                SELECT team_id, team_name, total_wins, avg_score_all_time, overall_win_rate
                FROM team_performance_summary
                ORDER BY total_wins DESC, avg_score_all_time DESC
                LIMIT 5
            """)
            top_teams = cursor.fetchall()
        except Exception as e:
            print(f"View not available, using basic query: {e}")
            try:
                cursor.execute("""
                    SELECT t.team_id, t.team_name, 
                           COUNT(m.winner_id) as total_wins,
                           0 as avg_score_all_time,
                           0 as overall_win_rate
                    FROM teams t
                    LEFT JOIN matches m ON t.team_id = m.winner_id
                    GROUP BY t.team_id, t.team_name
                    ORDER BY total_wins DESC
                    LIMIT 5
                """)
                top_teams = cursor.fetchall()
            except Exception as e2:
                print(f"Error in fallback query: {e2}")

        cursor.close()

    except Exception as e:
        error_msg = str(e)
        print(f'Database connection error: {error_msg}')
        
        # Provide helpful error messages
        if "Can't connect" in error_msg or "2002" in error_msg or "10061" in error_msg:
            flash('⚠️ MySQL Server is not running. Please start MySQL/XAMPP and try again.', 'danger')
        elif "Access denied" in error_msg:
            flash('⚠️ Database authentication failed. Please check your .env file credentials.', 'danger')
        elif "Unknown database" in error_msg:
            flash('⚠️ Database not found. Please run the esports_db.sql script to create the database.', 'danger')
        else:
            flash(f'⚠️ Database error: {error_msg}', 'danger')
    
    return render_template(
        'index.html',
        upcoming=upcoming_tournaments,
        ongoing=ongoing_tournaments,
        top_teams=top_teams
    )


@main_bp.route('/er-diagram')
def er_diagram():
    """Serve the ER diagram HTML file"""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'er_diagram.html')
