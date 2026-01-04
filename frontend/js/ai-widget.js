const aiWidgetStyles = `
<style>
    /* Widget Container */
    #ai-widget-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
        font-family: 'Inter', sans-serif;
    }

    /* Floating Action Button (FAB) */
    .ai-fab-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        border: none;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.5);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 28px;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .ai-fab-button:hover {
        transform: scale(1.1);
    }

    /* Chat Window */
    .ai-chat-window {
        position: absolute;
        bottom: 80px;
        right: 0;
        width: 380px;
        height: 550px; /* Fixed height for chat */
        background: #0f172a; /* Dark Navy Background */
        border: 1px solid rgba(59, 130, 246, 0.3); /* Subtle Blue Border */
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        overflow: hidden;
        opacity: 0;
        transform: translateY(20px) scale(0.95);
        visibility: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
    }

    .ai-chat-window.active {
        opacity: 1;
        transform: translateY(0) scale(1);
        visibility: visible;
    }

    /* Header */
    .ai-header {
        padding: 20px;
        background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent 70%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        flex-shrink: 0;
    }

    .ai-title-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    .ai-icon-large {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
    }

    .ai-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
    }

    .ai-description {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0;
    }

    /* Chat Scroll Area */
    .ai-chat-body {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: #0f172a;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    /* Status Indicator */
    .ai-status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 8px;
        align-self: center;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981; /* Green */
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    /* Messages */
    .ai-message {
        display: flex;
        gap: 12px;
        max-width: 85%;
        animation: fadeIn 0.3s ease;
    }

    .ai-message.bot {
        align-self: flex-start;
    }

    .ai-message.user {
        align-self: flex-end;
        flex-direction: row-reverse;
    }

    .ai-avatar-small {
        width: 28px;
        height: 28px;
        min-width: 28px;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        flex-shrink: 0;
    }

    .ai-message-content {
        padding: 12px 16px;
        border-radius: 12px;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .ai-message.bot .ai-message-content {
        background: #1e293b;
        color: #e2e8f0;
        border-top-left-radius: 2px;
    }

    .ai-message.user .ai-message-content {
        background: #3b82f6;
        color: white;
        border-top-right-radius: 2px;
    }

    .ai-message-example {
        color: #94a3b8;
        font-style: italic;
        display: block;
        margin-top: 8px;
        font-size: 0.85rem;
    }

    /* Quick Action Buttons */
    .ai-quick-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
        align-self: flex-start;
        max-width: 85%;
    }

    .ai-quick-btn {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #3b82f6;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;
    }

    .ai-quick-btn:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: #3b82f6;
        transform: translateY(-2px);
    }

    /* Input Area */
    .ai-input-area {
        padding: 16px;
        background: #1e293b;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .ai-input {
        flex: 1;
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 24px;
        padding: 10px 16px;
        color: white;
        font-size: 0.9rem;
        outline: none;
        transition: border-color 0.2s;
    }

    .ai-input:focus {
        border-color: #3b82f6;
    }

    .ai-send-btn {
        width: 40px;
        height: 40px;
        background: #3b82f6;
        border: none;
        border-radius: 50%;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.2s;
    }

    .ai-send-btn:hover {
        background: #2563eb;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Mobile Responsive */
    @media (max-width: 480px) {
        .ai-chat-window {
            width: calc(100vw - 40px);
            right: 0;
            height: 500px;
            bottom: 80px;
        }
        #ai-widget-container {
            right: 20px;
            bottom: 20px;
        }
    }
</style>
`;

const aiWidgetHTML = `
<div id="ai-widget-container">
    <div class="ai-chat-window" id="aiChatWindow">
        <div class="ai-header">
            <div class="ai-title-row">
                <div class="ai-icon-large">
                    <ion-icon name="sparkles"></ion-icon>
                </div>
                <h3 class="ai-title">Meet Cai</h3>
            </div>
            <p class="ai-description">
                Your AI Finance Assistant. Ask me about credit evaluation, risk models, or pricing.
            </p>
        </div>

        <div class="ai-chat-body" id="aiChatBody">
            <div class="ai-status-indicator">
                <span class="status-dot"></span>
                Cai is Online
            </div>

            <!-- Intro Message -->
            <div class="ai-message bot">
                <div class="ai-avatar-small">
                    <ion-icon name="sparkles"></ion-icon>
                </div>
                <div class="ai-message-content">
                    <p>Hello! I'm Cai. I can help guide you through our platform. Try asking:</p>
                    <span class="ai-message-example">"How does the risk model work?" or "Is there a free trial?"</span>
                </div>
            </div>
        </div>

        <div class="ai-input-area">
            <input type="text" class="ai-input" id="aiChatInput" placeholder="Type a message..." autocomplete="off">
            <button class="ai-send-btn" id="aiSendBtn">
                <ion-icon name="send"></ion-icon>
            </button>
        </div>
    </div>

    <button class="ai-fab-button" id="aiFabButton" aria-label="Open AI Assistant">
        <ion-icon name="chatbubbles-outline"></ion-icon>
    </button>
</div>
`;

