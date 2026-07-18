"""Dashboard Routes"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from app.extensions import db
from app.models.room import Room, RoomPlayer
from app.models.question import Category
from app.models.economy import Transaction, LeaderboardEntry
from app.models.achievement import UserAchievement

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    recent_matches = current_user.scores.order_by(db.desc('id')).limit(5).all()
    friends = current_user.get_friends()
    online_friends = [f for f in friends if f.is_online]
    notifications = current_user.notifications.limit(10).all()
    top_players = LeaderboardEntry.query.filter_by(period='alltime').order_by(
        LeaderboardEntry.score.desc()).limit(5).all()
    categories = Category.query.filter_by(is_active=True).all()
    active_rooms = Room.query.filter_by(status='waiting').limit(8).all()
    transactions = current_user.transactions.order_by(db.desc('id')).limit(5).all()
    achievements = UserAchievement.query.filter_by(
        user_id=current_user.id, is_unlocked=True).order_by(db.desc('unlocked_at')).limit(6).all()

    return render_template('dashboard/index.html',
                         recent_matches=recent_matches,
                         online_friends=online_friends,
                         notifications=notifications,
                         top_players=top_players,
                         categories=categories,
                         active_rooms=active_rooms,
                         transactions=transactions,
                         achievements=achievements)

@dashboard_bp.route('/api/stats')
@login_required
def api_user_stats():
    stats = {
        'username': current_user.username,
        'display_name': current_user.display_name,
        'level': current_user.level,
        'xp': current_user.xp,
        'coins': current_user.coins,
        'wins': current_user.wins,
        'losses': current_user.losses,
        'games_played': current_user.games_played,
        'accuracy': round(current_user.accuracy, 1),
        'avatar': current_user.avatar_url,
        'is_online': current_user.is_online
    }
    return jsonify(stats)

@dashboard_bp.route('/daily-reward', methods=['POST'])
@login_required
def daily_reward():
    if current_user.last_daily_reward:
        time_since = datetime.utcnow() - current_user.last_daily_reward
        if time_since < timedelta(hours=20):
            hours_left = 20 - (time_since.total_seconds() / 3600)
            return jsonify({'success': False, 'message': f'Come back in {int(hours_left)}h!'})

    from flask import current_app
    reward = current_app.config['DAILY_REWARD_COINS']
    current_user.add_coins(reward, 'Daily Reward')
    current_user.last_daily_reward = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'reward': reward, 'new_balance': current_user.coins})
