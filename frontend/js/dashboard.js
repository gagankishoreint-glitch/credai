// Dashboard JavaScript with MindMarket styling

const api = new APIClient();
let allApplications = [];
let currentView = 'grid'; // 'grid' or 'table'

document.addEventListener('DOMContentLoaded', function () {
    const statusFilter = document.getElementById('statusFilter');
    const refreshBtn = document.getElementById('refreshBtn');
    const viewGridBtn = document.getElementById('viewGrid');
    const viewTableBtn = document.getElementById('viewTable');

    // Load applications on page load
    loadApplications();

    // Event listeners
    if (statusFilter) {
        statusFilter.addEventListener('change', filterApplications);
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadApplications);
    }

    if (viewGridBtn && viewTableBtn) {
        viewGridBtn.addEventListener('click', () => switchView('grid'));
        viewTableBtn.addEventListener('click', () => switchView('table'));
    }
});

function switchView(view) {
    currentView = view;
    const viewGridBtn = document.getElementById('viewGrid');
    const viewTableBtn = document.getElementById('viewTable');
    const gridEl = document.getElementById('applicationsGrid');
    const tableEl = document.getElementById('applicationsTable');

    // Update buttons
    if (view === 'grid') {
        viewGridBtn.classList.add('active');
        viewTableBtn.classList.remove('active');
        if (allApplications.length > 0) {
            gridEl.style.display = 'grid';
            tableEl.style.display = 'none';
        }
    } else {
        viewGridBtn.classList.remove('active');
        viewTableBtn.classList.add('active');
        if (allApplications.length > 0) {
            gridEl.style.display = 'none';
            tableEl.style.display = 'block';
        }
    }
}

async function loadApplications() {
    const loadingState = document.getElementById('loadingState');
    const applicationsGrid = document.getElementById('applicationsGrid');
    const applicationsTable = document.getElementById('applicationsTable');
    const emptyState = document.getElementById('emptyState');

    loadingState.style.display = 'block';
    applicationsGrid.style.display = 'none';
    applicationsTable.style.display = 'none';
    emptyState.style.display = 'none';

    try {
        allApplications = await api.getApplications();
        updateStats(allApplications);
        displayApplications(allApplications);
    } catch (error) {
        console.error('Error loading applications:', error);
        loadingState.innerHTML = `
            <p style="color: var(--color-danger); font-weight: 600;">Error loading applications</p>
            <p style="color: var(--color-text-muted); margin-top: 1rem;">${error.message}</p>
        `;
    }
}

function updateStats(apps) {
    const total = apps.length;
    const approved = apps.filter(a => a.recommendation === 'approve').length; // Assuming backend sends recommendation in list
    // Note: Backend might not send recommendation in list view, might need detail fetch or update API.
    // Fallback: If status is 'evaluated', count based on implicit logic or mock for now if not available.
    // Actually, let's use status.
    const pending = apps.filter(a => a.status !== 'evaluated').length;

    // For approved/rejected, we might need to check if we have that data. 
    // If not in listing, we might just show Evaluated vs Pending.
    // But let's assume we can get it or just show Evaluated count.

    // Let's refine:
    const evaluated = apps.filter(a => a.status === 'evaluated');
    // We'll mock the approved/rejected split for listing stats if data missing, 
    // OR we relies on the API updating to send this. 
    // For now, let's just count evaluated.

    document.getElementById('totalApps').textContent = total;
    document.getElementById('pendingApps').textContent = pending;

    // Optimization: Since standard list API might not have recommendation, 
    // we'll just show "-" for strictly Approved/Rejected unless we have the data.
    // Check first app to see structure
    if (apps.length > 0 && apps[0].recommendation) {
        document.getElementById('approvedApps').textContent = apps.filter(a => a.recommendation === 'approve').length;
        document.getElementById('rejectedApps').textContent = apps.filter(a => a.recommendation === 'reject').length;
    } else {
        document.getElementById('approvedApps').textContent = '-';
        document.getElementById('rejectedApps').textContent = '-';
        // Hint user that they are just 'Evaluated'
    }
}

function displayApplications(applications) {
    const loadingState = document.getElementById('loadingState');
    const applicationsGrid = document.getElementById('applicationsGrid');
    const applicationsTable = document.getElementById('applicationsTable');
    const emptyState = document.getElementById('emptyState');

    loadingState.style.display = 'none';

    if (applications.length === 0) {
        emptyState.style.display = 'block';
        return;
    }

    if (currentView === 'grid') {
        applicationsGrid.style.display = 'grid';
        applicationsTable.style.display = 'none';
        applicationsGrid.innerHTML = applications.map(app => createApplicationCard(app)).join('');
    } else {
        applicationsGrid.style.display = 'none';
        applicationsTable.style.display = 'block';
        document.getElementById('applicationsTableBody').innerHTML = applications.map(app => createApplicationRow(app)).join('');
    }
}

