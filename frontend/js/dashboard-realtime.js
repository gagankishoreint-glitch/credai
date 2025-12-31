// Dashboard Real-Time Updates - ENHANCED to show ALL client data
// Listens to Firestore for application status changes and displays complete application details

document.addEventListener('DOMContentLoaded', function () {
    // Get application ID from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const applicationId = urlParams.get('id') || localStorage.getItem('applicationId');

    if (!applicationId) {
        console.log('No application ID found');
        document.body.innerHTML = `
            <div style="text-align: center; padding: 100px 20px;">
                <h2>No Application Found</h2>
                <p>Please submit an application first.</p>
                <a href="application.html" class="btn btn-primary">Apply Now</a>
            </div>
        `;
        return;
    }

    console.log('📊 Loading application:', applicationId);

    // Listen for real-time updates
    const unsubscribe = db.collection('applications')
        .doc(applicationId)
        .onSnapshot((doc) => {
            if (doc.exists) {
                const data = doc.data();
                console.log('✅ Application data loaded:', data);
                updateDashboard(data);
            } else {
                console.log('❌ Application not found');
            }
        }, (error) => {
            console.error('❌ Error listening to application:', error);
        });

    function updateDashboard(data) {
        console.log('🔄 Updating dashboard UI with:', data);

        // 1. Update business name in header
        const appHeader = document.querySelector('h3');
        if (appHeader) {
            appHeader.innerHTML = `
                <div style="font-size: 1rem; color: var(--color-text-muted); margin-bottom: 8px;">Loan Application</div>
                <div style="font-size: 1.8rem; color: var(--color-white);">${data.businessName || 'N/A'}</div>
            `;
        }

        // 2. Update submitted date
        const dateTexts = document.querySelectorAll('p[style*="color: var(--color-text-secondary)"]');
        if (dateTexts[0] && data.submittedAt) {
            try {
                const date = data.submittedAt.toDate ? data.submittedAt.toDate() : new Date();
                dateTexts[0].textContent = `Submitted on ${date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`;
            } catch (e) {
                dateTexts[0].textContent = 'Submitted recently';
            }
        }

        // 3. Update status badge
        const statusBadge = document.querySelector('[style*="background: rgba(90, 69, 255"]');
        if (statusBadge) {
            const statusMap = {
                'received': { text: 'Received ✓', color: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' },
                'analyzing': { text: 'Analyzing...', color: '#5A45FF', bg: 'rgba(90, 69, 255, 0.1)' },
                'decision': { text: 'Decision Ready', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' }
            };

            const status = statusMap[data.status] || statusMap['received'];
            statusBadge.textContent = status.text;
            statusBadge.style.background = status.bg;
            statusBadge.style.color = status.color;
        }

        // 4. Update credit score
        const scoreElement = document.querySelector('h2[style*="font-size: 3.5rem"]');
        if (scoreElement) {
            scoreElement.textContent = data.aiScore || data.creditScore || '720';
        }

        // 5. MOST IMPORTANT: Replace "Next Steps" with COMPLETE APPLICATION DATA
        const nextStepsContainer = document.querySelector('[style*="background: var(--color-bg-secondary)"]');
        if (nextStepsContainer) {
            nextStepsContainer.innerHTML = `
                <h4 style="margin-bottom: 24px; font-size: 1.2rem;">📋 Application Details</h4>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;">
                    <!-- Business Info -->
                    <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg); border-left: 3px solid var(--color-accent-purple);">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">BUSINESS NAME</div>
                        <div style="font-weight: 600; font-size: 1.1rem; color: var(--color-white);">${data.businessName || 'N/A'}</div>
                    </div>
                    
                    <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg); border-left: 3px solid #10B981;">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">INDUSTRY</div>
                        <div style="font-weight: 600; font-size: 1.1rem;">${data.industry || 'N/A'}</div>
                    </div>
                    
                    <!-- Financial Info -->
                    <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg); border-left: 3px solid #F59E0B;">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">LOAN AMOUNT REQUESTED</div>
                        <div style="font-weight: 700; font-size: 1.3rem; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">$${(data.loanAmount || 0).toLocaleString()}</div>
                    </div>
                    
                    <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg); border-left: 3px solid #06B6D4;">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">ANNUAL REVENUE</div>
                        <div style="font-weight: 600; font-size: 1.1rem;">$${(data.annualRevenue || 0).toLocaleString()}</div>
                    </div>
                    
                    <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg);">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">YEARS IN BUSINESS</div>
                        <div style="font-weight: 600; font-size: 1.1rem;">${data.yearsInBusiness || 0} years</div>
                    </div>
                    
                    <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg);">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">STATUS</div>
                        <div style="font-weight: 600; font-size: 1.1rem; text-transform: capitalize;">${data.status || 'Processing'}</div>
                    </div>
                </div>

                ${data.operatingExpenses ? `
                    <div style="margin-top: 20px; padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-lg);">
                        <div style="color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px;">OPERATING EXPENSES</div>
                        <div style="font-weight: 600;">$${data.operatingExpenses.toLocaleString()} / month</div>
                    </div>
                ` : ''}

                <div style="margin-top: 24px; padding: 20px; background: linear-gradient(135deg, rgba(90, 69, 255, 0.1), rgba(16, 185, 129, 0.1)); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <ion-icon name="information-circle-outline" style="font-size: 24px; color: var(--color-accent-purple); margin-right: 12px;"></ion-icon>
                        <h5 style="margin: 0;">Next Steps</h5>
                    </div>
                    <p style="color: var(--color-text-secondary); line-height: 1.7; margin: 0;">
                        ${getNextStepsMessage(data)}
                    </p>
                </div>
            `;
        }
    }

    function getNextStepsMessage(data) {
        if (data.status === 'decision') {
            if (data.decision === 'approved') {
                return '🎉 <strong style="color: #10B981;">APPROVED!</strong> Your loan application has been approved. Our team will contact you within 24 hours with the next steps and terms.';
            } else if (data.decision === 'rejected') {
                return '⚠️ Your application was not approved at this time. Please check your registered email for detailed feedback or contact our support team for assistance.';
            }
            return '✅ Your application has been reviewed. Decision details have been sent to your email. All information is displayed above.';
        } else if (data.status === 'analyzing') {
            return '🤖 Our AI models are currently analyzing your business financials and credit profile. This typically takes 2-5 minutes. All updates appear here in real-time - no need to refresh!';
        }
        return '📬 Your application has been received and queued for processing. You\'ll see live status updates here as we progress through each stage. All your submitted data is displayed above for your reference.';
    }
});
