const chatBox = document.getElementById('chat-box');
const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
let conversation = [];

function addMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  if (role === 'assistant') {
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = 'A';
    wrapper.appendChild(avatar);
  }

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  wrapper.appendChild(bubble);

  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addTypingIndicator() {
  const wrapper = document.createElement('div');
  wrapper.className = 'message assistant typing';

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = 'A';
  wrapper.appendChild(avatar);

  const bubble = document.createElement('div');
  bubble.className = 'bubble typing-bubble';
  bubble.textContent = 'Pensando...';
  wrapper.appendChild(bubble);

  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
  return wrapper;
}

function removeTypingIndicator(node) {
  if (node && node.parentNode) {
    node.parentNode.removeChild(node);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage('user', message);
  conversation.push(['user', message]);
  input.value = '';
  input.style.height = 'auto';

  const typingNode = addTypingIndicator();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        history: conversation.slice(0, -1).map(([, text]) => text)
      })
    });

    const data = await response.json();
    removeTypingIndicator(typingNode);
    const reply = data.reply || 'No pude responder ahora mismo.';
    addMessage('assistant', reply);
    conversation.push(['assistant', reply]);
  } catch (error) {
    removeTypingIndicator(typingNode);
    addMessage('assistant', 'Ha ocurrido un error. Inténtalo de nuevo en un momento.');
  }
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
});
