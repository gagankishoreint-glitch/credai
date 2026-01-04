
// Cai - Artificial Intelligence Finance Agent
// Handles interaction logic for the Autonomous Finance chat interface

document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const messagesContainer = document.getElementById('chat-messages');

    if (!chatInput || !sendBtn || !messagesContainer) return;

    // --- Synthetic Data "Database" ---
    const MOCK_DB = {
        'TechCorp': { score: 780, risk: 'Low', dso: 32, limit_usd: '$500,000', limit_inr: '₹4,15,00,000', behavior: 'Pays 2 days early' },
        'Acme': { score: 620, risk: 'Medium', dso: 45, limit_usd: '$50,000', limit_inr: '₹41,50,000', behavior: 'Pays on due date' },
        'GlobalTrade': { score: 450, risk: 'High', dso: 65, limit_usd: '$10,000', limit_inr: '₹8,30,000', behavior: 'Avg 15 days late' }
    };

    let currentCurrency = 'USD'; // Default

    // --- Event Listeners ---
    sendBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    // --- Core Logic ---
    function handleSendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Add User Message
        appendMessage('user', text);
        chatInput.value = '';

        // 2. Simulate "Thinking" (Delay)
        showTypingIndicator();

        setTimeout(() => {
            removeTypingIndicator();
            const response = generateAIResponse(text);
            appendMessage('bot', response);
        }, 1200 + Math.random() * 800); // Random delay 1.2s - 2.0s
    }

    // --- AI Intent Classification ---
    function generateAIResponse(input) {
        const lowerInput = input.toLowerCase();

        // Intent: Switch Currency
        if (lowerInput.includes('rupee') || lowerInput.includes('inr') || lowerInput.includes('india')) {
            currentCurrency = 'INR';
            return "I've switched my financial reporting to <strong>Indian Rupees (₹)</strong>. Ask me to analyze a company now.";
        }
        if (lowerInput.includes('dollar') || lowerInput.includes('usd')) {
            currentCurrency = 'USD';
            return "I've switched my financial reporting to <strong>US Dollars ($)</strong>.";
        }

        // Intent: Greeting
        if (lowerInput.match(/\b(hi|hello|hey|greetings)\b/)) {
            return "Hello! I'm ready to assist with your financial operations. You can ask me to analyze a company or draft emails.";
        }

        // Intent: Risk/Score Analysis
        if (lowerInput.includes('risk') || lowerInput.includes('score') || lowerInput.includes('credit')) {
            // Check for entity names
            const entity = Object.keys(MOCK_DB).find(key => lowerInput.includes(key.toLowerCase()));

            if (entity) {
                const data = MOCK_DB[entity];
                let color = data.risk === 'Low' ? '#10B981' : (data.risk === 'Medium' ? '#F59E0B' : '#EF4444');
                const limit = currentCurrency === 'INR' ? data.limit_inr : data.limit_usd;

                return `
                    <strong>Analysis for ${entity}:</strong><br>
                    • Credit Score: ${data.score} <br>
                    • Risk Level: <span style="color: ${color}; font-weight: bold;">${data.risk}</span><br>
                    • Recommended Limit: <strong>${limit}</strong><br>
                    • Behavior: ${data.behavior}
                `;
            } else {
                return "I can analyze credit risk. Please specify a company name like 'TechCorp', 'Acme', or 'GlobalTrade'.";
            }
        }

        // Intent: Email Drafting
        if (lowerInput.includes('email') || lowerInput.includes('draft') || lowerInput.includes('reminder')) {
            return `
                I've drafted a reminder email for the overdue invoice:<br><br>
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; font-style: italic; font-size: 0.85rem;">
                    "Dear Finance Team,<br>
                    This is a gentle reminder regarding Invoice #1023 ($12,500) which is now 5 days overdue.<br>
                    Please click here to pay immediately to avoid service interruption."
                </div>
                <br>
                <button class="btn btn-sm btn-primary" style="padding: 4px 12px; font-size: 0.8rem; margin-top: 8px;">Send Now</button>
            `;
        }

        // Intent: DSO / Metrics
        if (lowerInput.includes('dso') || lowerInput.includes('cash') || lowerInput.includes('metric')) {
            return "Current Portfolio DSO is <strong>38 days</strong>, which is 12% better than the industry average. <br>Predicted cash inflow for next week: <strong>$1.2M</strong>.";
        }

        // Fallback
        return "I'm processing that context. Could you clarify if you need a <strong>Risk Analysis</strong>, <strong>Collection Draft</strong>, or <strong>Portfolio Metrics</strong>?";
    }

    // --- UI Helpers ---
    function appendMessage(sender, htmlContent) {
        const div = document.createElement('div');
        div.className = `message-${sender}`;
        div.style.cssText = `display: flex; gap: 12px; margin-bottom: 20px; ${sender === 'user' ? 'flex-direction: row-reverse;' : ''}`;

        const avatar = document.createElement('div');
        avatar.style.cssText = `width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;`;

        if (sender === 'bot') {
            avatar.style.background = 'var(--gradient-primary)';
            avatar.innerHTML = '<ion-icon name="sparkles" style="font-size: 16px; color: white;"></ion-icon>';
        } else {
            avatar.style.background = '#333';
            avatar.innerHTML = '<ion-icon name="person" style="font-size: 16px; color: #aaa;"></ion-icon>';
        }

        const bubble = document.createElement('div');
        bubble.style.cssText = `padding: 12px 16px; border-radius: ${sender === 'bot' ? '0 12px 12px 12px' : '12px 0 12px 12px'}; max-width: 85%;`;

        if (sender === 'bot') {
            bubble.style.background = 'rgba(255,255,255,0.1)';
            bubble.style.color = '#eee';
        } else {
            bubble.style.background = 'var(--color-accent-cyan)';
            bubble.style.color = '#000';
            bubble.style.fontWeight = '500';
        }

        bubble.innerHTML = `<p style="margin: 0; font-size: 0.9rem;">${htmlContent}</p>`;

        div.appendChild(avatar);
        div.appendChild(bubble);
        messagesContainer.appendChild(div);
        messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
    }

    function showTypingIndicator() {
        const id = 'typing-indicator';
        if (document.getElementById(id)) return;

        const div = document.createElement('div');
        div.id = id;
        div.style.cssText = `display: flex; gap: 12px; margin-bottom: 20px;`;
        div.innerHTML = `
            <div style="width: 32px; height: 32px; background: var(--gradient-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <ion-icon name="sparkles" style="font-size: 16px; color: white;"></ion-icon>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 12px 16px; border-radius: 0 12px 12px 12px; display: flex; align-items: center; gap: 4px;">
                <div class="dot" style="width: 6px; height: 6px; background: #aaa; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both;"></div>
                <div class="dot" style="width: 6px; height: 6px; background: #aaa; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.32s;"></div>
                <div class="dot" style="width: 6px; height: 6px; background: #aaa; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.16s;"></div>
            </div>
        `;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });

        // Add keyframes if not present
        if (!document.getElementById('typing-style')) {
            const style = document.createElement('style');
            style.id = 'typing-style';
            style.textContent = `
                @keyframes bounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }
});
