import { AlertCircle, XCircle, Info, AlertTriangle, FileText, Upload } from 'lucide-react';
import './ErrorState.css';

/**
 * ErrorState Component
 * Displays transparent, actionable error messages
 * Prioritizes honesty over false optimism
 */
export default function ErrorState({ type, data, onRetry, onContact, onUpload }) {
    const renderInconclusiveState = () => (
        <div className="error-state warning">
            <AlertCircle size={48} className="error-icon" />
            <h2>Manual Review Required</h2>
            <p>
                Our AI system analyzed your application but couldn't make a confident
                automated decision. This doesn't mean rejection—it means a human
                underwriter will carefully review your case.
            </p>

            <div className="timeline-box">
                <strong>What happens next:</strong>
                <ol>
                    <li>An underwriter will review your application within 48 hours</li>
                    <li>They may request additional documentation</li>
                    <li>You'll receive a final decision via email</li>
                </ol>
            </div>

            <div className="transparency-note">
                <Info size={16} />
                <span>
                    Why manual review? Our AI had {(data.confidence_score * 100).toFixed(0)}% confidence
                    (we require 70%+ for automated decisions). This ensures fairness.
                </span>
            </div>
        </div>
    );

    const renderMissingDataState = () => (
        <div className="error-state info">
            <FileText size={48} className="error-icon" />
            <h3>Income Verification Needed</h3>
            <p>
                You reported an annual income of ${data.self_reported_income?.toLocaleString()},
                but we couldn't verify this from your uploaded documents.
            </p>

            <div className="required-docs">
                <strong>Please upload one of the following:</strong>
                <ul>
                    <li>Recent bank statements (last 3 months)</li>
                    <li>Pay stubs (last 3 months)</li>
                    <li>W2 form (most recent year)</li>
                    <li>Tax return (most recent year)</li>
                </ul>
            </div>

            <button className="btn btn-primary" onClick={onUpload}>
                <Upload size={18} />
                Upload Documents
            </button>

            <div className="transparency-note">
                <Info size={16} />
                <span>
                    Why we need this: Federal regulations require income verification
                    for credit decisions over $10,000.
                </span>
            </div>
        </div>
    );

    const renderDataConflictState = () => (
        <div className="error-state warning">
            <AlertTriangle size={48} className="error-icon" />
            <h3>Data Inconsistency Detected</h3>
            <p>
                We found a difference between your reported income and the income
                shown in your uploaded documents:
            </p>

            <table className="conflict-table">
                <tbody>
                    <tr>
                        <td>You reported:</td>
                        <td><strong>${data.conflicts[0].self_reported.toLocaleString()}/year</strong></td>
                    </tr>
                    <tr>
                        <td>Documents show:</td>
                        <td><strong>${data.conflicts[0].document_verified.toLocaleString()}/year</strong></td>
                    </tr>
                    <tr>
                        <td>Difference:</td>
                        <td className="highlight">{data.conflicts[0].discrepancy_percent}%</td>
                    </tr>
                </tbody>
            </table>

            <div className="action-required">
                <strong>What you can do:</strong>
                <ol>
                    <li>Update your reported income to match your documents</li>
                    <li>Upload additional documents showing the higher income</li>
                    <li>Provide an explanation for the difference</li>
                </ol>
            </div>
        </div>
    );

    const renderRefusalState = () => (
        <div className="error-state error">
            <XCircle size={48} className="error-icon" />
            <h2>Application Cannot Be Processed</h2>
            <p>
                We're unable to process your application at this time due to
                inconsistencies in the submitted information.
            </p>

            <div className="refusal-details">
                <strong>What this means:</strong>
                <p>
                    Our system detected multiple discrepancies between your reported
                    information and supporting documents. This is a safety measure to
                    protect both you and our institution.
                </p>
            </div>

            <div className="next-steps">
                <strong>What you can do:</strong>
                <ol>
                    <li>Review all submitted information for accuracy</li>
                    <li>Ensure all documents are current and legible</li>
                    <li>Contact support if you believe this is an error</li>
                </ol>
            </div>

            <div className="contact-support">
                <button className="btn btn-primary" onClick={onContact}>
                    Contact Support
                </button>
                <button className="btn btn-outline">
                    Start New Application
                </button>
            </div>

            <div className="transparency-note">
                <Info size={16} />
                <span>
                    This decision was made by our automated system. You have the right
                    to request human review by contacting support.
                </span>
            </div>
        </div>
    );

    const renderIneligibleState = () => (
        <div className="error-state neutral">
            <Info size={48} className="error-icon" />
            <h2>Not Eligible at This Time</h2>
            <p>
                Unfortunately, your application doesn't meet our current minimum
                requirements for this product.
            </p>

            <div className="criteria-details">
                <strong>Specific criteria not met:</strong>
                {data.violations?.map((violation, idx) => (
                    <div key={idx} className="criterion">
                        <span className="criterion-name">{violation.rule.replace(/_/g, ' ')}</span>
                        <div className="criterion-values">
                            <span>Required: {violation.required}</span>
                            <span>Your score: {violation.actual}</span>
                        </div>
                    </div>
                ))}
            </div>

            <div className="improvement-advice">
                <h3>How to improve your eligibility:</h3>
                <ul>
                    <li>Pay down existing debts to improve your credit score</li>
                    <li>Make all payments on time for the next 6-12 months</li>
                    <li>Dispute any errors on your credit report</li>
                    <li>Consider a secured credit card to build credit history</li>
                </ul>
            </div>

            <div className="reapply-info">
                <strong>When to reapply:</strong>
                <p>
                    We recommend waiting at least 6 months and working on improving
                    your credit score before reapplying.
                </p>
            </div>

            <div className="transparency-note">
                <Info size={16} />
                <span>
                    Under the Fair Credit Reporting Act, you have the right to know
                    the specific reasons for this decision.
                </span>
            </div>
        </div>
    );

    const renderTechnicalError = () => (
        <div className="error-state warning">
            <AlertTriangle size={48} className="error-icon" />
            <h2>System Temporarily Unavailable</h2>
            <p>
                We're experiencing technical difficulties and couldn't process your
                application right now.
            </p>

            <div className="error-details">
                <strong>What happened:</strong>
                <p>
                    Our decision engine is temporarily unavailable. Your application
                    data has been saved, and no information was lost.
                </p>
            </div>

            <div className="next-steps">
                <strong>What to do:</strong>
                <ol>
                    <li>Wait a few minutes and try again</li>
                    <li>If the problem persists, contact support</li>
                    <li>Your application will be saved for 30 days</li>
                </ol>
            </div>

            <div className="buttons">
                <button className="btn btn-primary" onClick={onRetry}>
                    Try Again
                </button>
                <button className="btn btn-outline" onClick={onContact}>
                    Contact Support
                </button>
            </div>

            <div className="transparency-note">
                <Info size={16} />
                <span>
                    Error Code: {data.error_code} | Time: {new Date().toISOString()} |
                    Reference: {data.reference_id}
                </span>
            </div>
        </div>
    );

    // Render appropriate error state
    switch (type) {
        case 'inconclusive':
            return renderInconclusiveState();
        case 'missing_data':
            return renderMissingDataState();
        case 'data_conflict':
            return renderDataConflictState();
        case 'refused':
            return renderRefusalState();
        case 'ineligible':
            return renderIneligibleState();
        case 'technical':
            return renderTechnicalError();
        default:
            return (
                <div className="error-state neutral">
                    <Info size={48} />
                    <h2>Something Went Wrong</h2>
                    <p>We encountered an unexpected issue. Please try again or contact support.</p>
                </div>
            );
    }
}
