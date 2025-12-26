// Dashboard JavaScript with MindMarket styling

const api = new APIClient();
let allApplications = [];

document.addEventListener('DOMContentLoaded', function () {
    const statusFilter = document.getElementById('statusFilter');
    const refreshBtn = document.getElementById('refreshBtn');

    // Load applications on page load
    loadApplications();

    // Event listeners
    if (statusFilter) {
        statusFilter.addEventListener('change', filterApplications);
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadApplications);
    }
});

async function loadApplications() {
    const loadingState = document.getElementById('loadingState');
    const applicationsGrid = document.getElementById('applicationsGrid');
    const emptyState = document.getElementById('emptyState');

    loadingState.style.display = 'block';
    applicationsGrid.style.display = 'none';
    emptyState.style.display = 'none';

    try {
        allApplications = await api.getApplications();
        displayApplications(allApplications);
    } catch (error) {
        console.error('Error loading applications:', error);
        loadingState.innerHTML = `
            <p style="color: var(--color-danger); font-weight: 600;">Error loading applications</p>
            <p style="color: var(--color-text-muted); margin-top: 1rem;">${error.message}</p>
        `;
    }
}

function displayApplications(applications) {
    const loadingState = document.getElementById('loadingState');
    const applicationsGrid = document.getElementById('applicationsGrid');
    const emptyState = document.getElementById('emptyState');

    loadingState.style.display = 'none';

    if (applications.length === 0) {
        emptyState.style.display = 'block';
        return;
    }

    applicationsGrid.style.display = 'grid';
    applicationsGrid.innerHTML = applications.map(app => createApplicationCard(app)).join('');
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
