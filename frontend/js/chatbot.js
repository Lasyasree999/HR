/**
 * HireGenius AI — HR Copilot Chatbot Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('chatbot', 'HR Copilot', 'AI Intelligence / Chatbot');
    setupChat();
});

function setupChat() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });
    sendBtn.addEventListener('click', sendMessage);

    // Setup suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.textContent;
            sendMessage();
        });
    });

    addBotMessage("Hello! I'm your AI recruitment assistant. I can help you search candidates, answer policy questions, and provide recruitment insights. What would you like to know?");
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addUserMessage(message);
    input.value = '';
    showTyping();

    try {
        const response = await API.post('/chat/message', { message });
        hideTyping();
        addBotMessage(response.response);

        if (response.suggestions && response.suggestions.length) {
            updateSuggestions(response.suggestions);
        }
    } catch (e) {
        hideTyping();
        addBotMessage("I'm sorry, I encountered an error. Please try again.");
    }
}

function addUserMessage(text) {
    const container = document.getElementById('chatMessages');
    container.innerHTML += `
        <div class="chat-message user">
            <div class="message-avatar"><i class="bi bi-person-fill"></i></div>
            <div class="message-bubble">${escapeHtml(text)}</div>
        </div>`;
    container.scrollTop = container.scrollHeight;
}

function addBotMessage(text) {
    const container = document.getElementById('chatMessages');
    container.innerHTML += `
        <div class="chat-message bot">
            <div class="message-avatar">🧠</div>
            <div class="message-bubble">${formatBotMessage(text)}</div>
        </div>`;
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const container = document.getElementById('chatMessages');
    container.innerHTML += `<div class="chat-message bot" id="typingIndicator"><div class="message-avatar">🧠</div>
        <div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

function updateSuggestions(suggestions) {
    const container = document.getElementById('chatSuggestions');
    container.innerHTML = suggestions.map(s => `<button class="suggestion-chip" onclick="document.getElementById('chatInput').value='${s}';sendMessage();">${s}</button>`).join('');
}

function formatBotMessage(text) {
    return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
