from backend.extensions import socketio, db
from flask_socketio import emit, join_room, leave_room
from backend.models import User, Room

@socketio.on('join_game')
def handle_join(data):
    room_code = data.get('room_code')
    user_id = data.get('user_id')
    
    join_room(room_code)
    
    # Broadcast to everyone else in the room
    emit('player_joined', {'user_id': user_id, 'message': 'A new challenger has appeared!'}, to=room_code)

@socketio.on('submit_answer')
def handle_answer(data):
    room_code = data.get('room_code')
    is_correct = data.get('is_correct')
    
    # Calculate score logic here...
    points_awarded = 100 if is_correct else 0
    
    # Instantly sync leaderboard
    emit('update_leaderboard', {'user_id': data['user_id'], 'score': points_awarded}, to=room_code)