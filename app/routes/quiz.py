"""Quiz Routes"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.question import Category, Question, Answer
from app.models.room import Room, RoomPlayer

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/categories')
def categories():
    cats = Category.query.filter_by(is_active=True).all()
    return jsonify([c.to_dict() for c in cats])

@quiz_bp.route('/questions')
def get_questions():
    category_id = request.args.get('category_id', type=int)
    difficulty = request.args.get('difficulty', 'mixed')
    limit = request.args.get('limit', 10, type=int)
    query = Question.query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if difficulty != 'mixed':
        query = query.filter_by(difficulty=difficulty)
    questions = query.order_by(db.func.random()).limit(limit).all()
    return jsonify([q.to_dict() for q in questions])

@quiz_bp.route('/play/<room_code>')
@login_required
def play(room_code):
    room = Room.query.filter_by(code=room_code).first_or_404()
    player = RoomPlayer.query.filter_by(room_id=room.id, user_id=current_user.id).first()
    if not player:
        from flask import flash, redirect, url_for
        flash('You are not in this room.', 'danger')
        return redirect(url_for('rooms.lobby'))
    return render_template('quiz/play.html', room=room)
