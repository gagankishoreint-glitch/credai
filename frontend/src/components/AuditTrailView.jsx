import { useState, useEffect } from 'react';
import { FileText, Download, Lock } from 'lucide-react';
import './AuditTrailView.css';

/**
 * AuditTrailView Component
 * Displays immutable audit trail for credit decisions
 * Shows AI decision, underwriter override, and final outcome
 */
export default function AuditTrailView({ applicationId }) {
    const [auditData, setAuditData] = useState(null);

    useEffect(() => {
        // In production: fetch from /api/v1/audit/:applicationId
        setAuditData({
            application_id: 'APP-2024-001',
            applicant_name: 'Jane Doe',
            submitted_at: '2024-01-05T14:23:12Z',

            ai_decision: {
                decision_id: 'dec_a1b2c3d4',
                timestamp: '2024-01-05T14:25:08Z',
                tier: 'Review',
                risk_score: 0.32,
                confidence_score: 0.85,
                factors: [
                    { name: 'Payment History', impact: 0.18, direction: 'positive' },
                    { name: 'Debt-to-Income', impact: -0.22, direction: 'negative' },
                    { name: 'Employment Stability', impact: 0.09, direction: 'positive' }
                ],
                reason_code: 'RC-03',
                model_version: 'v2.1.3'
            },

            override: {
                override_id: 'ovr_x7y8z9',
                timestamp: '2024-01-05T16:45:22Z',
                final_decision: 'Approve',
                underwriter_email: 'john.smith@company.com',
                justification: 'Applicant works in Construction sector with seasonal income variability. While DTI is 47%, strong 5-year payment history and verified assets of $50K provide adequate buffer. Approved with 6-month monitoring.'
            },

            final_outcome: {
                status: 'Approved',
                finalized_at: '2024-01-05T16:45:22Z',
                notification_sent_at: '2024-01-05T16:46:01Z',
                is_locked: true
            },

            audit_log: [
                { timestamp: '2024-01-05T14:23:12Z', action: 'APPLICATION_SUBMITTED', actor: 'applicant_001' },
                { timestamp: '2024-01-05T14:25:08Z', action: 'AI_DECISION_MADE', actor: 'system' },
                { timestamp: '2024-01-05T16:40:15Z', action: 'CASE_ASSIGNED', actor: 'underwriter_john' },
                { timestamp: '2024-01-05T16:45:22Z', action: 'MANUAL_OVERRIDE', actor: 'underwriter_john' },
                { timestamp: '2024-01-05T16:46:01Z', action: 'NOTIFICATION_SENT', actor: 'system' }
            ]
        });
    }, [applicationId]);

    if (!auditData) return <div>Loading...</div>;

    const formatTimestamp = (isoString) => {
        const date = new Date(isoString);
        return date.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    };

    const getTierClass = (tier) => {
        return tier.toLowerCase();
    };

    return (
        <div className="audit-trail-container">
            <header className="audit-header">
                <h1>Audit Trail - {auditData.application_id}</h1>
                <div className="audit-actions">
                    <button className="btn btn-outline">
                        <FileText size={18} />
                        Export PDF
                    </button>
                    <button className="btn btn-outline">
                        <Download size={18} />
                        Export JSON
                    </button>
                </div>
            </header>

            {/* Application Summary */}
            <div className="audit-summary card">
                <div className="summary-row">
                    <span><strong>Applicant:</strong> {auditData.applicant_name}</span>
                    <span><strong>Submitted:</strong> {formatTimestamp(auditData.submitted_at)}</span>
                </div>
                <div className="summary-row">
                    <span className={`final-outcome ${auditData.final_outcome.status.toLowerCase()}`}>
                        <strong>Final Outcome:</strong> {auditData.final_outcome.status.toUpperCase()}
                    </span>
                    <span><strong>Finalized:</strong> {formatTimestamp(auditData.final_outcome.finalized_at)}</span>
                </div>
            </div>

            {/* Decision Timeline */}
            <div className="timeline-container card">
                <h2>Decision Timeline</h2>

                {/* AI Decision */}
                <div className="timeline-event ai-decision">
                    <div className="event-header">
                        <span className="event-icon">🤖</span>
                        <span className="event-title">AI DECISION</span>
                        <span className="event-timestamp">{formatTimestamp(auditData.ai_decision.timestamp)}</span>
                    </div>

                    <div className="event-content">
                        <div className={`decision-badge ${getTierClass(auditData.ai_decision.tier)}`}>
                            {auditData.ai_decision.tier.toUpperCase()}
                        </div>

                        <div className="risk-display">
                            <strong>Risk Score:</strong> {(auditData.ai_decision.risk_score * 100).toFixed(1)}%
                            (Range: {((auditData.ai_decision.risk_score - 0.1) * 100).toFixed(1)}%-
                            {((auditData.ai_decision.risk_score + 0.1) * 100).toFixed(1)}%)
                        </div>

                        <div className="confidence">
                            <strong>Confidence:</strong> High ({(auditData.ai_decision.confidence_score * 100).toFixed(0)}%)
                        </div>

                        <div className="factors">
                            <h4>Key Factors:</h4>
                            {auditData.ai_decision.factors.map((factor, idx) => (
                                <div key={idx} className="factor">
                                    {factor.direction === 'positive' ? '↗️' : '↘️'} {factor.name} ({factor.impact > 0 ? '+' : ''}{factor.impact.toFixed(2)} impact)
                                </div>
                            ))}
                        </div>

                        <div className="metadata">
                            <span>Reason Code: {auditData.ai_decision.reason_code}</span>
                            <span>Model Version: {auditData.ai_decision.model_version}</span>
                            <span>Decision ID: {auditData.ai_decision.decision_id}</span>
                        </div>
                    </div>
                </div>

                <div className="timeline-connector">↓</div>

                {/* Underwriter Override */}
                {auditData.override && (
                    <>
                        <div className="timeline-event override">
                            <div className="event-header">
                                <span className="event-icon">👤</span>
                                <span className="event-title">UNDERWRITER OVERRIDE</span>
                                <span className="event-timestamp">{formatTimestamp(auditData.override.timestamp)}</span>
                            </div>

                            <div className="event-content">
                                <div className={`decision-badge ${getTierClass(auditData.override.final_decision)}`}>
                                    {auditData.override.final_decision.toUpperCase()}
                                </div>

                                <div className="underwriter">
                                    <strong>Underwriter:</strong> {auditData.override.underwriter_email}
                                </div>

                                <div className="justification">
                                    <h4>Justification:</h4>
                                    <p>"{auditData.override.justification}"</p>
                                </div>

                                <div className="metadata">
                                    <span>Override ID: {auditData.override.override_id}</span>
                                </div>
                            </div>
                        </div>

                        <div className="timeline-connector">↓</div>
                    </>
                )}

                {/* Final Outcome */}
                <div className="timeline-event final-outcome">
                    <div className="event-header">
                        <span className="event-icon">✓</span>
                        <span className="event-title">FINAL OUTCOME</span>
                        <span className="event-timestamp">{formatTimestamp(auditData.final_outcome.finalized_at)}</span>
                    </div>

                    <div className="event-content">
                        <div className={`status ${auditData.final_outcome.status.toLowerCase()}`}>
                            {auditData.final_outcome.status.toUpperCase()}
                        </div>

                        {auditData.final_outcome.notification_sent_at && (
                            <div className="notification">
                                <strong>Notification Sent:</strong> {formatTimestamp(auditData.final_outcome.notification_sent_at)}
                            </div>
                        )}

                        {auditData.final_outcome.is_locked && (
                            <div className="immutable-badge">
                                <Lock size={16} />
                                Record Locked (Immutable)
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* System Audit Log */}
            <div className="audit-log card">
                <h2>System Audit Log</h2>
                <table className="audit-log-table">
                    <thead>
                        <tr>
                            <th>Timestamp (UTC)</th>
                            <th>Action</th>
                            <th>Actor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {auditData.audit_log.map((log, idx) => (
                            <tr key={idx}>
                                <td>{formatTimestamp(log.timestamp)}</td>
                                <td>{log.action}</td>
                                <td>{log.actor}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
