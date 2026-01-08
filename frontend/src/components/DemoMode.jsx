import { useState } from 'react';
import { Play, RotateCcw, TrendingUp, Users, DollarSign, Scale } from 'lucide-react';
import './DemoMode.css';

/**
 * DemoMode Component
 * Interactive demonstration of AI vs Traditional credit evaluation
 */
export default function DemoMode() {
    const [activeScenario, setActiveScenario] = useState(null);
    const [isRunning, setIsRunning] = useState(false);
    const [traditionalProgress, setTraditionalProgress] = useState(0);
    const [aiProgress, setAIProgress] = useState(0);

    const scenarios = [
        { id: 'speed', name: 'Speed Comparison', icon: TrendingUp },
        { id: 'consistency', name: 'Consistency Test', icon: Users },
        { id: 'fairness', name: 'Fairness Analysis', icon: Scale },
        { id: 'cost', name: 'Cost Savings', icon: DollarSign }
    ];

    const metrics = {
        speed: {
            traditional: { time: '45 min', perApp: '4.5 min' },
            ai: { time: '2.3 sec', perApp: '0.23 sec' },
            improvement: '1,174x faster'
        },
        consistency: {
            traditional: { score: 62, variance: 'High' },
            ai: { score: 100, variance: 'Zero' },
            improvement: '+38 pp'
        },
        fairness: {
            traditional: { dir: 0.60, status: 'Below threshold' },
            ai: { dir: 0.89, status: 'Compliant' },
            improvement: '+48%'
        },
        cost: {
            traditional: { annual: '$320,000' },
            ai: { annual: '$65,000' },
            improvement: '$255,000 saved'
        }
    };

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    const runSpeedDemo = async () => {
        setIsRunning(true);
        setTraditionalProgress(0);
        setAIProgress(0);

        // AI completes quickly
        for (let i = 0; i <= 100; i += 10) {
            setAIProgress(i);
            await sleep(230);
        }

        // Traditional takes much longer
        for (let i = 0; i <= 100; i += 10) {
            setTraditionalProgress(i);
            await sleep(4500);
        }

        setIsRunning(false);
    };

    const renderSpeedScenario = () => (
        <div className="scenario-content">
            <h2>Speed Comparison</h2>
            <p>Processing 10 credit applications...</p>

            <div className="comparison-grid">
                <div className="method-card traditional">
                    <h3>Traditional Method</h3>
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${traditionalProgress}%` }}></div>
                    </div>
                    <div className="progress-text">{traditionalProgress}%</div>
                    <div className="time-display">
                        <strong>Time:</strong> {metrics.speed.traditional.time}
                    </div>
                    <div className="status">
                        {traditionalProgress < 100 ? 'In Progress...' : 'Complete'}
                    </div>
                </div>

                <div className="method-card ai">
                    <h3>AI-Powered System</h3>
                    <div className="progress-bar">
                        <div className="progress-fill ai" style={{ width: `${aiProgress}%` }}></div>
                    </div>
                    <div className="progress-text">{aiProgress}%</div>
                    <div className="time-display">
                        <strong>Time:</strong> {metrics.speed.ai.time} ✓
                    </div>
                    <div className="status">
                        {aiProgress === 100 ? 'Complete ✓' : 'Processing...'}
                    </div>
                </div>
            </div>

            <div className="improvement-banner">
                🚀 {metrics.speed.improvement}
            </div>

            <button
                className="btn btn-primary"
                onClick={runSpeedDemo}
                disabled={isRunning}
            >
                <Play size={18} />
                {isRunning ? 'Running...' : 'Run Demo'}
            </button>
        </div>
    );

    const renderConsistencyScenario = () => (
        <div className="scenario-content">
            <h2>Consistency Test</h2>
            <p>Testing 100 identical applications...</p>

            <div className="comparison-grid">
                <div className="method-card traditional">
                    <h3>Traditional (3 Underwriters)</h3>
                    <div className="consistency-results">
                        <div className="result-item">
                            <span>Approve:</span>
                            <strong>62</strong>
                        </div>
                        <div className="result-item">
                            <span>Reject:</span>
                            <strong>31</strong>
                        </div>
                        <div className="result-item">
                            <span>Review:</span>
                            <strong>7</strong>
                        </div>
                    </div>
                    <div className="consistency-score">
                        <strong>Consistency:</strong> {metrics.consistency.traditional.score}%
                    </div>
                    <div className="variance">
                        Variance: {metrics.consistency.traditional.variance}
                    </div>
                </div>

                <div className="method-card ai">
                    <h3>AI System</h3>
                    <div className="consistency-results">
                        <div className="result-item">
                            <span>Approve:</span>
                            <strong>100 ✓</strong>
                        </div>
                        <div className="result-item">
                            <span>Reject:</span>
                            <strong>0</strong>
                        </div>
                        <div className="result-item">
                            <span>Review:</span>
                            <strong>0</strong>
                        </div>
                    </div>
                    <div className="consistency-score">
                        <strong>Consistency:</strong> {metrics.consistency.ai.score}% ✓
                    </div>
                    <div className="variance">
                        Variance: {metrics.consistency.ai.variance} ✓
                    </div>
                </div>
            </div>

            <div className="insight-box">
                <strong>Insight:</strong> Human underwriters showed 38% disagreement on identical
                cases due to fatigue, mood, and subjective judgment.
            </div>
        </div>
    );

    const renderFairnessScenario = () => (
        <div className="scenario-content">
            <h2>Fairness Analysis</h2>
            <p>Comparing approval rates across business sectors...</p>

            <div className="comparison-grid">
                <div className="method-card traditional">
                    <h3>Traditional Method</h3>
                    <div className="fairness-metrics">
                        <div className="sector-rate">
                            <span>IT Sector:</span>
                            <strong>68% approved</strong>
                        </div>
                        <div className="sector-rate warning">
                            <span>Construction:</span>
                            <strong>41% approved ⚠️</strong>
                        </div>
                    </div>
                    <div className="dir-display">
                        <strong>Disparate Impact Ratio:</strong>
                        <div className="dir-value error">
                            {metrics.fairness.traditional.dir} ❌
                        </div>
                        <div className="dir-status">
                            (Below 0.80 threshold)
                        </div>
                    </div>
                </div>

                <div className="method-card ai">
                    <h3>AI with Fairness Mitigation</h3>
                    <div className="fairness-metrics">
                        <div className="sector-rate">
                            <span>IT Sector:</span>
                            <strong>65% approved</strong>
                        </div>
                        <div className="sector-rate success">
                            <span>Construction:</span>
                            <strong>58% approved ✓</strong>
                        </div>
                    </div>
                    <div className="dir-display">
                        <strong>Disparate Impact Ratio:</strong>
                        <div className="dir-value success">
                            {metrics.fairness.ai.dir} ✓
                        </div>
                        <div className="dir-status">
                            (Above 0.80 threshold)
                        </div>
                    </div>
                </div>
            </div>

            <div className="insight-box">
                <strong>Mitigation:</strong> Stratified thresholds ensure Construction sector
                applicants are evaluated fairly despite income variability.
            </div>
        </div>
    );

    const renderCostScenario = () => (
        <div className="scenario-content">
            <h2>Annual Cost Comparison</h2>

            <table className="cost-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Traditional</th>
                        <th>AI System</th>
                        <th>Savings</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Underwriter Salaries (3 FTE)</td>
                        <td>$240,000</td>
                        <td>$0</td>
                        <td className="savings">$240,000</td>
                    </tr>
                    <tr>
                        <td>Training & Onboarding</td>
                        <td>$30,000</td>
                        <td>$0</td>
                        <td className="savings">$30,000</td>
                    </tr>
                    <tr>
                        <td>Error Correction</td>
                        <td>$50,000</td>
                        <td>$5,000</td>
                        <td className="savings">$45,000</td>
                    </tr>
                    <tr>
                        <td>AI System Cost</td>
                        <td>$0</td>
                        <td>$60,000</td>
                        <td className="cost">-$60,000</td>
                    </tr>
                    <tr className="total">
                        <td><strong>Total</strong></td>
                        <td><strong>$320,000</strong></td>
                        <td><strong>$65,000</strong></td>
                        <td className="savings"><strong>$255,000</strong></td>
                    </tr>
                </tbody>
            </table>

            <div className="improvement-banner">
                💰 80% cost reduction
            </div>
        </div>
    );

    return (
        <div className="demo-mode-container">
            <header className="demo-header">
                <h1>AI Credit System Demo</h1>
                <div className="demo-controls">
                    <button className="btn btn-outline" onClick={() => {
                        setActiveScenario(null);
                        setTraditionalProgress(0);
                        setAIProgress(0);
                    }}>
                        <RotateCcw size={18} />
                        Reset
                    </button>
                </div>
            </header>

            {!activeScenario ? (
                <div className="scenario-selector">
                    <h2>Choose a Demo Scenario</h2>
                    <div className="scenarios-grid">
                        {scenarios.map(scenario => {
                            const Icon = scenario.icon;
                            return (
                                <div
                                    key={scenario.id}
                                    className="scenario-card"
                                    onClick={() => setActiveScenario(scenario.id)}
                                >
                                    <Icon size={48} />
                                    <h3>{scenario.name}</h3>
                                    <button className="btn btn-primary">
                                        Start Demo →
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ) : (
                <div className="scenario-display">
                    <button
                        className="btn btn-outline back-button"
                        onClick={() => setActiveScenario(null)}
                    >
                        ← Back to Scenarios
                    </button>

                    {activeScenario === 'speed' && renderSpeedScenario()}
                    {activeScenario === 'consistency' && renderConsistencyScenario()}
                    {activeScenario === 'fairness' && renderFairnessScenario()}
                    {activeScenario === 'cost' && renderCostScenario()}
                </div>
            )}

            <div className="insights-panel">
                <h2>Key Insights</h2>
                <ul>
                    <li>✓ 1,174x faster processing</li>
                    <li>✓ 100% decision consistency</li>
                    <li>✓ 48% improvement in fairness (DIR: 0.60 → 0.89)</li>
                    <li>✓ $255,000 annual cost savings</li>
                    <li>✓ 200x daily capacity increase</li>
                </ul>
            </div>
        </div>
    );
}
