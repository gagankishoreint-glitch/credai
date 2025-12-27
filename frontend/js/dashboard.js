document.addEventListener('DOMContentLoaded', async function () {
    const tableBody = document.getElementById('applicationsTableBody');
    const statusFilter = document.getElementById('statusFilter');
    const limitFilter = document.getElementById('limitFilter');

    // Initialize
    await loadApplications();

    // Event Listeners
    statusFilter.addEventListener('change', loadApplications);
    limitFilter.addEventListener('change', loadApplications);

    async function loadApplications() {
        const status = statusFilter.value;
        const limit = limitFilter.value; // For now just uses this as limit, pagination later

        // Show loading
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 2rem;">Loading applications...</td></tr>';

        try {
            let url = `/api/applications/?limit=${limit}`;
            if (status) {
                url += `&status=${status}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch applications');

            const applications = await response.json();
            renderTable(applications);

            // Update stats (simple mock for now, actual stats endpoint later)
            updateDashboardStats(applications);

        } catch (error) {
            console.error(error);
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center" style="color: var(--color-danger); padding: 2rem;">Error loading data: ${error.message}</td></tr>`;
        }
    }

    function renderTable(apps) {
        if (apps.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 2rem;">No applications found matching criteria.</td></tr>';
            return;
        }

        tableBody.innerHTML = apps.map(app => {
            const riskScore = app.evaluation ? Math.round(app.evaluation.risk_score) : '--';
            const riskBadge = getRiskBadge(app.evaluation?.recommendation);
            const statusBadge = getStatusBadge(app.status);

            return `
            <tr>
                <td style="font-family: monospace; font-weight: 600;">${app.applicant_id}</td>
                <td>
                    <div style="font-weight: 500;">${app.business_type}</div>
                    <div style="font-size: 0.8rem; color: var(--color-text-muted);">${app.years_in_operation} yrs • ₹${formatCompact(app.annual_revenue)}</div>
                </td>
                <td>₹${formatNumber(app.loan_amount_requested)}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-weight: 700;">${riskScore}</span>
                        ${riskBadge}
                    </div>
                </td>
                <td>${statusBadge}</td>
                <td style="font-size: 0.85rem; color: var(--color-text-muted);">
                    ${new Date(app.created_at).toLocaleDateString()}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="viewDetails(${app.id})">Review</button>
                </td>
            </tr>
            `;
        }).join('');
    }

    function getRiskBadge(recommendation) {
        if (!recommendation) return '<span class="status-badge" style="background: #f3f4f6; color: #6b7280;">Pending</span>';

        if (recommendation === 'approve') return '<span class="status-badge status-success">Low Risk</span>';
        if (recommendation === 'reject') return '<span class="status-badge status-high-risk">High Risk</span>';
        return '<span class="status-badge status-warning">Medium</span>';
    }

    function getStatusBadge(status) {
        if (status === 'pending') return '<span class="status-badge" style="background: #e5e7eb; color: #374151;">Pending</span>';
        if (status === 'evaluated') return '<span class="status-badge" style="background: #dbeafe; color: #1e40af;">Evaluated</span>';
        if (status === 'approved') return '<span class="status-badge status-success">Approved</span>';
        if (status === 'rejected') return '<span class="status-badge status-high-risk">Rejected</span>';
        return `<span class="status-badge">${status}</span>`;
    }

    function formatNumber(num) {
        return new Intl.NumberFormat('en-IN').format(num);
    }

    function formatCompact(num) {
        return new Intl.NumberFormat('en-IN', { notation: "compact", compactDisplay: "short" }).format(num);
    }

    // Quick Stats Update (Client-side calculation for now)
    function updateDashboardStats(apps) {
        const total = apps.length;
        const approved = apps.filter(a => a.status === 'approved' || (a.evaluation && a.evaluation.recommendation === 'approve')).length;
        const rejected = apps.filter(a => a.status === 'rejected' || (a.evaluation && a.evaluation.recommendation === 'reject')).length;
        const pending = apps.filter(a => a.status === 'pending').length;

        document.getElementById('statTotal').innerText = total;
        document.getElementById('statApproved').innerText = approved;
        document.getElementById('statRejected').innerText = rejected; // or Warning/Review count
        document.getElementById('statPending').innerText = pending;
    }
});

// Exposed for button click
function viewDetails(id) {
    // For now simple alert or redirect. Ideally a drawer.
    // Let's redirect to evaluation page for now, or trigger a drawer if we build it.
    // The requirement says "Detail Drawer". For this step, let's redirect to 'dashboard-detail.html' (to be made) or re-use evaluation.
    window.location.href = `evaluation.html?id=${id}`;
    // Ideally evaluation.html needs to support viewing purely by ID even if we are 'admin'. 
    // Currently evaluation.html does fetch by ID so it works.
}