// Extended Knowledge Base (The "Dataset")
const knowledgeBase = {
    greeting: {
        keywords: ['hello', 'hi', 'hey', 'start', 'begin', 'morning', 'evening', 'yo'],
        response: "Hello! I'm ready to help you analyze credit risks. How can I assist you today?"
    },
    about_site: {
        keywords: ['what this site does', 'what is this site', 'purpose', 'about', 'function', 'overview', 'summary', 'explain this site', 'what is CredAi'],
        response: "CredAi is an **AI-Driven Credit Evaluation Platform**. We automate the lending underwriting process for SMBs and consumers. Our system replaces manual underwriting (days) with AI (seconds) using XGBoost and Random Forest models with >80% accuracy."
    },
    methodology_steps: {
        keywords: ['methodology', 'how it works', 'process', 'steps', 'approach'],
        response: "Our methodology follows 4 steps: <br>1. **Data Preprocessing**: Cleaning and normalizing data.<br>2. **Document Analysis**: Optical Character Recognition (OCR) for PDFs.<br>3. **Model Development**: Risk scoring using XGBoost and Random Forest.<br>4. **Decision Logic**: Automated approval/rejection thresholds."
    },
    tech_stack: {
        keywords: ['tech stack', 'technology', 'backend', 'frontend', 'python', 'react', 'database'],
        response: "Our Tech Stack includes: <br>• **Backend**: Python (Flask/FastAPI) with Scikit-learn/TensorFlow.<br>• **Frontend**: HTML5, CSS3, JavaScript.<br>• **Data**: PostgreSQL/MongoDB and Firebase for realtime updates."
    },
    features: {
        keywords: ['features', 'value', 'benefit', 'advantage', 'accuracy'],
        response: "Key Features:<br>• **Greater Accuracy**: Analyzes thousands of data points.<br>• **Full Explainability**: Transparent reasoning for every score.<br>• **Proven Value**: 30% reduction in default rates."
    },
    navigate_apply: {
        keywords: ['navigate', 'apply', 'application', 'sign up', 'register', 'start', 'loan', 'get started'],
        response: "I can help you get started. <br><br>👉 <a href='application.html' style='color: #3b82f6; text-decoration: none; font-weight: bold;'>Click here to Start a New Application</a>.<br>Or visit the <a href='signup.html' style='color: #06b6d4;'>Sign Up page</a> to create an account."
    },
    navigate_dashboard: {
        keywords: ['dashboard', 'home', 'main', 'panel', 'board', 'login'],
        response: "You can view your active applications and analytics on the <a href='dashboard.html' style='color: #3b82f6; font-weight: bold;'>Dashboard</a>."
    },
    risk_model: {
        keywords: ['risk', 'model', 'xgboost', 'random forest', 'logistic regression', 'algorithm', 'score'],
        response: "We use three core models:<br>1. **XGBoost**: For high-performance classification.<br>2. **Random Forest**: For robust feature importance.<br>3. **Logistic Regression**: A baseline for linear interpretability."
    },
    pricing: {
        keywords: ['price', 'cost', 'plan', 'free', 'subscription', 'pay', 'money', 'charge'],
        response: "We offer a **Free Starter Plan** for basic evaluations. Our **Pro Plan** ($49/mo) includes detailed risk reports, API access, and priority support. You can view all options on our Pricing page."
    },
    security: {
        keywords: ['security', 'safe', 'data', 'privacy', 'encrypt', 'gdpr'],
        response: "Your data security is our top priority. We use **256-bit AES encryption** for all stored data and strictly adhere to GDPR and SOC2 compliance standards."
    },
    contact: {
        keywords: ['contact', 'support', 'email', 'help', 'human', 'talk'],
        response: "You can reach our human support team at **support@credai.com**. We're available 24/7 for enterprise inquiries."
    },
    default: {
        response: "I'm trained specifically on CredAi's services. Try asking me to **'Navigate to Application'**, explain **'How it works'**, or check **'Pricing'**."
    }
};

