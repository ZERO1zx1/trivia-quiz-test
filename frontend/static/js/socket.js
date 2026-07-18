// Initialize WebSocket connection
const socket = io();

// Connection event
socket.on('connect', () => {
    console.log('Successfully connected to TriviaVerse real-time server.');
});

function joinRoom() {
    const roomCode = document.querySelector('input').value;
    if(roomCode.length === 6) {
        // Trigger server-side event
        socket.emit('join_game', { room_code: roomCode, user_id: 1 /* Replace with actual auth ID */ });
    }
}

// Listen for instant updates
socket.on('player_joined', (data) => {
    console.log(data.message);
    // Here you would trigger a UI toast notification or update lobby state
});

socket.on('update_leaderboard', (data) => {
    // Dynamically animate leaderboard update
    const board = document.getElementById('live-leaderboard');
    // Implementation for dynamic sorting and D3/Anime.js animation would go here
});