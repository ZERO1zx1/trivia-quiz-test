// Quiz Game Logic
let gameState = { currentQuestion: 0, totalQuestions: 0, timeLeft: 20, timerInterval: null, answers: {}, score: 0 };

function initQuiz(roomCode) {
    window.roomCode = roomCode;

    socket.on('question', (data) => { renderQuestion(data); startTimer(data.time_limit || 20); });
    socket.on('answer_result', (data) => { showAnswerResult(data); });
    socket.on('round_results', (data) => { showRoundResults(data); });
    socket.on('next_question_ready', () => { socket.emit('request_question', { room_code: roomCode }); });
    socket.on('game_over', (data) => { showGameOver(data); });

    socket.emit('request_question', { room_code: roomCode });
}

function renderQuestion(data) {
    gameState.currentQuestion = data.question_number;
    gameState.totalQuestions = data.total_questions;
    gameState.timeLeft = data.time_limit;

    const container = document.getElementById('quizContainer');
    container.innerHTML = `
        <div class="question-card" id="questionCard">
            <div class="question-number">Question ${data.question_number} of ${data.total_questions}</div>
            <h2 class="question-text">${escapeHtml(data.question_text)}</h2>
            ${data.image_url ? `<img src="${data.image_url}" style="max-width:100%;border-radius:12px;margin-bottom:20px;">` : ''}
            <div class="timer-container">
                <svg class="timer-svg" width="120" height="120" viewBox="0 0 120 120">
                    <circle class="timer-bg" cx="60" cy="60" r="54"/>
                    <circle class="timer-progress" id="timerCircle" cx="60" cy="60" r="54" stroke-dasharray="339.292" stroke-dashoffset="0"/>
                </svg>
                <div class="timer-text" id="timerText">${data.time_limit}</div>
            </div>
            <div class="answers-grid" id="answersGrid">
                ${data.answers.map(a => `
                    <button class="answer-btn" onclick="submitAnswer(${a.id})" data-id="${a.id}">
                        ${escapeHtml(a.answer_text)}
                    </button>
                `).join('')}
            </div>
        </div>
    `;

    const circle = document.getElementById('timerCircle');
    const circumference = 2 * Math.PI * 54;
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
}

function startTimer(seconds) {
    gameState.timeLeft = seconds;
    const circle = document.getElementById('timerCircle');
    const text = document.getElementById('timerText');
    const circumference = 2 * Math.PI * 54;

    if (gameState.timerInterval) clearInterval(gameState.timerInterval);

    const startTime = Date.now();
    const endTime = startTime + (seconds * 1000);

    gameState.timerInterval = setInterval(() => {
        const now = Date.now();
        const remaining = Math.max(0, endTime - now);
        const elapsed = seconds - (remaining / 1000);
        gameState.timeLeft = remaining / 1000;

        const offset = circumference - (elapsed / seconds) * circumference;
        circle.style.strokeDashoffset = offset;
        text.textContent = Math.ceil(gameState.timeLeft);

        if (gameState.timeLeft <= 5) circle.style.stroke = '#EF4444';
        else if (gameState.timeLeft <= 10) circle.style.stroke = '#FACC15';

        if (remaining <= 0) {
            clearInterval(gameState.timerInterval);
            submitAnswer(null);
        }
    }, 100);
}

function submitAnswer(answerId) {
    clearInterval(gameState.timerInterval);

    const buttons = document.querySelectorAll('.answer-btn');
    buttons.forEach(btn => {
        btn.disabled = true;
        if (parseInt(btn.dataset.id) === answerId) btn.classList.add('selected');
    });

    const timeTaken = document.getElementById('timerText').textContent;
    socket.emit('submit_answer', { room_code: window.roomCode, answer_id: answerId, time_taken: parseInt(timeTaken) });
}

