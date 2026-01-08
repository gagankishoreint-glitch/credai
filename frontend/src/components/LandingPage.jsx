import React from 'react';
import { Link } from 'react-router-dom';
import '../design-system.css';

const LandingPage = () => {
    return (
        <div className="page-home">
            {/* Navbar */}
            <nav className="navbar">
                <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Link to="/" className="text-xl font-bold text-primary" style={{ textDecoration: 'none', fontSize: '1.8rem', fontWeight: 700 }}>
                        CredAi
                    </Link>

                    <div className="hidden md:flex gap-8" style={{ display: 'flex', gap: '40px' }}>
                        <Link to="/application" className="text-secondary hover:text-accent" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}>Application Submission</Link>
                        <Link to="/dashboard" className="text-secondary hover:text-accent" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}>Risk Score Visualization</Link>
                        <Link to="/underwriter" className="text-secondary hover:text-accent" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}>Underwriter Dashboard</Link>
                    </div>

                    <div className="flex gap-4">
                        <Link to="/login" className="btn btn-outline" style={{ marginRight: '12px' }}>Sign In</Link>
                        <Link to="/application" className="btn btn-primary">Start for Free</Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section style={{ padding: '180px 0 120px', position: 'relative', overflow: 'hidden' }}>
                <div className="container grid grid-cols-2 gap-8 items-center" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '80px', alignItems: 'center' }}>
                    <div>
                        <h1 className="mb-4" style={{ fontSize: '4.5rem', lineHeight: 1.1, marginBottom: '24px' }}>
                            <span className="text-gradient">AI-Driven</span> Smart<br />Credit Evaluation
                        </h1>
                        <p className="text-secondary mb-8" style={{ fontSize: '1.25rem', marginBottom: '40px', lineHeight: 1.7 }}>
                            Automate your lending decisions with 80% accuracy. Reduce manual underwriting time from days to seconds using advanced machine learning.
                        </p>
                        <div className="flex gap-4">
                            <Link to="/application" className="btn btn-primary">Start for Free</Link>
                            <Link to="/methodology" className="btn btn-outline">How it Works</Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section style={{ padding: '120px 0', background: 'var(--color-bg-primary)' }}>
                <div className="container">
                    <div className="text-center mb-12" style={{ marginBottom: '60px' }}>
                        <span className="badge badge-review mb-4" style={{ background: 'transparent', border: '1px solid var(--color-accent-primary)', color: 'var(--color-accent-primary)' }}>Why Choose Our AI</span>
                        <h2 className="mb-4" style={{ marginTop: '16px' }}>Power Your Lending Decisions</h2>
                        <p className="text-secondary" style={{ maxWidth: '600px', margin: '0 auto' }}>
                            Our system leverages advanced machine learning to provide explainable, fair, and accurate credit scores.
                        </p>
                    </div>

                    <div className="grid grid-cols-3 gap-8" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>

                        <Link to="/application" className="card" style={{ textDecoration: 'none', display: 'block' }}>
                            <div className="mb-4 text-accent" style={{ marginBottom: '20px', fontSize: '28px' }}>
                                📄
                            </div>
                            <h3 className="mb-4" style={{ marginBottom: '16px' }}>Application Submission</h3>
                            <p className="text-secondary">
                                Streamlined interface for business loan applications with intelligent document upload capabilities.
                            </p>
                        </Link>

                        <Link to="/dashboard" className="card" style={{ textDecoration: 'none', display: 'block' }}>
                            <div className="mb-4 text-accent" style={{ marginBottom: '20px', fontSize: '28px' }}>
                                📊
                            </div>
                            <h3 className="mb-4" style={{ marginBottom: '16px' }}>Risk Visualization</h3>
                            <p className="text-secondary">
                                Real-time AI analysis providing clear credit scoring, probability metrics, and risk insights.
                            </p>
                        </Link>

                        <Link to="/underwriter" className="card" style={{ textDecoration: 'none', display: 'block' }}>
                            <div className="mb-4 text-accent" style={{ marginBottom: '20px', fontSize: '28px' }}>
                                🛡️
                            </div>
                            <h3 className="mb-4" style={{ marginBottom: '16px' }}>Underwriter Dashboard</h3>
                            <p className="text-secondary">
                                Advanced admin panel for human underwriters to review AI recommendations and decisions.
                            </p>
                        </Link>

                    </div>
                </div>
            </section>
        </div>
    );
};

export default LandingPage;
