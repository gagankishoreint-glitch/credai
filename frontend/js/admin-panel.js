// Admin Panel - FULLY FUNCTIONAL with Real-Time Firebase Data
// Displays all applications, search, filter, and review functionality

document.addEventListener('DOMContentLoaded', function () {
    const applicationsTable = document.querySelector('#applications-tbody');
    const searchInput = document.querySelector('input[placeholder="Search..."]');

    if (!applicationsTable) {
        console.log('❌ Applications table not found');
        return;
    }

    console.log('✅ Admin panel initializing...');

    let allApplications = [];
    let selectedApplication = null;

    // Listen for real-time application updates from Firebase
    db.collection('applications')
        .orderBy('submittedAt', 'desc')
        .onSnapshot((snapshot) => {
            console.log(`📊 Loaded ${snapshot.size} applications from Firebase`);

            allApplications = [];
            applicationsTable.innerHTML = '';

            if (snapshot.empty) {
                applicationsTable.innerHTML = `
                    <tr>
                        <td colspan="6" style="padding: 60px; text-align: center;">
                            <ion-icon name="document-text-outline" style="font-size: 48px; color: var(--color-text-muted); margin-bottom: 16px;"></ion-icon>
                            <div style="font-size: 1.1rem; margin-bottom: 8px;">No Applications Yet</div>
                            <div style="color: var(--color-text-muted); font-size: 0.9rem;">Applications will appear here when submitted</div>
                        </td>
                    </tr>
                `;
                return;
            }

            snapshot.forEach((doc) => {
                const app = { id: doc.id, ...doc.data() };
                allApplications.push(app);

                const row = createApplicationRow(app);
                applicationsTable.appendChild(row);
            });

            console.log('✅ Applications loaded successfully');
        }, (error) => {
            console.error('❌ Error loading applications:', error);
            applicationsTable.innerHTML = `
                <tr>
                    <td colspan="6" style="padding: 40px; text-align: center; color: #EF4444;">
                        <div>Error loading applications: ${error.message}</div>
                    </td>
                </tr>
            `;
        });

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filterApplications(searchTerm);
        });
    }

    function filterApplications(searchTerm) {
        applicationsTable.innerHTML = '';

        const filtered = allApplications.filter(app =>
            (app.businessName || '').toLowerCase().includes(searchTerm) ||
            (app.industry || '').toLowerCase().includes(searchTerm) ||
            (app.id || '').toLowerCase().includes(searchTerm)
        );

        if (filtered.length === 0) {
            applicationsTable.innerHTML = `
                <tr>
                    <td colspan="6" style="padding: 40px; text-align: center; color: var(--color-text-muted);">
                        No applications match "${searchTerm}"
                    </td>
                </tr>
            `;
            return;
        }

        filtered.forEach(app => {
            const row = createApplicationRow(app);
            applicationsTable.appendChild(row);
        });
    }
});

function createApplicationRow(app) {
    const row = document.createElement('tr');
    row.style.cssText = 'border-bottom: 1px solid var(--color-border); cursor: pointer;';
    row.onmouseenter = () => row.style.background = 'rgba(90, 69, 255, 0.05)';
    row.onmouseleave = () => row.style.background = 'transparent';

    // Format date
    const date = app.submittedAt ?
        new Date(app.submittedAt.toDate()).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) :
        'Just now';

    // Risk color mapping
    const riskColors = {
        'low': { bg: 'rgba(16, 185, 129, 0.1)', text: '#10B981', label: 'Low Risk' },
        'medium': { bg: 'rgba(245, 158, 11, 0.1)', text: '#F59E0B', label: 'Medium Risk' },
        'high': { bg: 'rgba(239, 68, 68, 0.1)', text: '#EF4444', label: 'High Risk' }
    };

    const risk = riskColors[app.riskLevel] || { bg: 'rgba(100, 100, 100, 0.1)', text: '#888', label: 'Pending' };

    // Calculate a simple credit score if not present (based on revenue/loan ratio)
    let displayScore = app.aiScore || app.creditScore;
    if (!displayScore && app.annualRevenue && app.loanAmount) {
        const ratio = app.annualRevenue / app.loanAmount;
        displayScore = Math.min(850, Math.max(300, Math.round(300 + (ratio * 100))));
    }

    row.innerHTML = `
        <td style="padding: 20px;">
            <div>
                <div style="font-weight: 600; margin-bottom: 4px;">#${app.id.substring(0, 6)}</div>
                <div style="font-size: 0.85rem; color: var(--color-text-muted);">${date}</div>
            </div>
        </td>
        <td style="padding: 20px;">
            <div style="font-weight: 500;">${app.businessName || 'N/A'}</div>
            <div style="font-size: 0.85rem; color: var(--color-text-muted);">${app.industry || ''}</div>
        </td>
        <td style="padding: 20px;">
            <div style="font-weight: 600; color: var(--color-white);">$${(app.loanAmount || 0).toLocaleString()}</div>
        </td>
        <td style="padding: 20px;">
            <div style="font-size: 1.5rem; font-weight: 700; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                ${displayScore || '---'}
            </div>
        </td>
        <td style="padding: 20px;">
            <span style="background: ${risk.bg}; color: ${risk.text}; padding: 6px 12px; border-radius: var(--radius-pill); font-size: 0.8rem; font-weight: 600;">
                ${risk.label}
            </span>
        </td>
        <td style="padding: 20px; text-align: right;">
            <button class="btn btn-outline" style="padding: 8px 20px; font-size: 0.85rem;" 
                    onclick="event.stopPropagation(); viewApplication('${app.id}')">
                Review
            </button>
        </td>
    `;

    // Click row to view details
    row.onclick = () => viewApplication(app.id);

    return row;
}

