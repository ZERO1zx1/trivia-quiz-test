// Socket.IO Client
let socket = null;
let currentRoom = null;

function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to TriviaVerse');
    });

    socket.on('error', (data) => {
        showToast(data.message, 'danger');
    });

    socket.on('player_joined', (data) => {
        updatePlayerList(data.players);
        showToast(`${data.player.username} joined the room`);
    });

    socket.on('player_left', (data) => {
        updatePlayerList(data.players);
    });

    socket.on('player_ready_changed', (data) => {
        updatePlayerList(data.players);
        const btn = document.getElementById('readyBtn');
        if (btn && data.user_id === window.currentUserId) {
            btn.textContent = data.is_ready ? 'Not Ready' : 'Ready';
            btn.classList.toggle('btn-success', data.is_ready);
        }
    });

    socket.on('chat_message', (data) => {
        addChatMessage(data);
    });

    socket.on('game_started', (data) => {
        window.location.href = `/quiz/play/${currentRoom}`;
    });

    socket.on('kicked_from_room', () => {
        showToast('You were kicked from the room', 'danger');
        setTimeout(() => window.location.href = '/rooms', 1500);
    });
}

function joinRoomSocket(roomCode) {
    currentRoom = roomCode;
    socket.emit('join_room', { room_code: roomCode });
}

function toggleReady(roomCode) {
    socket.emit('toggle_ready', { room_code: roomCode });
}

function sendChat(roomCode, message) {
    socket.emit('send_chat', { room_code: roomCode, message });
}

function startGame(roomCode) {
    socket.emit('start_game', { room_code: roomCode });
}

function updatePlayerList(players) {
    const container = document.getElementById('playerList');
    if (!container) return;

    container.innerHTML = players.map(p => `
        <div class="player-card ${p.is_ready ? 'ready' : ''} ${p.user_id === window.hostId ? 'host' : ''}">
            ${p.user_id === window.hostId ? '<span class="host-badge">HOST</span>' : ''}
            <img src="${p.avatar}" alt="${p.username}">
            <div class="player-name">${p.username}</div>
            <div class="ready-indicator ${p.is_ready ? 'ready' : ''}"></div>
        </div>
    `).join('');
}

function addChatMessage(data) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    const isSelf = data.user_id === window.currentUserId;
    const div = document.createElement('div');
    div.className = `chat-message ${isSelf ? 'chat-message-self' : ''}`;
    div.innerHTML = `
        <img src="${data.avatar}" alt="${data.username}">
        <div class="chat-message-content">
            <div class="chat-message-username">${data.username}</div>
            <div>${escapeHtml(data.message)}</div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

if (document.querySelector('.app-layout')) {
    initSocket();
}
