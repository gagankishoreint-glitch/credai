import { useAuth } from '../contexts/AuthContext';
import { LogOut, Activity, AlertTriangle, TrendingUp } from 'lucide-react';
import './AdminDashboard.css';

export default function AdminDashboard() {
    const { user, logout } = useAuth();

    const stats = [
        { label: 'Total Applications', value: '1,234', icon: Activity, trend: '+12%' },
        { label: 'Pending Review', value: '45', icon: AlertTriangle, trend: '-5%' },
        { label: 'Approval Rate', value: '68%', icon: TrendingUp, trend: '+3%' }
    ];

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="container">
                    <div className="header-content">
                        <div>
                            <h1>Admin Console</h1>
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
                <div className="stats-grid">
                    {stats.map((stat, idx) => (
                        <div key={idx} className="card stat-card">
                            <div className="stat-header">
                                <stat.icon size={24} />
                                <span className="stat-trend">{stat.trend}</span>
                            </div>
                            <div className="stat-value">{stat.value}</div>
                            <div className="stat-label">{stat.label}</div>
                        </div>
                    ))}
                </div>

                <div className="card" style={{ marginTop: '2rem' }}>
                    <h2>System Monitoring</h2>
                    <div className="monitoring-placeholder">
                        <Activity size={48} />
                        <p>PSI Drift Charts</p>
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                            Monitoring dashboard with drift detection metrics
                        </p>
                    </div>
                </div>

                <div className="card" style={{ marginTop: '2rem' }}>
                    <h2>Recent Audit Logs</h2>
                    <table className="audit-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Action</th>
                                <th>Actor</th>
                                <th>Entity</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{new Date().toLocaleString()}</td>
                                <td>MANUAL_OVERRIDE</td>
                                <td>underwriter_1</td>
                                <td>APP_001</td>
                            </tr>
                            <tr>
                                <td>{new Date().toLocaleString()}</td>
                                <td>DECISION_MADE</td>
                                <td>SYSTEM</td>
                                <td>APP_002</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    );
}
