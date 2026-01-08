import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle, LogOut, Info } from 'lucide-react';
import axios from 'axios';
import RiskVisualization from './RiskVisualization';
import ExplanationPanel from './ExplanationPanel';
import './ApplicantDashboard.css';

export default function ApplicantDashboard() {
    const { user, logout } = useAuth();
    const [file, setFile] = useState(null);
    const [applicationData, setApplicationData] = useState({
        age: '',
        annual_income: '',
        total_debt: '',
        credit_score: '',
        business_type: 'Retail',
        monthly_debt_obligations: '',
        assets_total: ''
    });
    const [errors, setErrors] = useState({});
    const [decision, setDecision] = useState(null);
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState(1);

    // Validation rules
    const validateField = (name, value) => {
        const rules = {
            age: { min: 18, max: 100, message: 'Age must be between 18 and 100' },
            credit_score: { min: 300, max: 850, message: 'Credit score must be between 300 and 850' },
            annual_income: { min: 0, message: 'Income must be positive' },
            total_debt: { min: 0, message: 'Debt must be positive' },
            monthly_debt_obligations: { min: 0, message: 'Monthly obligations must be positive' },
            assets_total: { min: 0, message: 'Assets must be positive' }
        };

        const rule = rules[name];
        if (!rule) return null;

        const numValue = parseFloat(value);
        if (isNaN(numValue)) return 'Must be a valid number';
        if (rule.min !== undefined && numValue < rule.min) return rule.message;
        if (rule.max !== undefined && numValue > rule.max) return rule.message;
        return null;
    };

    const handleInputChange = (name, value) => {
        setApplicationData({ ...applicationData, [name]: value });
        const error = validateField(name, value);
        setErrors({ ...errors, [name]: error });
    };

    const validateForm = () => {
        const newErrors = {};
        Object.keys(applicationData).forEach(key => {
            if (key !== 'business_type') {
                const error = validateField(key, applicationData[key]);
                if (error) newErrors[key] = error;
                if (!applicationData[key]) newErrors[key] = 'This field is required';
            }
        });
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleFileChange = async (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            // Validate file type
            const validTypes = ['application/pdf', 'text/csv'];
            if (!validTypes.includes(selectedFile.type)) {
                alert('Please upload a PDF or CSV file');
                return;
            }

            // Validate file size (10MB max)
            if (selectedFile.size > 10 * 1024 * 1024) {
                alert('File size must be less than 10MB');
                return;
            }

            setFile(selectedFile);

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await axios.post('/api/v1/documents/upload', formData);
                const extracted = response.data.data;

                if (extracted.doc_verified_income) {
                    setApplicationData(prev => ({
                        ...prev,
                        annual_income: extracted.doc_verified_income.toString(),
                        assets_total: (extracted.assets_total || prev.assets_total).toString()
                    }));
                }
            } catch (error) {
                console.error('Document upload failed:', error);
                alert('Document processing failed. You can continue without it.');
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const payload = {
                applicant_id: user.username,
                age: parseInt(applicationData.age),
                annual_income: parseFloat(applicationData.annual_income),
                total_debt: parseFloat(applicationData.total_debt),
                credit_score: parseInt(applicationData.credit_score),
                business_type: applicationData.business_type,
                monthly_debt_obligations: parseFloat(applicationData.monthly_debt_obligations),
                assets_total: parseFloat(applicationData.assets_total),
                doc_verified_income: parseFloat(applicationData.annual_income)
            };

            const response = await axios.post('/api/v1/decide', payload);
            setDecision(response.data);
            setStep(3);
        } catch (error) {
            console.error('Application failed:', error);
            alert('Application submission failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const getTierBadge = (tier) => {
        if (tier === 'Approve') return <span className="badge badge-success"><CheckCircle size={16} /> Approved</span>;
        if (tier === 'Reject') return <span className="badge badge-danger"><XCircle size={16} /> Declined</span>;
        return <span className="badge badge-warning"><AlertCircle size={16} /> Under Review</span>;
    };

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="container">
                    <div className="header-content">
                        <div>
                            <h1>Credit Application</h1>
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
                {/* Ethical Disclosure */}
                <div className="info-banner">
                    <Info size={20} />
                    <div>
                        <strong>How this works:</strong> Our AI analyzes your application and provides a recommendation.
                        All decisions are reviewed by human underwriters to ensure fairness. This is not an automated decision.
                    </div>
                </div>

                {step === 1 && (
                    <div className="card">
                        <h2>Step 1: Application Details</h2>
                        <p className="step-description">Please provide accurate information. All fields are required.</p>

                        <form onSubmit={(e) => {
                            e.preventDefault();
                            if (validateForm()) setStep(2);
                        }} className="application-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Age *</label>
                                    <input
                                        type="number"
                                        value={applicationData.age}
                                        onChange={(e) => handleInputChange('age', e.target.value)}
                                        className={errors.age ? 'error' : ''}
                                        required
                                    />
                                    {errors.age && <span className="error-text">{errors.age}</span>}
                                </div>
                                <div className="form-group">
                                    <label>Credit Score *</label>
                                    <input
                                        type="number"
                                        value={applicationData.credit_score}
                                        onChange={(e) => handleInputChange('credit_score', e.target.value)}
                                        className={errors.credit_score ? 'error' : ''}
                                        placeholder="300-850"
                                        required
                                    />
                                    {errors.credit_score && <span className="error-text">{errors.credit_score}</span>}
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Annual Income ($) *</label>
                                    <input
                                        type="number"
                                        value={applicationData.annual_income}
                                        onChange={(e) => handleInputChange('annual_income', e.target.value)}
                                        className={errors.annual_income ? 'error' : ''}
                                        required
                                    />
                                    {errors.annual_income && <span className="error-text">{errors.annual_income}</span>}
                                </div>
                                <div className="form-group">
                                    <label>Total Debt ($) *</label>
                                    <input
                                        type="number"
                                        value={applicationData.total_debt}
                                        onChange={(e) => handleInputChange('total_debt', e.target.value)}
                                        className={errors.total_debt ? 'error' : ''}
                                        required
                                    />
                                    {errors.total_debt && <span className="error-text">{errors.total_debt}</span>}
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Monthly Debt Obligations ($) *</label>
                                    <input
                                        type="number"
                                        value={applicationData.monthly_debt_obligations}
                                        onChange={(e) => handleInputChange('monthly_debt_obligations', e.target.value)}
                                        className={errors.monthly_debt_obligations ? 'error' : ''}
                                        required
                                    />
                                    {errors.monthly_debt_obligations && <span className="error-text">{errors.monthly_debt_obligations}</span>}
                                </div>
                                <div className="form-group">
                                    <label>Total Assets ($) *</label>
                                    <input
                                        type="number"
                                        value={applicationData.assets_total}
                                        onChange={(e) => handleInputChange('assets_total', e.target.value)}
                                        className={errors.assets_total ? 'error' : ''}
                                        required
                                    />
                                    {errors.assets_total && <span className="error-text">{errors.assets_total}</span>}
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Business Type *</label>
                                <select
                                    value={applicationData.business_type}
                                    onChange={(e) => setApplicationData({ ...applicationData, business_type: e.target.value })}
                                >
                                    <option>Retail</option>
                                    <option>IT</option>
                                    <option>Construction</option>
                                    <option>Healthcare</option>
                                    <option>Other</option>
                                </select>
                            </div>

                            <button type="submit" className="btn btn-primary btn-full">
                                Continue to Documents
                            </button>
                        </form>
                    </div>
                )}

                {step === 2 && (
                    <div className="card">
                        <h2>Step 2: Upload Documents (Optional)</h2>
                        <p className="step-description">Upload a bank statement or financial document to verify your income. This step is optional but recommended.</p>

                        <div className="upload-zone">
                            <Upload size={48} />
                            <p>Drag and drop or click to upload</p>
                            <p className="upload-hint">Accepted: PDF, CSV (Max 10MB)</p>
                            <input
                                type="file"
                                accept=".pdf,.csv"
                                onChange={handleFileChange}
                                style={{ display: 'none' }}
                                id="file-upload"
                            />
                            <label htmlFor="file-upload" className="btn btn-outline">
                                <FileText size={18} />
                                Choose File
                            </label>
                            {file && (
                                <div className="file-success">
                                    <CheckCircle size={16} />
                                    {file.name}
                                </div>
                            )}
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                            <button onClick={() => setStep(1)} className="btn btn-outline">
                                Back
                            </button>
                            <button onClick={handleSubmit} className="btn btn-primary" disabled={loading} style={{ flex: 1 }}>
                                {loading ? (
                                    <span className="loading-pulse">Analyzing your application...</span>
                                ) : (
                                    'Submit Application'
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {step === 3 && decision && (
                    <div className="card result-card">
                        <div className="result-header">
                            {getTierBadge(decision.tier)}
                            <h2>Application Status: {decision.tier}</h2>
                        </div>

                        {/* Risk Visualization */}
                        <RiskVisualization
                            riskScore={decision.risk_score}
                            confidenceScore={decision.confidence_score || 0.75}
                            tier={decision.tier}
                        />

                        {/* Explanation Panel */}
                        <ExplanationPanel
                            tier={decision.tier}
                            factors={decision.factors}
                            counterfactuals={decision.counterfactuals}
                        />

                        {decision.tier === 'Review' && (
                            <div className="review-notice">
                                <AlertCircle size={20} />
                                <div>
                                    <strong>Human Review Required</strong>
                                    <p>Your application will be reviewed by an underwriter within 24-48 hours. You'll receive an email with the final decision.</p>
                                </div>
                            </div>
                        )}

                        {decision.tier === 'Approve' && (
                            <div className="success-notice">
                                <CheckCircle size={20} />
                                <div>
                                    <strong>Preliminary Approval</strong>
                                    <p>Congratulations! Your application shows strong indicators. Final approval pending underwriter review.</p>
                                </div>
                            </div>
                        )}

                        <button onClick={() => { setStep(1); setDecision(null); setFile(null); }} className="btn btn-outline btn-full">
                            Submit New Application
                        </button>
                    </div>
                )}
            </main>
        </div>
    );
}



