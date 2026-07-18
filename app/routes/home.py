"""Home Routes"""
from flask import Blueprint, render_template, jsonify
from app.models.question import Category
from app.models.room import Room
from app.extensions import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    categories = Category.query.filter_by(is_active=True).all()
    public_rooms = Room.query.filter_by(is_private=False, status='waiting').limit(10).all()
    return render_template('home/index.html', categories=categories, public_rooms=public_rooms)

@home_bp.route('/about')
def about():
    return render_template('home/about.html')

@home_bp.route('/api/stats')
def api_stats():
    from app.models.user import User
    from app.models.question import Question
    stats = {
        'total_players': User.query.count(),
        'total_questions': Question.query.filter_by(is_active=True).count(),
        'total_categories': Category.query.filter_by(is_active=True).count(),
        'active_rooms': Room.query.filter_by(status='waiting').count()
    }
    return jsonify(stats)
