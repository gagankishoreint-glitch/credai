// Admin Panel - Real-Time Application Queue
// Displays all applications with real-time updates

document.addEventListener('DOMContentLoaded', function () {
    const applicationsTable = document.querySelector('tbody');

    if (!applicationsTable) {
        console.log('Applications table not found');
        return;
    }

    // Listen for real-time application updates
    db.collection('applications')
        .orderBy('submittedAt', 'desc')
        .onSnapshot((snapshot) => {
            // Clear existing rows
            applicationsTable.innerHTML = '';

            snapshot.forEach((doc) => {
                const app = doc.data();
                const appId = doc.id;

                // Create table row
                const row = createApplicationRow(app, appId);
                applicationsTable.appendChild(row);
            });

            console.log(`Loaded ${snapshot.size} applications`);
        }, (error) => {
            console.error('Error loading applications:', error);
        });
});

function createApplicationRow(app, appId) {
    const row = document.createElement('tr');
    row.style.cssText = 'border-bottom: 1px solid var(--color-border);';

    // Format date
    const date = app.submittedAt ?
        new Date(app.submittedAt.toDate()).toLocaleDateString() :
        'Just now';

    // Risk color mapping
    const riskColors = {
        'low': { bg: 'rgba(16, 185, 129, 0.1)', text: '#10B981', label: 'Low Risk' },
        'medium': { bg: 'rgba(245, 158, 11, 0.1)', text: '#F59E0B', label: 'Medium Risk' },
        'high': { bg: 'rgba(239, 68, 68, 0.1)', text: '#EF4444', label: 'High Risk' }
    };

    const risk = riskColors[app.riskLevel] || riskColors['low'];

    row.innerHTML = `
        <td style="padding: 20px;">
            <div>
                <div style="font-weight: 600; margin-bottom: 4px;">#${appId.substring(0, 6)}</div>
                <div style="font-size: 0.85rem; color: var(--color-text-muted);">${date}</div>
            </div>
        </td>
        <td style="padding: 20px;">
            <div style="font-weight: 500;">${app.businessName || 'N/A'}</div>
        </td>
        <td style="padding: 20px;">
            <div style="font-weight: 600; color: var(--color-white);">$${(app.loanAmount || 0).toLocaleString()}</div>
        </td>
        <td style="padding: 20px;">
            <div style="font-size: 1.5rem; font-weight: 700; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ${app.aiScore || '---'}
            </div>
        </td>
        <td style="padding: 20px;">
            <span style="background: ${risk.bg}; color: ${risk.text}; padding: 6px 12px; border-radius: var(--radius-pill); font-size: 0.8rem; font-weight: 600;">
                ${risk.label}
            </span>
        </td>
        <td style="padding: 20px; text-align: right;">
            <button class="btn btn-outline" style="padding: 8px 20px; font-size: 0.85rem;" 
                    onclick="viewApplication('${appId}')">
                Review
            </button>
        </td>
    `;

    return row;
}

// View application details
function viewApplication(appId) {
    db.collection('applications').doc(appId).get()
        .then((doc) => {
            if (doc.exists) {
                const app = doc.data();
                showApplicationDetail(app, appId);
            }
        })
        .catch((error) => {
            console.error('Error fetching application:', error);
            alert('Error loading application details');
        });
}

function showApplicationDetail(app, appId) {
    const detailView = document.getElementById('detail-view');
    if (!detailView) return;

    // Update detail view content
    const businessNameEl = detailView.querySelector('h3');
    if (businessNameEl) {
        businessNameEl.textContent = app.businessName || 'Unknown Business';
    }

    // Show the detail view
    detailView.style.display = 'block';
    detailView.scrollIntoView({ behavior: 'smooth' });

    console.log('Viewing application:', appId, app);
}
