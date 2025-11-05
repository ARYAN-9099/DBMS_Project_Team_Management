from flask import Blueprint, jsonify
from ..extensions import mysql

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/top_teams')
def api_top_teams():
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

        return jsonify({'success': True, 'data': teams})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/tournament/<int:tournament_id>/leaderboard')
def api_tournament_leaderboard(tournament_id):
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
        return jsonify({'success': False, 'error': str(e)}), 500