function initAIWidget() {
    // Prevent duplicate injection
    if (document.getElementById('ai-widget-container')) return;

    // Inject Styles
    document.head.insertAdjacentHTML('beforeend', aiWidgetStyles);

    // Inject HTML
    document.body.insertAdjacentHTML('beforeend', aiWidgetHTML);

    // Elements
    const fab = document.getElementById('aiFabButton');
    const windowEl = document.getElementById('aiChatWindow');
    const icon = fab.querySelector('ion-icon');
    const chatBody = document.getElementById('aiChatBody');
    const chatInput = document.getElementById('aiChatInput');
    const sendBtn = document.getElementById('aiSendBtn');

    // Toggle Window
    fab.addEventListener('click', () => {
        const isActive = windowEl.classList.contains('active');
        if (isActive) {
            windowEl.classList.remove('active');
            icon.setAttribute('name', 'chatbubbles-outline');
        } else {
            windowEl.classList.add('active');
            icon.setAttribute('name', 'close-outline');
            setTimeout(() => chatInput.focus(), 300); // Focus input on open
        }
    });

    // Add initial quick action buttons
    setTimeout(() => {
        const initialActions = document.createElement('div');
        initialActions.className = 'ai-quick-actions';

        const initialSuggestions = ['How does it work?', 'Pricing', 'Start Application'];
        initialSuggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.className = 'ai-quick-btn';
            btn.textContent = suggestion;
            btn.onclick = () => {
                chatInput.value = suggestion;
                processMessage();
            };
            initialActions.appendChild(btn);
        });

        chatBody.appendChild(initialActions);
    }, 100);


    // Simple Markdown Parser
    function parseMarkdown(text) {
        // Convert **bold** to <strong>bold</strong>
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Convert <br> tags (already in responses)
        // Links are already HTML, so they're fine
        return text;
    }

    // Chat Logic
    function appendMessage(text, sender, suggestions = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-message ${sender}`;

        let content = '';
        if (sender === 'bot') {
            const formattedText = parseMarkdown(text);
            content = `
                <div class="ai-avatar-small">
                    <ion-icon name="sparkles"></ion-icon>
                </div>
                <div class="ai-message-content"><p>${formattedText}</p></div>
            `;
        } else {
            content = `<div class="ai-message-content"><p>${text}</p></div>`;
        }

        msgDiv.innerHTML = content;
        chatBody.appendChild(msgDiv);

        // Add Quick Action Buttons if provided
        if (suggestions.length > 0) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-quick-actions';

            suggestions.forEach(suggestion => {
                const btn = document.createElement('button');
                btn.className = 'ai-quick-btn';
                btn.textContent = suggestion;
                btn.onclick = () => {
                    chatInput.value = suggestion;
                    processMessage();
                };
                actionsDiv.appendChild(btn);
            });

            chatBody.appendChild(actionsDiv);
        }

        chatBody.scrollTop = chatBody.scrollHeight; // Auto-scroll
    }

    function processMessage() {
        const text = chatInput.value.trim().toLowerCase();
        if (!text) return;

        // User Message
        appendMessage(chatInput.value, 'user');
        chatInput.value = '';

        // Bot Typing Simulation
        setTimeout(() => {
            let response = knowledgeBase.default.response;
            let bestMatchScore = 0;

            // Advanced Token-Based Matching Logic
            // This fixes the "hi" matching "this" bug by looking for word boundaries or exact phrase matches.

            for (const [key, data] of Object.entries(knowledgeBase)) {
                if (key === 'default') continue;

                let currentScore = 0;

                data.keywords.forEach(keyword => {
                    const normalizedKeyword = keyword.toLowerCase();

                    // 1. Exact Phrase Match (Highest Priority)
                    if (text.includes(normalizedKeyword)) {
                        currentScore += 10;
                    }
                    // 2. Individual Word Match with Boundary Check (Medium Priority)
                    else {
                        // Split keyword into words (e.g., "what is")
                        const words = normalizedKeyword.split(' ');
                        let allWordsFound = true;

                        // Check if ALL words in the keyword phrase exist as distinct words in user text
                        for (const word of words) {
                            // Regex: \bword\b matches whole word only. escape special chars just in case.
                            // simpler check:
                            const regex = new RegExp('\\b' + word + '\\b', 'i');
                            if (!regex.test(text)) {
                                allWordsFound = false;
                                break;
                            }
                        }

                        if (allWordsFound) {
                            currentScore += 5;
                        }
                    }
                });

                if (currentScore > bestMatchScore) {
                    bestMatchScore = currentScore;
                    response = data.response;
                }
            }

            // Determine suggestions based on response type
            let suggestions = [];
            if (bestMatchScore === 0) {
                // Default fallback - show common options
                suggestions = ['How does it work?', 'Pricing', 'Start Application'];
            } else if (response.includes('XGBoost')) {
                suggestions = ['What is XGBoost?', 'View Tech Stack', 'Start Application'];
            } else if (response.includes('Free Starter')) {
                suggestions = ['Sign Up', 'View Features', 'Contact Support'];
            } else if (response.includes('Application')) {
                suggestions = ['Go to Dashboard', 'View Pricing', 'Contact Support'];
            } else {
                suggestions = ['Tell me more', 'Pricing', 'Start Application'];
            }

            appendMessage(response, 'bot', suggestions);
        }, 600);
    }

    // Event Listeners for Chat
    sendBtn.addEventListener('click', processMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') processMessage();
    });
}

// **Fix for Race Condition**: Check if DOM is already ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAIWidget);
} else {
    initAIWidget(); // Run immediately if DOM is already loaded
}
