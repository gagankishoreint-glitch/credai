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
        margin-bottom: 16px;
    }

    /* Features List */
    .ai-features {
        list-style: none;
        padding: 0;
        margin: 0 0 20px 0;
    }

    .ai-features li {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }

    .ai-features li ion-icon {
        color: #06b6d4; /* Cyan accent */
    }

    /* Chat Area */
    .ai-chat-body {
        padding: 0 20px 20px 20px;
        background: #0f172a;
    }

    .ai-status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.8rem;
        color: white;
        font-weight: 600;
        margin-bottom: 12px;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981; /* Green */
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    .ai-message-card {
        background: rgba(30, 41, 59, 0.5); /* Lighter Navy */
        border-radius: 12px;
        padding: 16px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
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
    }

    .ai-message-text {
        color: #e2e8f0;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .ai-message-text p {
        margin: 0 0 8px 0;
    }
    .ai-message-text p:last-child {
        margin: 0;
    }

    .ai-message-example {
        color: #94a3b8;
        font-style: italic;
        display: block;
        margin-top: 8px;
        font-size: 0.85rem;
    }

    /* Mobile Responsive */
    @media (max-width: 480px) {
        .ai-chat-window {
            width: calc(100vw - 40px);
            right: 0; /* Align relative to container */
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
                Your always-on AI Finance Assistant. Cai monitors risks, predicts payment behavior, and executes routine tasks autonomously.
            </p>

            <ul class="ai-features">
                <li>
                    <ion-icon name="chatbubble-ellipses-outline"></ion-icon>
                    Conversational Analytics ("Hey Cai, what's our DSO?")
                </li>
                <li>
                    <ion-icon name="flash-outline"></ion-icon>
                    Proactive Alerts on High-Risk Accounts
                </li>
                <li>
                    <ion-icon name="document-text-outline"></ion-icon>
                    Auto-drafting Collection Emails
                </li>
            </ul>

            <div class="ai-chat-body">
                <div class="ai-status-indicator">
                    <span class="status-dot"></span>
                    Cai - Finance Assistant (Online)
                </div>

                <div class="ai-message-card">
                    <div class="ai-avatar-small">
                        <ion-icon name="sparkles"></ion-icon>
                    </div>
                    <div class="ai-message-text">
                        <p>Hello! I'm Cai. I can analyze risk, predict payments, or draft collection emails. Try asking:</p>
                        <span class="ai-message-example">"Check risk for TechCorp" or "Draft reminder for Invoice #1023"</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <button class="ai-fab-button" id="aiFabButton" aria-label="Open AI Assistant">
        <ion-icon name="chatbubbles-outline"></ion-icon>
    </button>
</div>
`;

document.addEventListener('DOMContentLoaded', () => {
    // Inject Styles
    document.head.insertAdjacentHTML('beforeend', aiWidgetStyles);

    // Inject HTML
    document.body.insertAdjacentHTML('beforeend', aiWidgetHTML);

    // Logic
    const fab = document.getElementById('aiFabButton');
    const window = document.getElementById('aiChatWindow');
    const icon = fab.querySelector('ion-icon');

    fab.addEventListener('click', () => {
        const isActive = window.classList.contains('active');

        if (isActive) {
            window.classList.remove('active');
            icon.setAttribute('name', 'chatbubbles-outline');
        } else {
            window.classList.add('active');
            icon.setAttribute('name', 'close-outline');
        }
    });
});
