import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, Search, Filter, TrendingUp, TrendingDown, CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react';
import axios from 'axios';
import './UnderwriterDashboard.css';

export default function UnderwriterDashboard() {
    const { user, logout } = useAuth();
    const [applications, setApplications] = useState([]);
    const [selectedApp, setSelectedApp] = useState(null);
    const [overrideReasoning, setOverrideReasoning] = useState('');
    const [showOverrideModal, setShowOverrideModal] = useState(false);
    const [pendingAction, setPendingAction] = useState(null);
    const [filterTier, setFilterTier] = useState('all');

    // Mock data for demonstration
    useEffect(() => {
        // In production, fetch from /api/v1/applications?status=pending
        setApplications([
            {
                id: '1',
                applicant_id: 'APP-2024-001',
                applicant_name: 'Jane Doe',
                tier: 'Review',
                risk_score: 0.32,
                confidence_score: 0.85,
                created_at: new Date().toISOString(),
                reason: 'Gray Zone: Review Required',
                factors: [
                    { name: 'Payment History', impact: 'positive', strength: 'high', description: 'Consistent on-time payments for 3 years' },
                    { name: 'Debt-to-Income Ratio', impact: 'negative', strength: 'high', description: 'DTI at 47%, above typical threshold' },
                    { name: 'Employment Stability', impact: 'positive', strength: 'medium', description: '5 years with same employer' }
                ],
                applicant_data: {
                    age: 35,
                    income: 75000,
                    credit_score: 680,
                    business_type: 'Construction',
                    total_debt: 35000
                }
            },
            {
                id: '2',
                applicant_id: 'APP-2024-002',
                applicant_name: 'John Smith',
                tier: 'Approve',
                risk_score: 0.15,
                confidence_score: 0.65,
                created_at: new Date().toISOString(),
                reason: 'Solid Approval',
                factors: [
                    { name: 'Credit Score', impact: 'positive', strength: 'high', description: 'Credit score of 750 is excellent' },
                    { name: 'Recent Inquiries', impact: 'negative', strength: 'low', description: '2 credit inquiries in past 6 months' }
                ],
                applicant_data: {
                    age: 42,
                    income: 95000,
                    credit_score: 750,
                    business_type: 'IT',
                    total_debt: 15000
                }
            }
        ]);
    }, []);

    const getTierBadge = (tier) => {
        const classes = {
            'Approve': 'badge-success',
            'Reject': 'badge-danger',
            'Review': 'badge-warning'
        };
        return <span className={`badge ${classes[tier]}`}>{tier}</span>;
    };

    const getConfidenceLabel = (score) => {
        if (score > 0.7) return 'High';
        if (score > 0.4) return 'Medium';
        return 'Low';
    };

    const handleAction = (action) => {
        setPendingAction(action);
        setShowOverrideModal(true);
    };

    const submitOverride = async () => {
        if (overrideReasoning.length < 20) {
            alert('Override reasoning must be at least 20 characters');
            return;
        }

        try {
            await axios.post('/api/v1/override', {
                decision_id: selectedApp.id,
                new_tier: pendingAction,
                justification: overrideReasoning
            });

            // Remove from queue
            setApplications(apps => apps.filter(app => app.id !== selectedApp.id));
            setSelectedApp(null);
            setShowOverrideModal(false);
            setOverrideReasoning('');
            alert('Decision submitted successfully');
        } catch (error) {
            console.error('Override failed:', error);
            alert('Failed to submit decision. Please try again.');
        }
    };

    const filteredApps = filterTier === 'all'
        ? applications
        : applications.filter(app => app.tier === filterTier);

    const queueSummary = {
        approve: applications.filter(a => a.tier === 'Approve').length,
        review: applications.filter(a => a.tier === 'Review').length,
        reject: applications.filter(a => a.tier === 'Reject').length
    };

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="container">
                    <div className="header-content">
                        <div>
                            <h1>Underwriter Cockpit</h1>
                            <p>Welcome, {user.username}</p>
                        </div>
                        <button onClick={logout} className="btn btn-outline">
                            <LogOut size={18} />
                            Sign Out
                        </button>
                    </div>
                </div>
            </header>

            <main className="container" style={{ marginTop: '2rem' }}>
                {!selectedApp ? (
                    <>
                        {/* Queue Summary */}
                        <div className="queue-summary">
                            <div className="summary-card" onClick={() => setFilterTier('Approve')}>
                                <div className="summary-icon approve">
                                    <CheckCircle size={24} />
                                </div>
                                <div className="summary-data">
                                    <div className="summary-count">{queueSummary.approve}</div>
                                    <div className="summary-label">Approve</div>
                                </div>
                            </div>
                            <div className="summary-card" onClick={() => setFilterTier('Review')}>
                                <div className="summary-icon review">
                                    <AlertCircle size={24} />
                                </div>
                                <div className="summary-data">
                                    <div className="summary-count">{queueSummary.review}</div>
                                    <div className="summary-label">Review</div>
                                </div>
                            </div>
                            <div className="summary-card" onClick={() => setFilterTier('Reject')}>
                                <div className="summary-icon reject">
                                    <XCircle size={24} />
                                </div>
                                <div className="summary-data">
                                    <div className="summary-count">{queueSummary.reject}</div>
                                    <div className="summary-label">Reject</div>
                                </div>
                            </div>
                        </div>

                        {/* Controls */}
                        <div className="cockpit-controls">
                            <div className="search-box">
                                <Search size={20} />
                                <input type="text" placeholder="Search applications..." />
                            </div>
                            <button className="btn btn-outline" onClick={() => setFilterTier('all')}>
                                <Filter size={18} />
                                {filterTier !== 'all' ? `Filtered: ${filterTier}` : 'All Cases'}
                            </button>
                        </div>

                        {/* Application List */}
                        <div className="applications-grid">
                            {filteredApps.map(app => (
                                <div key={app.id} className="card application-card" onClick={() => setSelectedApp(app)}>
                                    <div className="app-header">
                                        <div>
                                            <h3>{app.applicant_id}</h3>
                                            <p className="app-name">{app.applicant_name}</p>
                                        </div>
                                        {getTierBadge(app.tier)}
                                    </div>

                                    <div className="app-metrics">
                                        <div className="metric">
                                            <span className="metric-label">PD</span>
                                            <span className="metric-value">{(app.risk_score * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="metric">
                                            <span className="metric-label">Confidence</span>
                                            <span className="metric-value">{getConfidenceLabel(app.confidence_score)}</span>
                                        </div>
                                    </div>

                                    <div className="app-preview">
                                        {app.factors && app.factors.slice(0, 2).map((factor, idx) => (
                                            <div key={idx} className="factor-preview">
                                                {factor.impact === 'positive' ?
                                                    <TrendingUp size={14} className="factor-icon positive" /> :
                                                    <TrendingDown size={14} className="factor-icon negative" />
                                                }
                                                <span>{factor.name}</span>
                                            </div>
                                        ))}
                                    </div>

                                    <button className="btn btn-primary btn-sm">View Details →</button>
                                </div>
                            ))}
                        </div>

                        {filteredApps.length === 0 && (
                            <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                                <p style={{ color: 'var(--color-gray-600)' }}>No applications in this category</p>
                            </div>
                        )}
                    </>
                ) : (
                    /* Detail View */
                    <div className="detail-view">
                        <button onClick={() => setSelectedApp(null)} className="btn btn-outline" style={{ marginBottom: '1rem' }}>
                            ← Back to Queue
                        </button>

                        <div className="detail-grid">
                            {/* Left Column */}
                            <div className="detail-column">
                                <div className="card">
                                    <h3>Applicant Information</h3>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="info-label">Name</span>
                                            <span className="info-value">{selectedApp.applicant_name}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Age</span>
                                            <span className="info-value">{selectedApp.applicant_data.age}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Income</span>
                                            <span className="info-value">${selectedApp.applicant_data.income.toLocaleString()}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Credit Score</span>
                                            <span className="info-value">{selectedApp.applicant_data.credit_score}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Business Type</span>
                                            <span className="info-value">{selectedApp.applicant_data.business_type}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Total Debt</span>
                                            <span className="info-value">${selectedApp.applicant_data.total_debt.toLocaleString()}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="card">
                                    <h3>Documents</h3>
                                    <div className="document-list">
                                        <div className="document-item">
                                            <CheckCircle size={16} className="doc-icon" />
                                            <FileText size={16} />
                                            <span>Bank Statement</span>
                                        </div>
                                        <div className="document-item">
                                            <CheckCircle size={16} className="doc-icon" />
                                            <FileText size={16} />
                                            <span>Tax Return (2023)</span>
                                        </div>
                                        <div className="document-item">
                                            <CheckCircle size={16} className="doc-icon" />
                                            <FileText size={16} />
                                            <span>Pay Stubs (3 months)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Right Column */}
                            <div className="detail-column">
                                <div className="card">
                                    <h3>AI Recommendation</h3>
                                    <div className="recommendation-header">
                                        {getTierBadge(selectedApp.tier)}
                                        <div className="pd-display">
                                            <span className="pd-label">PD:</span>
                                            <span className="pd-value">{(selectedApp.risk_score * 100).toFixed(1)}%</span>
                                            <span className="pd-range">(Range: {((selectedApp.risk_score - 0.1) * 100).toFixed(1)}%-{((selectedApp.risk_score + 0.1) * 100).toFixed(1)}%)</span>
                                        </div>
                                        <div className="confidence-display">
                                            Confidence: <strong>{getConfidenceLabel(selectedApp.confidence_score)}</strong>
                                        </div>
                                    </div>

                                    <h4 style={{ marginTop: '1.5rem' }}>Key Drivers</h4>
                                    <div className="factors-list">
                                        {selectedApp.factors.map((factor, idx) => (
                                            <div key={idx} className="factor-detail">
                                                <div className="factor-header-detail">
                                                    {factor.impact === 'positive' ?
                                                        <TrendingUp size={18} className="factor-icon positive" /> :
                                                        <TrendingDown size={18} className="factor-icon negative" />
                                                    }
                                                    <div>
                                                        <div className="factor-name">{factor.name}</div>
                                                        <div className="factor-strength">
                                                            {factor.strength === 'high' ? 'Strong influence' :
                                                                factor.strength === 'medium' ? 'Moderate influence' : 'Minor influence'}
                                                        </div>
                                                    </div>
                                                </div>
                                                <p className="factor-description">{factor.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="card">
                                    <h3>Underwriter Actions</h3>
                                    <div className="action-buttons">
                                        <button onClick={() => handleAction('Approve')} className="btn btn-success">
                                            <CheckCircle size={18} />
                                            Approve
                                        </button>
                                        <button onClick={() => handleAction('Reject')} className="btn btn-danger">
                                            <XCircle size={18} />
                                            Reject
                                        </button>
                                        <button onClick={() => handleAction('Request Info')} className="btn btn-outline">
                                            <AlertCircle size={18} />
                                            Request More Info
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Override Modal */}
                {showOverrideModal && (
                    <div className="modal-overlay" onClick={() => setShowOverrideModal(false)}>
                        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                            <h2>Override Reasoning Required</h2>
                            <p>Please provide justification for your decision (minimum 20 characters):</p>

                            <textarea
                                value={overrideReasoning}
                                onChange={(e) => setOverrideReasoning(e.target.value)}
                                placeholder="Example: Applicant works in Construction sector. While DTI is elevated, strong payment history and employment stability justify approval with monitoring."
                                rows={6}
                                className="reasoning-textarea"
                            />

                            <div className="char-count">
                                {overrideReasoning.length} / 20 characters minimum
                            </div>

                            <div className="modal-actions">
                                <button onClick={() => setShowOverrideModal(false)} className="btn btn-outline">
                                    Cancel
                                </button>
                                <button
                                    onClick={submitOverride}
                                    className="btn btn-primary"
                                    disabled={overrideReasoning.length < 20}
                                >
                                    Submit Decision
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}


