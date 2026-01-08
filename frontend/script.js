document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('credit-form');
    const submitBtn = document.getElementById('submit-btn');
    const errorMessage = document.getElementById('error-message');

    // AUTH LOGIC (Global)
    checkAuth();

    function checkAuth() {
        const token = localStorage.getItem('auth_token');
        const navDashboard = document.getElementById('nav-dashboard');
        const navSignIn = document.getElementById('nav-signin');
        const navSignOut = document.getElementById('nav-signout');

        if (token) {
            // Logged In
            if (navDashboard) navDashboard.classList.remove('hidden');
            if (navSignIn) navSignIn.classList.add('hidden');
            if (navSignOut) {
                navSignOut.classList.remove('hidden');
                navSignOut.addEventListener('click', (e) => {
                    e.preventDefault();
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user_role');
                    window.location.href = 'index.html';
                });
            }
        } else {
            // Guest
            if (navDashboard) navDashboard.classList.add('hidden');
            if (navSignIn) navSignIn.classList.remove('hidden');
            if (navSignOut) navSignOut.classList.add('hidden');
        }
    }

    // Result Elements
    // View Containers
    const appView = document.getElementById('application-view');
    const resView = document.getElementById('results-view');
    const resetBtn = document.getElementById('reset-btn');

    // New Result Elements
    const riskBar = document.getElementById('risk-bar');
    const riskLabel = document.getElementById('risk-label');
    const riskRange = document.getElementById('risk-range');
    const factorsContainer = document.getElementById('factors-container');
    const statusBanner = document.getElementById('status-banner');
    const statusTitle = document.getElementById('status-title');
    const statusDesc = document.getElementById('status-desc');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        setLoading(true);
        errorMessage.classList.add('hidden');

        try {
            const formData = new FormData(form);
            const payload = {
                applicant_id: formData.get('applicant_id') || undefined,
                business_type: formData.get('business_type') || "Other",
                age: parseInt(formData.get('age')) || 18,
                credit_score: parseInt(formData.get('credit_score')) || 300,
                annual_income: parseFloat(formData.get('annual_income')) || 0,
                total_debt: parseFloat(formData.get('total_debt')) || 0,
                monthly_debt_obligations: formData.get('monthly_debt_obligations') ? parseFloat(formData.get('monthly_debt_obligations')) : 0,
                assets_total: formData.get('assets_total') ? parseFloat(formData.get('assets_total')) : 0.0
            };

            console.log("Submitting Payload:", payload);

            const response = await fetch('http://localhost:8000/api/v1/decide', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                mode: 'cors', // Explicitly request CORS
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();

            // Artificial delay for "analyzing" feel
            setTimeout(() => {
                displayResult(data);
            }, 800);

        } catch (error) {
            console.error('Submission Error:', error);
            // Show detailed error if available
            const msg = error.message === 'Failed to fetch'
                ? 'Cannot connect to Server. Is Backend running on port 8000?'
                : (error.message || 'An unexpected error occurred.');

            errorMessage.textContent = msg;
            errorMessage.classList.remove('hidden');
            setLoading(false);
        }
    });

    resetBtn.addEventListener('click', () => {
        // Switch back to form
        resView.classList.add('hidden');
        appView.classList.remove('hidden');
        appView.classList.add('reveal', 'active'); // Re-trigger anim
        setLoading(false);
        form.reset();
        // Scroll top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing Application...';
            submitBtn.style.opacity = '0.7';
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Continue to Documents';
            submitBtn.style.opacity = '1';
        }
    }

    function displayResult(data) {
        // 1. Switch Views
        appView.classList.add('hidden');
        resView.classList.remove('hidden');
        resView.classList.add('reveal', 'active'); // Trigger entry anim
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // 2. Populate Metrics
        const riskPercent = (data.risk_score * 100).toFixed(1);
        riskBar.style.width = `${riskPercent}%`;

        // Update Labels based on risk
        if (data.risk_score < 0.2) {
            riskLabel.textContent = "Low Risk";
            riskLabel.style.color = "#10b981"; // Green
        } else if (data.risk_score > 0.5) {
            riskLabel.textContent = "Higher Risk";
            riskLabel.style.color = "#ef4444"; // Red
        } else {
            riskLabel.textContent = "Moderate Risk";
            riskLabel.style.color = "#f59e0b"; // Orange
        }

        // Mock Range (Data + Uncertainty)
        const lowBound = Math.max(0, (riskPercent - 5)).toFixed(1);
        const highBound = Math.min(100, (parseFloat(riskPercent) + 5)).toFixed(1);
        riskRange.textContent = `${lowBound}% - ${highBound}%`;

        // 3. Populate Factors (New Card Style)
        factorsContainer.innerHTML = '';
        const factors = data.factors || [];

        if (factors.length === 0) {
            factorsContainer.innerHTML = '<p style="color:#64748b;">No strong negative factors found.</p>';
        } else {
            factors.forEach(f => {
                const name = typeof f === 'string' ? f : f.feature;
                // Create Card
                const div = document.createElement('div');
                div.className = 'factor-card';
                div.innerHTML = `
                    <h5><span style="color: #64748b;">&#8627;</span> ${name}</h5>
                    <p>Minor influence</p>
                `;
                factorsContainer.appendChild(div);
            });
        }

        // 4. Status Banner
        statusBanner.className = 'status-banner hidden'; // Reset
        statusBanner.classList.remove('hidden');

        const tier = data.tier.toLowerCase();
        if (tier === 'approve') {
            statusBanner.classList.add('approve');
            statusTitle.textContent = "Preliminary Approval";
            statusDesc.textContent = "Congratulations! Your application shows strong indicators. Final approval pending review.";
        } else if (tier === 'reject') {
            statusBanner.classList.add('reject');
            statusTitle.textContent = "Application Declined";
            statusDesc.textContent = "Based on our analysis, we cannot proceed with this application at this time.";
        } else {
            statusBanner.classList.add('review');
            statusTitle.textContent = "Under Review";
            statusDesc.textContent = "Your application requires further manual assessment by our underwriting team.";
        }
    }
});
// --- SCROLL REVEAL ANIMATION SYSTEM ---
document.addEventListener('DOMContentLoaded', () => {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Target generic reveal elements
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // Auto-reveal hero elements on load (if present)
    setTimeout(() => {
        document.querySelectorAll('.hero-section .reveal').forEach(el => el.classList.add('active'));
    }, 100);
});