// View application details
function viewApplication(appId) {
    console.log('👁️ Viewing application:', appId);

    db.collection('applications').doc(appId).get()
        .then((doc) => {
            if (doc.exists) {
                const app = { id: doc.id, ...doc.data() };
                showApplicationDetail(app);
            }
        })
        .catch((error) => {
            console.error('Error fetching application:', error);
            alert('Error loading application details');
        });
}

function showApplicationDetail(app) {
    const detailView = document.getElementById('detail-view');
    if (!detailView) return;

    // Update detail view content
    detailView.innerHTML = `
        <div class="feature-card glow-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 32px;">
                <div>
                    <h3 style="margin-bottom: 8px;">${app.businessName || 'Unknown Business'}</h3>
                    <p style="color: var(--color-text-muted);">Application #${app.id.substring(0, 8)}</p>
                </div>
                <button onclick="closeDetail()" class="btn btn-outline" style="padding: 8px 16px;">
                    <ion-icon name="close-outline"></ion-icon> Close
                </button>
            </div>

            <!-- Application Details Grid -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 32px;">
                <div style="padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-lg);">
                    <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">BUSINESS NAME</div>
                    <div style="font-weight: 600;">${app.businessName || 'N/A'}</div>
                </div>
                <div style="padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-lg);">
                    <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">INDUSTRY</div>
                    <div style="font-weight: 600;">${app.industry || 'N/A'}</div>
                </div>
                <div style="padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-lg);">
                    <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">LOAN AMOUNT</div>
                    <div style="font-weight: 700; font-size: 1.2rem; color: var(--color-accent-purple);">$${(app.loanAmount || 0).toLocaleString()}</div>
                </div>
                <div style="padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-lg);">
                    <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">ANNUAL REVENUE</div>
                    <div style="font-weight: 600;">$${(app.annualRevenue || 0).toLocaleString()}</div>
                </div>
                <div style="padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-lg);">
                    <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">YEARS IN BUSINESS</div>
                    <div style="font-weight: 600;">${app.yearsInBusiness || 0} years</div>
                </div>
                <div style="padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-lg);">
                    <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">STATUS</div>
                    <div style="font-weight: 600; text-transform: capitalize;">${app.status || 'Pending'}</div>
                </div>
            </div>

            <!-- Risk Assessment -->
            <div style="padding: 24px; background: var(--color-bg-secondary); border-radius: var(--radius-lg); margin-bottom: 24px;">
                <h4 style="margin-bottom: 16px;">📊 Risk Assessment Report</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                    <div>
                        <div style="color: var(--color-text-muted); font-size: 0.85rem; margin-bottom: 8px;">AI Credit Score</div>
                        <div style="font-size: 2rem; font-weight: 700; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                            ${app.aiScore || app.creditScore || '---'}
                        </div>
                    </div>
                    <div>
                        <div style="color: var(--color-text-muted); font-size: 0.85rem; margin-bottom: 8px;">Risk Level</div>
                        <div style="font-size: 1.5rem; font-weight: 600; text-transform: capitalize;">
                            ${app.riskLevel || 'Analyzing...'}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div style="display: flex; gap: 16px; justify-content: flex-end;">
                <button onclick="rejectApplication('${app.id}')" class="btn btn-outline" style="padding: 12px 24px; border-color: #EF4444; color: #EF4444;">
                    ❌ Reject
                </button>
                <button onclick="approveApplication('${app.id}')" class="btn btn-primary" style="padding: 12px 24px;">
                    ✅ Approve
                </button>
            </div>
        </div>
    `;

    // Show the detail view
    detailView.style.display = 'block';
    detailView.scrollIntoView({ behavior: 'smooth' });
}

function closeDetail() {
    const detailView = document.getElementById('detail-view');
    if (detailView) {
        detailView.style.display = 'none';
    }
}

async function approveApplication(appId) {
    if (!confirm('Are you sure you want to APPROVE this application?')) return;

    try {
        await db.collection('applications').doc(appId).update({
            decision: 'approved',
            status: 'decision',
            decidedAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        alert('✅ Application APPROVED successfully!');
        closeDetail();
    } catch (error) {
        console.error('Error approving:', error);
        alert('Error approving application: ' + error.message);
    }
}

async function rejectApplication(appId) {
    if (!confirm('Are you sure you want to REJECT this application?')) return;

    try {
        await db.collection('applications').doc(appId).update({
            decision: 'rejected',
            status: 'decision',
            decidedAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        alert('❌ Application REJECTED.');
        closeDetail();
    } catch (error) {
        console.error('Error rejecting:', error);
        alert('Error rejecting application: ' + error.message);
    }
}
