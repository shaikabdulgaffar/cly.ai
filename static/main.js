class AIAssistant {
    constructor() {
        this.currentMode = 'chat';
        this.isFirstMessage = true;
        this.isDarkMode = localStorage.getItem('theme') === 'dark';
        this.conversation = []; // <-- Add this line

        this.initializeElements();
        this.setupEventListeners();
        this.updatePlaceholder();
        this.applySavedTheme();
    }

    initializeElements() {
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.chatContainer = document.getElementById('chatContainer');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChat');
        this.themeToggleBtn = document.getElementById('themeToggle');
        this.tabBtns = document.querySelectorAll('.tab-btn');
        this.suggestionCards = document.querySelectorAll('.suggestion-card');
        // Removed: this.charCount
    }

    setupEventListeners() {
        // Tab switching
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchMode(btn.dataset.mode);
            });
        });

        // Suggestion cards
        this.suggestionCards.forEach(card => {
            card.addEventListener('click', () => {
                this.switchMode(card.dataset.mode);
                this.showChatInterface();
            });
        });

        // Chat input
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Send button
        this.sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Clear chat
        this.clearChatBtn.addEventListener('click', () => {
            this.clearChat();
        });

        // Theme toggle
        this.themeToggleBtn.addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    switchMode(mode) {
        this.currentMode = mode;

        // Update active tab
        this.tabBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            }
        });

        this.updatePlaceholder();
    }

    updatePlaceholder() {
        const placeholders = {
            chat: 'Type your message...',
            lyrics: 'Enter song name or artist...',
            summarizer: 'Paste YouTube URL here...'
        };

        this.chatInput.placeholder = placeholders[this.currentMode];
    }

    showChatInterface() {
        if (this.isFirstMessage) {
            this.welcomeScreen.classList.add('hiding');
            setTimeout(() => {
                this.welcomeScreen.style.display = 'none';
                this.chatContainer.classList.add('active');
            }, 300);
        }
    }

    async sendMessage() {
        let message = this.chatInput.value.trim();
        if (!message || message.length > 2000) return;

        // Prepend command based on current mode
        if (this.currentMode === 'lyrics') {
            message = `lyrics: ${message}`;
        } else if (this.currentMode === 'summarizer') {
            message = `summarize: ${message}`;
        }

        this.showChatInterface();
        this.addMessage(this.chatInput.value, 'user');
        this.conversation.push({ role: 'user', content: this.chatInput.value }); // <-- Add user message to history
        this.chatInput.value = '';

        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversation, // <-- Send history
                }),
            });
            const data = await response.json();
            this.hideTypingIndicator();
            this.addMessage(data.reply, 'ai');
            this.conversation.push({ role: 'assistant', content: data.reply }); // <-- Add AI reply to history
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage("Sorry, there was a problem connecting to the server.", 'ai');
        }

        this.isFirstMessage = false;
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        if (sender === 'ai') {
            let cleanText = text.trim();
            // Lyrics mode: render as HTML (no formatting)
            if (this.currentMode === 'lyrics') {
                content.innerHTML = cleanText;
            } else {
                // Handle code blocks for chat/summarizer
                if (cleanText.startsWith('```')) {
                    cleanText = cleanText.replace(/```(\w+)?\s*([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
                }
                content.innerHTML = this.formatMessage(cleanText);
            }

            // --- Add Copy Button INSIDE the bubble ---
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.type = 'button';
            copyBtn.addEventListener('click', () => {
                const textToCopy = this.currentMode === 'lyrics'
                    ? content.innerText
                    : content.textContent;
                navigator.clipboard.writeText(textToCopy);
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                }, 1200);
            });

            // Wrap button in a div for alignment
            const wrapper = document.createElement('div');
            wrapper.className = 'copy-btn-wrapper';
            wrapper.appendChild(copyBtn);

            // Add button inside the bubble, at the end
            content.appendChild(wrapper);

            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            messageDiv.appendChild(wrapper); 
        } else {
            content.innerHTML = this.formatMessage(text);
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
        }

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingMessage = this.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }

    clearChat() {
        this.chatMessages.innerHTML = '';
        this.chatContainer.classList.remove('active');
        this.welcomeScreen.style.display = 'flex';
        this.welcomeScreen.classList.remove('hiding');
        this.isFirstMessage = true;
        this.conversation = []; // <-- Clear conversation history
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;

        if (this.isDarkMode) {
            document.body.setAttribute('data-theme', 'dark');
            this.themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
            this.themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'light');
        }
    }

    applySavedTheme() {
        if (this.isDarkMode) {
            document.body.setAttribute('data-theme', 'dark');
            if (this.themeToggleBtn)
                this.themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            document.body.removeAttribute('data-theme');
            if (this.themeToggleBtn)
                this.themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    // Utility functions
    formatMessage(text) {
        // Escape HTML to prevent XSS
        let escaped = this.escapeHTML(text);

        // Headings: ## Heading
        escaped = escaped.replace(/^### (.*)$/gm, '<h3>$1</h3>');
        escaped = escaped.replace(/^## (.*)$/gm, '<h2>$1</h2>');
        escaped = escaped.replace(/^# (.*)$/gm, '<h1>$1</h1>');

        // Bold: **text** or __text__
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        escaped = escaped.replace(/__(.*?)__/g, '<strong>$1</strong>');

        // Italic: *text* or _text_
        escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
        escaped = escaped.replace(/_(.*?)_/g, '<em>$1</em>');

        // Inline code: `code`
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Unordered list: * item or - item
        escaped = escaped.replace(/^\s*[\*\-] (.*)$/gm, '<li>$1</li>');
        // Ordered list: 1. item
        escaped = escaped.replace(/^\s*\d+\. (.*)$/gm, '<li>$1</li>');
        // Wrap list items in <ul> or <ol>
        escaped = escaped.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

        // Line breaks
        escaped = escaped.replace(/\n/g, '<br>');

        return escaped;
    }

    escapeHTML(text) {
        // Very basic HTML escape to prevent XSS
        return text.replace(/[&<>"']/g, function (m) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }[m];
        });
    }

    validateYouTubeURL(url) {
        const youtubeRegex = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
    }

    truncateText(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new AIAssistant();
});