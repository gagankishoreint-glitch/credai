const API_BASE_URL = window.API_CONFIG ? window.API_CONFIG.BASE_URL : '/api';

document.addEventListener('DOMContentLoaded', async () => {
    // Basic check if user is logged in (client-side only for now)
    try {
        await window.authHelpers.checkAuth();
        loadAllApplications();
    } catch (e) {
        window.location.href = 'login.html';
    }
});

async function loadAllApplications() {
    const container = document.querySelector('.admin-queue-container') || document.querySelector('.container');

    // Inject proper structure if missing
    if (!document.querySelector('.applications-grid')) {
        const grid = document.createElement('div');
        grid.className = 'applications-grid';
        grid.style.marginTop = '24px';
        grid.style.display = 'grid';
        grid.style.gap = '20px';
        container.appendChild(grid);
    }

    const grid = document.querySelector('.applications-grid');
    grid.innerHTML = '<p style="color:white;">Loading applications...</p>';

    try {
        // Fetch from new Admin Endpoint
        // Note: For demo simplicity, we use the same auth token. In prod, check permissions.
        const response = await fetch(`${API_BASE_URL}/admin/applications`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to load applications');

        const apps = await response.json();

        if (apps.length === 0) {
            grid.innerHTML = '<p style="color: var(--color-text-secondary);">No applications found in the system.</p>';
            return;
        }

        grid.innerHTML = apps.map(app => createAdminCard(app)).join('');

    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p style="color: #EF4444;">Error accessing underwriter data. Please ensure the backend is running.</p>';
    }
}

function createAdminCard(app) {
    const statusColor = app.status === 'approved' ? '#10B981' : (app.status === 'rejected' ? '#EF4444' : '#F59E0B');
    const score = app.ai_score || 0;

    // Parse data safely
    let aiData = {};
    if (typeof app.data === 'string') {
        try { aiData = JSON.parse(app.data); } catch (e) { }
    } else {
        aiData = app.data || {};
    }

    const decision = aiData.decision || 'pending';

    return `
    <div class="feature-card glow-card" style="padding: 24px; display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h3 style="margin: 0; font-size: 1.25rem;">${app.business_name}</h3>
                <p style="color: var(--color-text-secondary); font-size: 0.9rem; margin-top: 4px;">User: ${app.full_name || app.email}</p>
            </div>
            <span style="background: ${statusColor}20; color: ${statusColor}; padding: 4px 12px; border-radius: 99px; font-size: 0.85rem; font-weight: 600;">
                ${decision.toUpperCase()}
            </span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 8px;">
            <div style="background: var(--color-bg-primary); padding: 12px; border-radius: 8px;">
                <p style="font-size: 0.8rem; color: var(--color-text-secondary); margin-bottom: 4px;">Request Amount</p>
                <p style="font-weight: 600; font-size: 1.1rem;">$${Number(app.amount).toLocaleString()}</p>
            </div>
            <div style="background: var(--color-bg-primary); padding: 12px; border-radius: 8px;">
                <p style="font-size: 0.8rem; color: var(--color-text-secondary); margin-bottom: 4px;">AI Score</p>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-weight: 600; font-size: 1.1rem; color: var(--color-accent-blue);">${score}</span>
                    <span style="font-size: 0.8rem; color: var(--color-text-secondary);">/ 850</span>
                </div>
            </div>
        </div>

        <div>
            <p style="font-size: 0.85rem; color: var(--color-text-secondary); margin-bottom: 8px;">AI Recommendation:</p>
            <p style="font-size: 0.95rem; line-height: 1.5;">${aiData.insights && aiData.insights.length > 0 ? aiData.insights[0].text : 'No specific insights generated.'}</p>
        </div>

        <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid var(--color-border); display: flex; gap: 12px;">
            <button class="btn btn-primary" style="flex: 1; padding: 8px;">Approve</button>
            <button class="btn btn-outline" style="flex: 1; padding: 8px;">Reject</button>
        </div>
    </div>
    `;
}
