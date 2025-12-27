document.addEventListener('DOMContentLoaded', async function () {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        return;
    }

    try {
        // Fetch metrics
        const response = await fetch('/api/metrics/');
        if (!response.ok) throw new Error('Failed to load metrics');
        const metrics = await response.json();

        renderPerformanceChart(metrics);
        renderFairnessChart(metrics.fairness_approval_rates);
        renderKeyStats(metrics);

    } catch (error) {
        console.error('Error loading benchmarks:', error);
        document.querySelector('.content-section').innerHTML = `
            <div class="container text-center" style="padding: 4rem;">
                <h3 style="color: var(--color-danger);">Unable to load benchmarks</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
});

function renderKeyStats(metrics) {
    // Populate the top stat cards with real model data
    // Metric 1: XGBoost AUC
    updateStatCard(0, (metrics.xgboost.auc * 100).toFixed(1) + '%', 'Model AUC (XGBoost)', 'Predictive Power');

    // Metric 2: XGBoost Accuracy
    updateStatCard(1, (metrics.xgboost.accuracy * 100).toFixed(1) + '%', 'Model Accuracy', 'Correct Predictions');

    // Metric 3: Baseline Comparison (Lift over LogReg)
    const lift = ((metrics.xgboost.auc - metrics.logistic_regression.auc) / metrics.logistic_regression.auc * 100).toFixed(1);
    updateStatCard(2, `+${lift}%`, 'Performance Lift', 'vs. Baseline Model');

    // Metric 4: Fairness Gap (Max - Min approval rate)
    const rates = Object.values(metrics.fairness_approval_rates);
    const maxRate = Math.max(...rates);
    const minRate = Math.min(...rates);
    const gap = ((maxRate - minRate) * 100).toFixed(1);
    updateStatCard(3, `${gap}%`, 'Demographic Gap', 'Approval Disparity');
}

function updateStatCard(index, value, label, subtext) {
    const cards = document.querySelectorAll('.stat-card');
    if (cards[index]) {
        cards[index].querySelector('.stat-value').textContent = value;
        cards[index].querySelector('.stat-label').textContent = label;
        cards[index].querySelector('.stat-change').textContent = subtext;

        // Update icon optionally
        // cards[index].querySelector('.stat-icon').innerHTML = ...
    }
}

function renderPerformanceChart(metrics) {
    const ctx = document.getElementById('performanceChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['AUC Score', 'Accuracy'],
            datasets: [
                {
                    label: 'XGBoost (Current)',
                    data: [metrics.xgboost.auc, metrics.xgboost.accuracy],
                    backgroundColor: '#10b981', // green
                    borderRadius: 6
                },
                {
                    label: 'Logistic Regression (Baseline)',
                    data: [metrics.logistic_regression.auc, metrics.logistic_regression.accuracy],
                    backgroundColor: '#94a3b8', // gray
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Model Performance Comparison' }
            },
            scales: {
                y: { beginAtZero: true, max: 1.0 }
            }
        }
    });
}

function renderFairnessChart(rates) {
    const ctx = document.getElementById('fairnessChart').getContext('2d');

    const labels = Object.keys(rates);
    const values = Object.values(rates).map(v => (v * 100).toFixed(1)); // Convert to %

    // Color code bars: extremely low rates in red, average in blue
    const avg = values.reduce((a, b) => parseFloat(a) + parseFloat(b), 0) / values.length;
    const colors = values.map(v => v < (avg * 0.5) ? '#ef4444' : '#3b82f6');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Approval Rate (%)',
                data: values,
                backgroundColor: colors,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Demographic Parity (Approval Rates by Business Type)' }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Approval Rate %' } }
            }
        }
    });
}
