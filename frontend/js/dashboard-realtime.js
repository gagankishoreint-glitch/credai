// Dashboard Real-Time Updates
// Listens to Firestore for application status changes

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

    // Listen for real-time updates
    const unsubscribe = db.collection('applications')
        .doc(applicationId)
        .onSnapshot((doc) => {
            if (doc.exists) {
                const data = doc.data();
                updateDashboard(data);
            } else {
                console.log('Application not found');
            }
        }, (error) => {
            console.error('Error listening to application:', error);
        });

    function updateDashboard(data) {
        // Update application number
        const appNumber = document.querySelector('h3');
        if (appNumber) {
            appNumber.textContent = `Loan Application #${data.businessName.substring(0, 5).toUpperCase()}`;
        }

        // Update status badge
        const statusBadge = document.querySelector('[style*="background: rgba(90, 69, 255"]');
        if (statusBadge) {
            const statusMap = {
                'received': { text: 'Received', color: '#10B981' },
                'analyzing': { text: 'Analyzing', color: '#5A45FF' },
                'decision': { text: 'Decision Ready', color: '#F59E0B' }
            };

            const status = statusMap[data.status] || statusMap['received'];
            statusBadge.textContent = status.text;
            statusBadge.style.background = `rgba(${hexToRgb(status.color)}, 0.1)`;
            statusBadge.style.color = status.color;
        }

        // Update progress tracker
        updateProgressTracker(data.status);

        // Update credit score if available
        if (data.aiScore) {
            const scoreElement = document.querySelector('h2[style*="font-size: 3.5rem"]');
            if (scoreElement) {
                scoreElement.textContent = data.aiScore;
            }

            // Update risk text
            const riskText = document.querySelector('p[style*="color: var(--color-text-secondary)"]');
            if (riskText && data.riskLevel) {
                const riskMap = {
                    'low': 'Low Risk - Good Standing',
                    'medium': 'Medium Risk - Review Required',
                    'high': 'High Risk - Additional Info Needed'
                };
                riskText.textContent = riskMap[data.riskLevel] || 'Pending Analysis';
            }
        }

        // Update next steps text
        const nextStepsText = document.querySelector('[style*="background: var(--color-bg-secondary)"] p');
        if (nextStepsText) {
            if (data.status === 'decision') {
                nextStepsText.textContent = `Your application has been processed! Decision: ${data.decision.toUpperCase()}. Check your email for detailed results.`;
            } else if (data.status === 'analyzing') {
                nextStepsText.textContent = 'Our AI models are currently analyzing your financial inputs. This typically takes 2-5 minutes. Real-time updates will appear here.';
            }
        }
    }

    function updateProgressTracker(status) {
        // Status mapping to step numbers
        const stepMap = {
            'received': 1,
            'analyzing': 2,
            'decision': 3
        };

        const currentStep = stepMap[status] || 1;

        // Update each step indicator (simplified - you'd need to target specific elements)
        console.log(`Current step: ${currentStep}`);
    }

    function hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ?
            `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` :
            '90, 69, 255';
    }
});
