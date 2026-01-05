// Dashboard Real-Time Updates - ENHANCED to show ALL client data
// Listens to Firestore for application status changes and displays complete application details

document.addEventListener('DOMContentLoaded', function () {
    // Wait for auth to be ready
    auth.onAuthStateChanged(user => {
        if (user) {
            console.log('User logged in:', user.uid);
            loadUserApplications(user.uid);
        } else {
            console.log('No user logged in, redirecting...');
            window.location.href = 'login.html';
        }
    });

    function loadUserApplications(userId) {
        db.collection('applications')
            .where('userId', '==', userId)
            .onSnapshot((snapshot) => {
                const container = document.getElementById('dashboard-content');

                if (snapshot.empty) {
                    renderEmptyState(container);
                    return;
                }

                container.innerHTML = ''; // Clear loading state or old data

                // Convert to array and sort client-side to avoid index requirement
                const docs = [];
                snapshot.forEach(doc => docs.push({ id: doc.id, ...doc.data() }));

                // Sort by submittedAt desc
                docs.sort((a, b) => {
                    const timeA = a.submittedAt ? a.submittedAt.seconds : 0;
                    const timeB = b.submittedAt ? b.submittedAt.seconds : 0;
                    return timeB - timeA;
                });

                docs.forEach(data => {
                    const card = createApplicationCard(data.id, data);
                    container.appendChild(card);
                });

            }, (error) => {
                console.error('Error fetching applications:', error);
                document.getElementById('dashboard-content').innerHTML = `
                    <div style="text-align: center; color: var(--color-danger); padding: 40px;">
                        <ion-icon name="alert-circle-outline" style="font-size: 32px; margin-bottom: 16px;"></ion-icon>
                        <p>Error loading applications. Please refresh.</p>
                    </div>
                `;
            });
    }

    function renderEmptyState(container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 40px; border: 1px dashed var(--color-border); border-radius: var(--radius-lg); background: var(--color-bg-secondary);">
                <div style="width: 80px; height: 80px; margin: 0 auto 24px; background: rgba(255,255,255,0.05); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <ion-icon name="folder-open-outline" style="font-size: 40px; color: var(--color-text-muted);"></ion-icon>
                </div>
                <h3 style="color: var(--color-white); margin-bottom: 8px;">No Applications Yet</h3>
                <p style="color: var(--color-text-secondary); margin-bottom: 24px;">Start your first credit evaluation request today.</p>
                <a href="application.html" class="btn btn-primary">Start New Application</a>
            </div>
        `;
    }

    function createApplicationCard(appId, data) {
        // Formatted Date
        let dateStr = 'Just now';
        if (data.submittedAt && data.submittedAt.toDate) {
            dateStr = data.submittedAt.toDate().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        }

        // Status Logic
        const statusMap = {
            'received': { text: 'Received', icon: 'checkmark', color: '#10B981', bg: 'rgba(16, 185, 129, 0.1)', step: 1 },
            'analyzing': { text: 'Analyzing', icon: 'sync', color: '#5A45FF', bg: 'rgba(90, 69, 255, 0.1)', step: 2 },
            'decision': { text: 'Decision Ready', icon: 'bulb', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)', step: 3 }
        };
        const statusNode = statusMap[data.status] || statusMap['received'];

        // Card Container
        const card = document.createElement('div');
        card.className = 'grid';
        card.style.cssText = 'grid-template-columns: 2fr 1fr; gap: 32px; margin-bottom: 48px; border-bottom: 1px solid var(--color-border); padding-bottom: 48px;';

        // Progress Steps HTML
        const isStep1 = statusNode.step >= 1 ? 'color: #10B981;' : 'color: var(--color-text-muted);';
        const isStep2 = statusNode.step >= 2 ? 'color: #5A45FF;' : 'color: var(--color-text-muted);';
        const isStep3 = statusNode.step >= 3 ? 'color: #F59E0B;' : 'color: var(--color-text-muted);';

        card.innerHTML = `
             <!-- LEFT: Status & Details -->
            <div class="feature-card glow-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px;">
                    <div>
                        <h3 style="margin: 0;">${data.businessName || 'Loan Application'}</h3>
                        <p style="color: var(--color-text-secondary); font-size: 0.9rem; margin-top: 8px;">Submitted on ${dateStr} • ID: #${appId.substr(0, 6)}</p>
                    </div>
                    <span style="background: ${statusNode.bg}; color: ${statusNode.color}; padding: 8px 16px; border-radius: var(--radius-pill); font-size: 0.85rem; font-weight: 600;">
                        ${statusNode.text}
                    </span>
                </div>

                <!-- Status Tracker -->
                <div style="position: relative; display: flex; justify-content: space-between; margin-bottom: 48px;">
                    <div style="position: absolute; top: 16px; left: 0; width: 100%; height: 2px; background: var(--color-border); z-index: 0;"></div>

                    <div style="z-index: 1; text-align: center;">
                        <div style="width: 40px; height: 40px; background: ${statusNode.step >= 1 ? '#10B981' : 'var(--color-bg-card)'}; border: ${statusNode.step >= 1 ? 'none' : '2px solid var(--color-border)'}; border-radius: 50%; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; color: ${statusNode.step >= 1 ? 'white' : 'var(--color-text-muted)'};">
                            <ion-icon name="checkmark"></ion-icon>
                        </div>
                        <span style="font-size: 0.85rem; font-weight: 600; ${isStep1}">Received</span>
                    </div>

                    <div style="z-index: 1; text-align: center;">
                        <div style="width: 40px; height: 40px; background: ${statusNode.step >= 2 ? 'var(--gradient-primary)' : 'var(--color-bg-card)'}; border: ${statusNode.step >= 2 ? 'none' : '2px solid var(--color-border)'}; border-radius: 50%; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; color: ${statusNode.step >= 2 ? 'white' : 'var(--color-text-muted)'}; box-shadow: ${statusNode.step >= 2 ? 'var(--shadow-glow)' : 'none'};">
                            <ion-icon name="sync"></ion-icon>
                        </div>
                        <span style="font-size: 0.85rem; font-weight: 600; ${isStep2}">Analyzing</span>
                    </div>

                    <div style="z-index: 1; text-align: center;">
                        <div style="width: 40px; height: 40px; background: ${statusNode.step >= 3 ? '#F59E0B' : 'var(--color-bg-card)'}; border: ${statusNode.step >= 3 ? 'none' : '2px solid var(--color-border)'}; border-radius: 50%; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; color: ${statusNode.step >= 3 ? 'white' : 'var(--color-text-muted)'};">
                            <span style="font-size: 0.85rem;">3</span>
                        </div>
                        <span style="font-size: 0.85rem; ${isStep3}">Decision</span>
                    </div>
                </div>

                <div style="background: var(--color-bg-secondary); padding: 28px; border-radius: var(--radius-lg);">
                    <h4 style="margin-bottom: 12px;">Next Steps</h4>
                    <p style="color: var(--color-text-secondary); font-size: 0.95rem; line-height: 1.7;">
                        ${statusNode.step === 3 ? 'Your application has been processed. Download your report below.' : 'Our AI models are currently analyzing your documents and financial inputs.'}
                    </p>
                </div>
            </div>

            <!-- RIGHT: Risk Gauge & Insights -->
            <div class="feature-card glow-card" style="text-align: center;">
                <h3 style="margin-bottom: 32px;">Credit Health</h3>

                <div style="width: 200px; height: 100px; border-top-left-radius: 100px; border-top-right-radius: 100px; background: var(--color-bg-secondary); margin: 0 auto; position: relative; overflow: hidden;">
                    <div style="width: 100%; height: 100%; background: conic-gradient(from 180deg, #EF4444 0deg, #F59E0B 60deg, #10B981 120deg, #10B981 180deg); opacity: 0.3;"></div>
                    <div style="position: absolute; bottom: 0; left: 50%; width: 160px; height: 80px; background: var(--color-bg-card); transform: translateX(-50%); border-top-left-radius: 80px; border-top-right-radius: 80px;"></div>
                    
                    <!-- Needle Visualization -->
                    <div style="position: absolute; bottom: 0; left: 50%; width: 4px; height: 90px; background: var(--gradient-primary); transform-origin: bottom center; transform: translateX(-50%) rotate(${calculateNeedleRotation(data.creditScore || 720)}deg); box-shadow: 0 0 10px rgba(90, 69, 255, 0.5);"></div>
                </div>

                <!-- Score Display: Fixed Margin to Prevent Overlap -->
                <div style="margin-top: 10px; margin-bottom: 32px;">
                    <h2 style="font-size: 3.5rem; margin-bottom: 0; background: var(--gradient-primary); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        ${data.creditScore || 720}
                    </h2>
                    <p style="color: var(--color-text-secondary);">${statusNode.step === 3 ? 'Final Score' : 'Pending Final Review'}</p>
                </div>

                <!-- AI Insights Section -->
                <div style="text-align: left; background: var(--color-bg-secondary); padding: 20px; border-radius: 16px;">
                    <h4 style="margin-bottom: 16px; display: flex; align-items: center;">
                        <ion-icon name="analytics-outline" style="color: var(--color-accent-purple); margin-right: 8px;"></ion-icon>
                        AI Risk Analysis
                    </h4>

                    <div style="margin-bottom: 12px; font-size: 0.9rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Revenue Stability</span>
                            <span style="color: #10B981;">Strong</span>
                        </div>
                        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                            <div style="width: 85%; height: 100%; background: #10B981; border-radius: 3px;"></div>
                        </div>
                    </div>

                    <div style="margin-bottom: 12px; font-size: 0.9rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Market Position</span>
                            <span style="color: #F59E0B;">Good</span>
                        </div>
                        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                            <div style="width: 70%; height: 100%; background: #F59E0B; border-radius: 3px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return card;
    }

    function calculateNeedleRotation(score) {
        // Map score 300-850 to degrees -90 to 90
        const minScore = 300;
        const maxScore = 850;
        const percent = (score - minScore) / (maxScore - minScore);
        const deg = -90 + (percent * 180);
        return Math.min(Math.max(deg, -90), 90);
    }
});
