import React from 'react';
import '../theme.css';

/**
 * Premium Decision Card Component
 * Demonstrates the calm confidence design system
 */
const PremiumDecisionCard = ({ decision }) => {
    const {
        application_id,
        decision: decisionType,
        risk_level,
        default_probability,
        certainty,
        certainty_description,
        explanation,
        positive_factors = [],
        negative_factors = [],
        recommendations = []
    } = decision;

    // Determine risk level for styling
    const getRiskClass = (level) => {
        if (level?.toLowerCase().includes('low')) return 'low';
        if (level?.toLowerCase().includes('high')) return 'high';
        return 'medium';
    };

    const riskClass = getRiskClass(risk_level);
    const riskPercentage = parseFloat(default_probability) || 0;

    return (
        <div className="card stagger-item" style={{ maxWidth: '800px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{ marginBottom: 'var(--space-6)' }}>
                <div className="flex justify-between items-center" style={{ marginBottom: 'var(--space-2)' }}>
                    <h2 className="heading-xl text-primary">Credit Decision</h2>
                    <span className={`badge badge-${decisionType?.toLowerCase() === 'approve' ? 'approve' : decisionType?.toLowerCase() === 'reject' ? 'reject' : 'review'}`}>
                        {decisionType}
                    </span>
                </div>
                <p className="body-md text-secondary">Application ID: <span className="data-sm">{application_id}</span></p>
            </div>

            {/* Risk Level */}
            <div style={{ marginBottom: 'var(--space-8)' }}>
                <div className="flex justify-between items-center" style={{ marginBottom: 'var(--space-3)' }}>
                    <div>
                        <p className="body-sm text-tertiary" style={{ textTransform: 'uppercase', letterSpacing: 'var(--tracking-wide)', marginBottom: 'var(--space-1)' }}>
                            Risk Level
                        </p>
                        <p className="heading-lg text-primary">{risk_level}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                        <p className="data-lg text-trust">{default_probability}</p>
                        <p className="body-sm text-secondary">Default Probability</p>
                    </div>
                </div>

                {/* Risk Meter */}
                <div className="risk-meter">
                    <div
                        className={`risk-meter-fill ${riskClass}`}
                        style={{ width: `${riskPercentage * 100}%` }}
                    />
                </div>
            </div>

            {/* Explanation */}
            {explanation && (
                <div style={{
                    padding: 'var(--space-6)',
                    background: 'var(--color-bg-secondary)',
                    borderRadius: 'var(--radius-md)',
                    marginBottom: 'var(--space-8)',
                    border: '1px solid var(--color-border)'
                }}>
                    <p className="body-lg text-primary">{explanation}</p>
                    <div className="flex items-center gap-2" style={{ marginTop: 'var(--space-3)' }}>
                        <div style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: 'var(--radius-full)',
                            background: certainty >= 0.7 ? 'var(--color-trust)' : 'var(--color-text-muted)'
                        }} />
                        <p className="body-sm text-secondary">
                            Certainty: {certainty} ({certainty_description})
                        </p>
                    </div>
                </div>
            )}

            {/* Factors */}
            {(positive_factors.length > 0 || negative_factors.length > 0) && (
                <div style={{ marginBottom: 'var(--space-8)' }}>
                    <h3 className="heading-md text-primary" style={{ marginBottom: 'var(--space-4)' }}>
                        Contributing Factors
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                        {/* Positive Factors */}
                        {positive_factors.length > 0 && (
                            <div>
                                <p className="body-sm text-success" style={{
                                    marginBottom: 'var(--space-3)',
                                    fontWeight: 'var(--weight-semibold)',
                                    textTransform: 'uppercase',
                                    letterSpacing: 'var(--tracking-wide)'
                                }}>
                                    ✓ Positive
                                </p>
                                <div className="flex flex-col gap-3">
                                    {positive_factors.map((factor, idx) => (
                                        <div key={idx} style={{
                                            padding: 'var(--space-4)',
                                            background: 'var(--color-success-subtle)',
                                            borderRadius: 'var(--radius-md)',
                                            borderLeft: '3px solid var(--color-success)'
                                        }}>
                                            <p className="body-md text-success" style={{ fontWeight: 'var(--weight-semibold)', marginBottom: 'var(--space-1)' }}>
                                                {factor.factor}
                                            </p>
                                            <p className="body-sm text-secondary">{factor.description}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Negative Factors */}
                        {negative_factors.length > 0 && (
                            <div>
                                <p className="body-sm text-critical" style={{
                                    marginBottom: 'var(--space-3)',
                                    fontWeight: 'var(--weight-semibold)',
                                    textTransform: 'uppercase',
                                    letterSpacing: 'var(--tracking-wide)'
                                }}>
                                    ⚠ Negative
                                </p>
                                <div className="flex flex-col gap-3">
                                    {negative_factors.map((factor, idx) => (
                                        <div key={idx} style={{
                                            padding: 'var(--space-4)',
                                            background: 'var(--color-critical-subtle)',
                                            borderRadius: 'var(--radius-md)',
                                            borderLeft: '3px solid var(--color-critical)'
                                        }}>
                                            <p className="body-md text-critical" style={{ fontWeight: 'var(--weight-semibold)', marginBottom: 'var(--space-1)' }}>
                                                {factor.factor}
                                            </p>
                                            <p className="body-sm text-secondary">{factor.description}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Recommendations */}
            {recommendations.length > 0 && (
                <div>
                    <h3 className="heading-md text-primary" style={{ marginBottom: 'var(--space-4)' }}>
                        Improvement Recommendations
                    </h3>
                    <div className="flex flex-col gap-4">
                        {recommendations.map((rec, idx) => (
                            <div key={idx} className="card" style={{
                                background: 'var(--color-bg-secondary)',
                                border: '1px solid var(--color-border)',
                                padding: 'var(--space-5)'
                            }}>
                                <div className="flex justify-between items-start" style={{ marginBottom: 'var(--space-3)' }}>
                                    <div>
                                        <span className="body-sm text-trust" style={{
                                            fontWeight: 'var(--weight-semibold)',
                                            textTransform: 'uppercase',
                                            letterSpacing: 'var(--tracking-wide)'
                                        }}>
                                            Priority {rec.priority}
                                        </span>
                                        <h4 className="heading-sm text-primary" style={{ marginTop: 'var(--space-1)' }}>
                                            {rec.action}
                                        </h4>
                                    </div>
                                    {rec.impact && (
                                        <span className="badge badge-approve">{rec.impact}</span>
                                    )}
                                </div>

                                <div className="flex gap-6" style={{ marginBottom: 'var(--space-3)' }}>
                                    <div>
                                        <p className="body-sm text-tertiary">Current</p>
                                        <p className="data-md text-primary">{rec.current}</p>
                                    </div>
                                    <div>
                                        <p className="body-sm text-tertiary">Target</p>
                                        <p className="data-md text-success">{rec.target}</p>
                                    </div>
                                    {rec.timeline && (
                                        <div>
                                            <p className="body-sm text-tertiary">Timeline</p>
                                            <p className="body-md text-primary">{rec.timeline}</p>
                                        </div>
                                    )}
                                </div>

                                {rec.how_to && rec.how_to.length > 0 && (
                                    <div>
                                        <p className="body-sm text-secondary" style={{ marginBottom: 'var(--space-2)', fontWeight: 'var(--weight-medium)' }}>
                                            Action Steps:
                                        </p>
                                        <ul style={{ paddingLeft: 'var(--space-5)' }}>
                                            {rec.how_to.map((step, stepIdx) => (
                                                <li key={stepIdx} className="body-md text-secondary" style={{ marginBottom: 'var(--space-1)' }}>
                                                    {step}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PremiumDecisionCard;
