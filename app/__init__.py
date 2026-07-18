"""TriviaVerse Application Factory"""
from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config[config_name])

    from app.extensions import db, migrate, login_manager, socketio, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app, async_mode=app.config['SOCKETIO_ASYNC_MODE'],
                     cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'])
    csrf.init_app(app)

    from app.routes.home import home_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.rooms import rooms_bp
    from app.routes.quiz import quiz_bp
    from app.routes.leaderboard import leaderboard_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(rooms_bp, url_prefix='/rooms')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(leaderboard_bp, url_prefix='/leaderboard')

    from app.sockets.room_socket import register_room_events
    from app.sockets.game_socket import register_game_events
    register_room_events(socketio)
    register_game_events(socketio)

    with app.app_context():
        db.create_all()
        _seed_categories()
        _seed_achievements()

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, url_for, flash
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('auth.login'))

    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        return {
            'app_name': 'TriviaVerse',
            'current_year': 2026,
            'current_user': current_user
        }

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

def _seed_categories():
    from app.models.question import Category
    if Category.query.first():
        return
    categories = [
        ('General Knowledge', 'general', 'Brain', '#5865F2'),
        ('Science', 'science', 'Atom', '#00D4FF'),
        ('Programming', 'programming', 'Code', '#8B5CF6'),
        ('Technology', 'technology', 'Cpu', '#EC4899'),
        ('History', 'history', 'Landmark', '#FACC15'),
        ('Movies', 'movies', 'Film', '#EF4444'),
        ('Anime', 'anime', 'Sparkles', '#22C55E'),
        ('Music', 'music', 'Music', '#7289DA'),
        ('Gaming', 'gaming', 'Gamepad2', '#5865F2'),
        ('Sports', 'sports', 'Trophy', '#00D4FF'),
    ]
    for name, slug, icon, color in categories:
        db.session.add(Category(name=name, slug=slug, icon=icon, color=color))
    db.session.commit()

def _seed_achievements():
    from app.models.achievement import Achievement
    if Achievement.query.first():
        return
    achievements = [
        ('First Blood', 'Win your first match', 'sword', 'wins', 'wins_count', 1, 50, 100, 'common'),
        ('Rising Star', 'Win 10 matches', 'star', 'wins', 'wins_count', 10, 200, 500, 'common'),
        ('Champion', 'Win 50 matches', 'crown', 'wins', 'wins_count', 50, 500, 2000, 'rare'),
        ('Legend', 'Win 100 matches', 'trophy', 'wins', 'wins_count', 100, 1000, 5000, 'epic'),
        ('Trivia Master', 'Play 500 games', 'brain', 'games', 'games_count', 500, 2000, 10000, 'legendary'),
        ('Sharpshooter', 'Maintain 80% accuracy', 'target', 'accuracy', 'accuracy_rate', 80, 300, 1000, 'rare'),
        ('Speed Demon', 'Answer correctly in under 2 seconds', 'zap', 'special', 'fast_answer', 1, 100, 200, 'epic'),
        ('Perfectionist', 'Get a perfect game', 'check-circle', 'special', 'perfect_game', 1, 500, 1000, 'legendary'),
    ]
    for name, desc, icon, cat, req_type, req_val, xp, coins, rarity in achievements:
        db.session.add(Achievement(
            name=name, description=desc, icon=icon, category=cat,
            requirement_type=req_type, requirement_value=req_val,
            xp_reward=xp, coin_reward=coins, rarity=rarity
        ))
    db.session.commit()
