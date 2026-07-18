import os
from dotenv import load_dotenv
from flask import Flask
from backend.extensions import db, socketio, login_manager
from backend.models import User  # User моделийг дээр нь импортлоорой

load_dotenv()

def create_app():
    app = Flask(__name__, 
                static_folder='frontend/static', 
                template_folder='frontend/templates')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    # ─── ҮҮНИЙГ НЭМЖ ӨГӨӨРЭЙ ─────────────────────────────────
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    # ────────────────────────────────────────────────────────

    # Жишээ route (Үндсэн нүүр хуудас)
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('dashboard.html')

    return app

if __name__ == '__main__':
    app = create_app()
    print("TriviaVerse Web & WebSocket Server running on http://127.0.0.1:5000")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)