function showAnswerResult(data) {
    const buttons = document.querySelectorAll('.answer-btn');
    buttons.forEach(btn => {
        const btnId = parseInt(btn.dataset.id);
        if (btnId === data.correct_answer_id) btn.classList.add('correct');
        else if (btn.classList.contains('selected') && !data.correct) btn.classList.add('wrong');
    });

    gameState.score = data.total_score;

    const popup = document.createElement('div');
    popup.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--glass);padding:32px 48px;border-radius:24px;border:1px solid var(--border);text-align:center;z-index:100;animation:scaleIn 0.3s ease;';
    popup.innerHTML = `
        <div style="font-size:3rem;margin-bottom:8px;">${data.correct ? '✅' : '❌'}</div>
        <div style="font-size:1.5rem;font-weight:800;">${data.correct ? 'Correct!' : 'Wrong!'}</div>
        <div style="color:var(--text-secondary);margin-top:8px;">+${data.score_earned} points</div>
        <div style="margin-top:16px;font-size:0.9rem;">Streak: ${data.streak} 🔥</div>
    `;
    document.body.appendChild(popup);

    setTimeout(() => { popup.style.opacity = '0'; setTimeout(() => popup.remove(), 300); }, 2000);
}

function showRoundResults(data) {
    const container = document.getElementById('quizContainer');
    container.innerHTML = `
        <div class="question-card">
            <h2 style="margin-bottom:24px;">Round Results</h2>
            <div style="display:flex;flex-direction:column;gap:12px;">
                ${data.leaderboard.map((p, i) => `
                    <div style="display:flex;align-items:center;gap:16px;padding:16px;background:var(--surface);border-radius:12px;border:${i === 0 ? '2px solid var(--warning)' : '1px solid var(--border)'};">
                        <div style="font-size:1.5rem;font-weight:800;width:40px;">#${i+1}</div>
                        <img src="${p.avatar}" style="width:40px;height:40px;border-radius:50%;">
                        <div style="flex:1;">
                            <div style="font-weight:700;">${escapeHtml(p.username)}</div>
                            <div style="font-size:0.85rem;color:var(--text-secondary);">Streak: ${p.streak}</div>
                        </div>
                        <div style="font-size:1.3rem;font-weight:800;color:var(--accent);">${p.score}</div>
                    </div>
                `).join('')}
            </div>
            <button class="btn btn-primary btn-full" style="margin-top:24px;" onclick="nextQuestion()">Next Question →</button>
        </div>
    `;
}

function nextQuestion() {
    socket.emit('next_question', { room_code: window.roomCode });
}

function showGameOver(data) {
    const container = document.getElementById('quizContainer');

    container.innerHTML = `
        <div class="question-card" style="text-align:center;">
            <h1 style="font-size:3rem;margin-bottom:8px;">🏆</h1>
            <h2 style="margin-bottom:32px;">Game Over!</h2>

            <div class="podium" style="margin:32px 0;">
                ${data.results.slice(0, 3).map((p, i) => `
                    <div class="podium-place podium-${i+1}">
                        <img src="${p.avatar}" class="podium-avatar" alt="${p.username}">
                        <div class="podium-block">${i+1}</div>
                        <div class="podium-info">
                            <div class="podium-name">${escapeHtml(p.username)}</div>
                            <div class="podium-score">${p.score} pts</div>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:32px;">
                ${data.results.map((p, i) => `
                    <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--surface);border-radius:12px;">
                        <span style="font-weight:800;width:30px;">#${i+1}</span>
                        <span style="flex:1;">${escapeHtml(p.username)}</span>
                        <span style="color:var(--accent);font-weight:700;">${p.score}</span>
                        <span style="font-size:0.85rem;color:var(--text-secondary);">${p.correct}/${data.total_questions}</span>
                    </div>
                `).join('')}
            </div>

            <a href="/rooms" class="btn btn-primary btn-lg">Back to Lobby</a>
        </div>
    `;

    createConfetti();
}

function createConfetti() {
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position:fixed;
            width:10px;height:10px;
            background:${['#FFD700', '#00D4FF', '#5865F2', '#EC4899', '#22C55E'][Math.floor(Math.random()*5)]};
            left:${Math.random()*100}%;
            top:-10px;
            border-radius:${Math.random()>0.5?'50%':'0'};
            animation:confettiFall ${3+Math.random()*4}s linear forwards;
            z-index:9999;
        `;
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), 7000);
    }
}

const style = document.createElement('style');
style.textContent = `
    @keyframes confettiFall {
        to { transform: translateY(100vh) rotate(720deg); opacity:0; }
    }
    @keyframes scaleIn {
        from { transform:translate(-50%,-50%) scale(0.8); opacity:0; }
        to { transform:translate(-50%,-50%) scale(1); opacity:1; }
    }
`;
document.head.appendChild(style);
