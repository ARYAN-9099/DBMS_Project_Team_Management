import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import mysql
from .routes import register_blueprints
from .errors import register_error_handlers


def create_app():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    load_dotenv(os.path.join(project_root, '.env'))

    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'esports_db')
    app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS', 'DictCursor')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    app.config['PORT'] = int(os.getenv('PORT', 5000))

    mysql.init_app(app)

    register_blueprints(app)

    legacy_endpoint_map = {
        'index': 'main.index',
        'register_user': 'auth.register_user',
        'login': 'auth.login',
        'logout': 'auth.logout',
        'create_team': 'teams.create_team',
        'add_player': 'teams.add_player',
        'view_teams': 'teams.view_teams',
        'team_details': 'teams.team_details',
        'create_tournament': 'tournaments.create_tournament',
        'register_team': 'tournaments.register_team',
        'leaderboard': 'tournaments.leaderboard',
        'view_tournaments': 'tournaments.view_tournaments',
        'record_match': 'matches.record_match',
        'view_matches': 'matches.view_matches',
        'api_top_teams': 'api.api_top_teams',
        'api_tournament_leaderboard': 'api.api_tournament_leaderboard',
    }
    for legacy_endpoint, new_endpoint in legacy_endpoint_map.items():
        view = app.view_functions.get(new_endpoint)
        if view:
            app.view_functions[legacy_endpoint] = view
            rules = app.url_map._rules_by_endpoint.get(new_endpoint, [])
            if rules:
                app.url_map._rules_by_endpoint[legacy_endpoint] = rules

    register_error_handlers(app)

    return app
