import { TrendingUp, Info } from 'lucide-react';
import './RiskVisualization.css';

/**
 * RiskVisualization Component
 * Displays probability of default (PD) as a range with confidence bands
 * Uses neutral language and non-manipulative colors
 */
export default function RiskVisualization({ riskScore, confidenceScore, tier }) {
    // Calculate confidence band (±10% around the point estimate)
    const lowerBound = Math.max(0, riskScore - 0.10);
    const upperBound = Math.min(1, riskScore + 0.10);

    // Determine risk category based on PD
    const getRiskCategory = (pd) => {
        if (pd < 0.20) return { label: 'Lower Risk', level: 'low' };
        if (pd < 0.45) return { label: 'Moderate Risk', level: 'moderate' };
        return { label: 'Higher Risk', level: 'high' };
    };

    // Determine confidence level
    const getConfidenceLevel = (confidence) => {
        if (confidence > 0.7) return 'High';
        if (confidence > 0.4) return 'Medium';
        return 'Low';
    };

    const riskCategory = getRiskCategory(riskScore);
    const confidenceLevel = getConfidenceLevel(confidenceScore);

    // Calculate position for visual indicator (0-100%)
    const indicatorPosition = riskScore * 100;
    const lowerBoundPosition = lowerBound * 100;
    const upperBoundPosition = upperBound * 100;

    return (
        <div className="risk-visualization">
            <div className="risk-header">
                <TrendingUp size={20} />
                <h3>Risk Assessment</h3>
            </div>

            {/* Textual Summary */}
            <div className="risk-summary">
                <div className="risk-category">
                    <span className="label">Estimated Default Risk:</span>
                    <span className={`value risk-${riskCategory.level}`}>
                        {riskCategory.label}
                    </span>
                </div>
                <div className="confidence-indicator">
                    <span className="label">Confidence:</span>
                    <span className="value">{confidenceLevel}</span>
                </div>
            </div>

            {/* Visual Range Display */}
            <div className="risk-range">
                <div className="range-labels">
                    <span>0%</span>
                    <span>25%</span>
                    <span>50%</span>
                    <span>75%</span>
                    <span>100%</span>
                </div>

                <div className="range-bar">
                    {/* Background gradient (neutral) */}
                    <div className="range-background"></div>

                    {/* Confidence band */}
                    <div
                        className="confidence-band"
                        style={{
                            left: `${lowerBoundPosition}%`,
                            width: `${upperBoundPosition - lowerBoundPosition}%`
                        }}
                    ></div>

                    {/* Point estimate marker */}
                    <div
                        className="point-estimate"
                        style={{ left: `${indicatorPosition}%` }}
                    >
                        <div className="marker"></div>
                        <div className="marker-label">{(riskScore * 100).toFixed(1)}%</div>
                    </div>
                </div>

                <div className="range-description">
                    <Info size={14} />
                    <span>
                        Estimated range: {(lowerBound * 100).toFixed(1)}% - {(upperBound * 100).toFixed(1)}%
                    </span>
                </div>
            </div>

            {/* Explanation */}
            <div className="risk-explanation">
                <p>
                    This assessment represents the model's estimate of credit risk based on the provided information.
                    The range reflects statistical uncertainty. All decisions are subject to human review.
                </p>
            </div>
        </div>
    );
}