function createApplicationRow(app) {
    const statusBadge = app.status === 'evaluated'
        ? '<span class="badge badge-success">Evaluated</span>'
        : '<span class="badge" style="background: #E8F4FF; color: #118AB2;">Pending</span>';

    const dateStr = new Date(app.created_at).toLocaleDateString();

    return `
        <tr style="border-bottom: 1px solid var(--color-border);">
            <td style="padding: 1rem; font-weight: 600;">${app.applicant_id || app.id}</td>
            <td style="padding: 1rem; color: var(--color-text-muted);">${dateStr}</td>
            <td style="padding: 1rem;">${app.business_type}</td>
            <td style="padding: 1rem;">₹${formatNumber(app.annual_revenue)}</td>
            <td style="padding: 1rem;">₹${formatNumber(app.loan_amount_requested)}</td>
            <td style="padding: 1rem; font-weight: 700;">${app.credit_score}</td>
            <td style="padding: 1rem;">${statusBadge}</td>
            <td style="padding: 1rem;">
                ${app.status === 'evaluated'
            ? `<button class="btn btn-sm btn-outline" onclick="viewResults(${app.id})">View Result</button>`
            : `<button class="btn btn-sm btn-lime" onclick="evaluateApplication(${app.id})">Evaluate</button>`
        }
            </td>
        </tr>
    `;
}

function createApplicationCard(app) {
    const statusBadge = app.status === 'evaluated'
        ? '<span class="badge badge-success">Evaluated</span>'
        : '<span class="badge" style="background: #E8F4FF; color: #118AB2;">Pending</span>';

    const actionButton = app.status === 'evaluated'
        ? `<button class="btn btn-primary" onclick="viewResults(${app.id})" style="width: 100%;">
                View Results
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
            </button>`
        : `<button class="btn btn-lime" onclick="evaluateApplication(${app.id})" style="width: 100%;">
                Evaluate Now
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
            </button>`;

    return `
        <div class="card" style="position: relative;">
            <div style="position: absolute; top: 2rem; right: 2rem;">
                ${statusBadge}
            </div>
            
            <div style="margin-bottom: 2rem;">
                <h3 style="font-size: 1.75rem; font-weight: 800; margin-bottom: 0.5rem; color: var(--color-text-primary);">
                    ${app.applicant_id || `APP-${app.id}`}
                </h3>
                <p style="color: var(--color-text-muted); font-size: 0.9rem;">
                    Submitted ${new Date(app.created_at).toLocaleDateString()}
                </p>
            </div>
            
            <div style="display: grid; gap: 1rem; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--color-bg-secondary); border-radius: var(--radius-md);">
                    <span style="color: var(--color-text-muted); font-size: 0.875rem; font-weight: 600;">Business Type</span>
                    <span style="font-weight: 700; color: var(--color-text-primary);">${app.business_type}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--color-bg-secondary); border-radius: var(--radius-md);">
                    <span style="color: var(--color-text-muted); font-size: 0.875rem; font-weight: 600;">Credit Score</span>
                    <span style="font-weight: 700; color: var(--color-text-primary);">${app.credit_score}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--color-bg-secondary); border-radius: var(--radius-md);">
                    <span style="color: var(--color-text-muted); font-size: 0.875rem; font-weight: 600;">Loan Amount</span>
                    <span style="font-weight: 700; color: var(--color-text-primary);">₹${formatNumber(app.loan_amount_requested)}</span>
                </div>
            </div>
            
            ${actionButton}
        </div>
    `;
}

function filterApplications() {
    const statusFilter = document.getElementById('statusFilter');
    const filterValue = statusFilter.value;

    if (filterValue === '') {
        displayApplications(allApplications);
    } else {
        const filtered = allApplications.filter(app => app.status === filterValue);
        displayApplications(filtered);
    }
}

async function evaluateApplication(appId) {
    if (!confirm('Start AI evaluation for this application?')) return;

    try {
        const evaluation = await api.evaluateApplication(appId);
        alert('Evaluation complete! Redirecting to results...');
        window.location.href = `evaluation.html?id=${evaluation.id}`;
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function viewResults(appId) {
    api.getEvaluationByApplication(appId)
        .then(evaluation => {
            if (evaluation) {
                window.location.href = `evaluation.html?id=${evaluation.id}`;
            }
        })
        .catch(error => {
            alert(`Error: ${error.message}`);
        });
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num);
}
