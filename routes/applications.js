const express = require('express');
const router = express.Router();
const db = require('../db');
const jwt = require('jsonwebtoken');

// Middleware to verify token
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.sendStatus(401);

    jwt.verify(token, process.env.JWT_SECRET || 'secret', (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
};

// GET /api/applications - Fetch all applications for the logged-in user
router.get('/', authenticateToken, async (req, res) => {
    try {
        const result = await db.query(
            'SELECT * FROM applications WHERE user_id = $1 ORDER BY created_at DESC',
            [req.user.id]
        );
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server Error' });
    }
});

// POST /api/applications - Submit a new application
router.post('/', authenticateToken, async (req, res) => {
    const { businessName, amount, data } = req.body;
    // AI Algorithm: Deterministic Heuristic Scoring
    let score = 650; // Base Score
    const insights = [];
    const annualRevenue = parseFloat(data.annualRevenue) || 0;
    const operatingExpenses = parseFloat(data.operatingExpenses) || 0; // Monthly
    const yearsInBusiness = parseInt(data.yearsInBusiness) || 0;
    const requestedAmount = parseFloat(amount) || 0;

    // 1. Profitability Impact
    const annualExpenses = operatingExpenses * 12;
    const netIncome = annualRevenue - annualExpenses;

    if (netIncome > (requestedAmount * 0.5)) {
        score += 50;
        insights.push({ type: 'positive', text: 'Strong Debt Coverage Ratio' });
    } else if (netIncome < 0) {
        score -= 50;
        insights.push({ type: 'negative', text: 'Negative Cash Flow Detected' });
    }

    // 2. Business Longevity
    if (yearsInBusiness >= 5) {
        score += 40;
        insights.push({ type: 'positive', text: 'Established Business History (>5 years)' });
    } else if (yearsInBusiness < 2) {
        score -= 30;
        insights.push({ type: 'negative', text: 'Early Stage Venture Risk' });
    }

    // 3. Loan-to-Revenue
    if (requestedAmount < (annualRevenue * 0.3)) {
        score += 30;
    } else if (requestedAmount > annualRevenue) {
        score -= 60;
        insights.push({ type: 'negative', text: 'High Loan-to-Revenue Ratio' });
    }

    // Bounds Check
    score = Math.min(850, Math.max(300, score));

    // Determine Status & Decision
    let status = 'analyzing';
    let decision = 'pending';

    // Simulate auto-approval for high scores
    if (score > 750) {
        status = 'decision';
        decision = 'approved';
    } else if (score < 500) {
        status = 'decision';
        decision = 'rejected';
    }

    data.insights = insights; // Store insights in JSONB
    data.decision = decision;

    try {
        const result = await db.query(
            `INSERT INTO applications (user_id, business_name, amount, status, ai_score, data) 
             VALUES ($1, $2, $3, $4, $5, $6) 
             RETURNING *`,
            [req.user.id, businessName, amount, status, score, data]
        );
        res.status(201).json(result.rows[0]);
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server Error' });
    }
});

module.exports = router;
