import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Lock, User } from 'lucide-react';
import '../design-system.css';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const user = await login(username, password);

            // Navigate based on role
            if (user.role === 'underwriter') {
                navigate('/underwriter');
            } else if (user.role === 'admin') {
                navigate('/admin');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            setError('Invalid credentials. Try: underwriter_1 / secret');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            padding: '2rem'
        }}>
            <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
                <div className="text-center mb-8">
                    <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>AI Credit System</h1>
                    <p className="text-secondary">Smart decisions. No hassle.</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div>
                        <label htmlFor="username" style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-text-secondary)' }}>
                            <div className="flex items-center gap-2">
                                <User size={16} /> Username
                            </div>
                        </label>
                        <input
                            id="username"
                            className="input"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                            autoFocus
                        />
                    </div>

                    <div>
                        <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-text-secondary)' }}>
                            <div className="flex items-center gap-2">
                                <Lock size={16} /> Password
                            </div>
                        </label>
                        <input
                            id="password"
                            className="input"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                            required
                        />
                    </div>

                    {error && <div className="badge badge-reject" style={{ width: '100%', justifyContent: 'center' }}>{error}</div>}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%' }}
                        disabled={loading}
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <div className="text-center mt-6" style={{ marginTop: '2rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                    <p className="text-secondary mb-4" style={{ fontSize: '0.85rem' }}>Demo accounts:</p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
                        <code className="text-accent">applicant_001 / secret</code>
                        <code className="text-accent">underwriter_1 / secret</code>
                        <code className="text-accent">admin / secret</code>
                    </div>
                </div>
            </div>
        </div>
    );
}
