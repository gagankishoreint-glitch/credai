// Dashboard Real-Time Updates - ENHANCED to show ALL client data
// Listens to Firestore for application status changes and displays complete application details

document.addEventListener('DOMContentLoaded', function () {
    // Get application ID from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const applicationId = urlParams.get('id') || localStorage.getItem('applicationId');

    if (!applicationId) {
        console.log('No application ID found');
        document.body.innerHTML = `
            <style>
                body {
                    background: var(--color-bg-primary);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
            </style>
            <div style="text-align: center; padding: 60px 40px; max-width: 600px;">
                <div style="width: 120px; height: 120px; margin: 0 auto 32px; background: linear-gradient(135deg, rgba(90, 69, 255, 0.2), rgba(147, 51, 234, 0.2)); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid var(--color-border);">
                    <ion-icon name="document-text-outline" style="font-size: 64px; color: var(--color-primary);"></ion-icon>
                </div>
                <h2 style="color: var(--color-white); font-size: 2rem; margin: 0 0 16px 0;">No Application Found</h2>
                <p style="color: var(--color-text-secondary); font-size: 1.1rem; line-height: 1.7; margin: 0 0 32px 0;">
                    You haven't submitted a loan application yet. Complete your application to access your personalized dashboard with real-time AI-powered credit analysis.
                </p>
                <a href="application.html" class="btn btn-primary" style="padding: 16px 32px; font-size: 1rem; text-decoration: none; display: inline-block; background: linear-gradient(135deg, #5A45FF, #9333EA); border: none; border-radius: 12px; color: white; font-weight: 600; cursor: pointer; transition: transform 0.2s;">
                    Apply for Credit Evaluation
                </a>
                <div style="margin-top: 40px; padding: 20px; background: rgba(90, 69, 255, 0.1); border-radius: 12px; border-left: 3px solid var(--color-primary);">
                    <p style="color: var(--color-text-secondary); font-size: 0.9rem; margin: 0;">
                        <strong style="color: var(--color-white);">Quick Tip:</strong> Have your business financials and bank statements ready. The application takes about 5 minutes to complete.
                    </p>
                </div>
            </div>
            <script type="module" src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js"></script>
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

        // 4. Update credit score dynamically
        const scoreElement = document.querySelector('h2[style*="font-size: 3.5rem"]');
        if (scoreElement && window.riskCalculator) {
            const calculatedScore = window.riskCalculator.calculateCreditScore(data);
            scoreElement.textContent = calculatedScore;

            // Update needle rotation based on score (300-850 range)
            const needle = document.querySelector('[style*="transform-origin: bottom center"]');
            if (needle) {
                // Map 300-850 to -90deg to +90deg
                const rotation = ((calculatedScore - 300) / 550) * 180 - 90;
                needle.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
            }
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

        // 6. Update AI Risk Analysis Section with Dynamic Calculations
        if (window.riskCalculator) {
            const revenueStability = window.riskCalculator.calculateRevenueStability(data);
            const marketPosition = window.riskCalculator.calculateMarketPosition(data);
            const debtCoverage = window.riskCalculator.calculateDebtServiceCoverage(data);
            const keyFactors = window.riskCalculator.generateKeyFactors(data, revenueStability, marketPosition, debtCoverage);

            // Update the AI Risk Analysis section
            const riskAnalysisContainer = document.querySelector('[style*="text-align: left"][style*="background: var(--color-bg-secondary)"]');
            if (riskAnalysisContainer) {
                riskAnalysisContainer.innerHTML = `
                    <h4 style="margin-bottom: 16px; display: flex; align-items: center;">
                        <ion-icon name="analytics-outline"
                            style="color: var(--color-accent-purple); margin-right: 8px;"></ion-icon>
                        AI Risk Analysis
                    </h4>

                    <div style="margin-bottom: 12px; font-size: 0.9rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Revenue Stability</span>
                            <span style="color: ${revenueStability.color};">${revenueStability.rating}</span>
                        </div>
                        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                            <div style="width: ${revenueStability.percentage}%; height: 100%; background: ${revenueStability.color}; border-radius: 3px;"></div>
                        </div>
                    </div>

                    <div style="margin-bottom: 12px; font-size: 0.9rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Market Position</span>
                            <span style="color: ${marketPosition.color};">${marketPosition.rating}</span>
                        </div>
                        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                            <div style="width: ${marketPosition.percentage}%; height: 100%; background: ${marketPosition.color}; border-radius: 3px;"></div>
                        </div>
                    </div>

                    <div style="font-size: 0.9rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Debt Service Coverage</span>
                            <span style="color: ${debtCoverage.color};">${debtCoverage.rating}</span>
                        </div>
                        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                            <div style="width: ${debtCoverage.percentage}%; height: 100%; background: ${debtCoverage.color}; border-radius: 3px;"></div>
                        </div>
                    </div>
                `;
            }

            // Update Key Factors section
            const keyFactorsContainer = document.querySelector('ul[style*="list-style: none"]');
            if (keyFactorsContainer) {
                keyFactorsContainer.innerHTML = keyFactors.map(factor => {
                    const icon = factor.type === 'positive' ? 'checkmark-circle' : 'alert-circle';
                    const color = factor.type === 'positive' ? '#10B981' : '#F59E0B';
                    return `
                        <li style="margin-bottom: 10px; display: flex; align-items: flex-start;">
                            <ion-icon name="${icon}"
                                style="color: ${color}; margin-right: 8px; margin-top: 2px;"></ion-icon>
                            <span>${factor.text}</span>
                        </li>
                    `;
                }).join('');
            }
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
