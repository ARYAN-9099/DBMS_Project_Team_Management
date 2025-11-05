def register_blueprints(app):
    from .main import main_bp
    from .auth import auth_bp
    from .teams import teams_bp
    from .tournaments import tournaments_bp
    from .matches import matches_bp
    from .api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(tournaments_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(api_bp)
