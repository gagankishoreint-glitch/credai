// Dynamic Risk Calculator for Credit Evaluation Dashboard
// Calculates AI score and risk metrics based on application data

function calculateCreditScore(data) {
    let score = 600; // Base score

    // Years in business impact (0-120 points)
    if (data.yearsInBusiness >= 10) score += 120;
    else if (data.yearsInBusiness >= 5) score += 80;
    else if (data.yearsInBusiness >= 3) score += 50;
    else if (data.yearsInBusiness >= 1) score += 20;

    // Revenue impact (0-100 points)
    if (data.annualRevenue >= 5000000) score += 100;
    else if (data.annualRevenue >= 2000000) score += 80;
    else if (data.annualRevenue >= 1000000) score += 60;
    else if (data.annualRevenue >= 500000) score += 40;
    else if (data.annualRevenue >= 100000) score += 20;

    // Debt-to-revenue ratio (0-80 points)
    const debtRatio = data.loanAmount / data.annualRevenue;
    if (debtRatio <= 0.2) score += 80;
    else if (debtRatio <= 0.3) score += 60;
    else if (debtRatio <= 0.5) score += 40;
    else if (debtRatio <= 0.7) score += 20;

    // Operating expenses efficiency (0-50 points)
    if (data.operatingExpenses > 0) {
        const monthlyExpenseRatio = (data.operatingExpenses * 12) / data.annualRevenue;
        if (monthlyExpenseRatio <= 0.3) score += 50;
        else if (monthlyExpenseRatio <= 0.5) score += 30;
        else if (monthlyExpenseRatio <= 0.7) score += 15;
    }

    return Math.min(Math.max(score, 300), 850); // Cap between 300-850
}

function calculateRevenueStability(data) {
    // Based on revenue size and years in business
    const revenuePerYear = data.annualRevenue / Math.max(data.yearsInBusiness, 1);

    if (revenuePerYear >= 1000000 && data.yearsInBusiness >= 5) {
        return { rating: 'Strong', percentage: 85, color: '#10B981' };
    } else if (revenuePerYear >= 500000 && data.yearsInBusiness >= 3) {
        return { rating: 'Good', percentage: 70, color: '#F59E0B' };
    } else if (revenuePerYear >= 200000) {
        return { rating: 'Fair', percentage: 55, color: '#F59E0B' };
    } else {
        return { rating: 'Developing', percentage: 35, color: '#EF4444' };
    }
}

function calculateMarketPosition(data) {
    // Based on industry and revenue
    const industryMultipliers = {
        'Tech': 1.2,
        'Technology': 1.2,
        'Services': 1.0,
        'Manufacturing': 1.1,
        'Retail': 0.9
    };

    const multiplier = industryMultipliers[data.industry] || 1.0;
    const adjustedRevenue = data.annualRevenue * multiplier;

    if (adjustedRevenue >= 3000000) {
        return { rating: 'Excellent', percentage: 90, color: '#10B981' };
    } else if (adjustedRevenue >= 1500000) {
        return { rating: 'Good', percentage: 70, color: '#F59E0B' };
    } else if (adjustedRevenue >= 500000) {
        return { rating: 'Fair', percentage: 55, color: '#F59E0B' };
    } else {
        return { rating: 'Growing', percentage: 40, color: '#EF4444' };
    }
}

function calculateDebtServiceCoverage(data) {
    // Monthly loan payment estimate (assuming 5 year term at 8% APR)
    const monthlyRate = 0.08 / 12;
    const months = 60;
    const monthlyPayment = (data.loanAmount * monthlyRate * Math.pow(1 + monthlyRate, months)) /
        (Math.pow(1 + monthlyRate, months) - 1);

    const monthlyRevenue = data.annualRevenue / 12;
    const monthlyProfit = monthlyRevenue - (data.operatingExpenses || 0);

    const coverageRatio = monthlyProfit / monthlyPayment;

    if (coverageRatio >= 2.0) {
        return { rating: 'Excellent', percentage: 92, color: '#5A45FF' };
    } else if (coverageRatio >= 1.5) {
        return { rating: 'Good', percentage: 75, color: '#10B981' };
    } else if (coverageRatio >= 1.2) {
        return { rating: 'Fair', percentage: 60, color: '#F59E0B' };
    } else {
        return { rating: 'Tight', percentage: 35, color: '#EF4444' };
    }
}

function generateKeyFactors(data, revenueStability, marketPosition, debtCoverage) {
    const factors = [];

    // Positive factors
    if (data.yearsInBusiness >= 5) {
        factors.push({
            type: 'positive',
            text: `Strong track record (${data.yearsInBusiness} years in operation)`
        });
    }

    if (revenueStability.rating === 'Strong' || revenueStability.rating === 'Good') {
        factors.push({
            type: 'positive',
            text: 'Positive annual revenue growth trend'
        });
    }

    if (debtCoverage.rating === 'Excellent' || debtCoverage.rating === 'Good') {
        factors.push({
            type: 'positive',
            text: 'Strong debt service coverage ratio'
        });
    }

    // Warning factors
    const debtRatio = data.loanAmount / data.annualRevenue;
    if (debtRatio > 0.5) {
        factors.push({
            type: 'warning',
            text: `High loan-to-revenue ratio (${(debtRatio * 100).toFixed(0)}%)`
        });
    }

    if (data.industry === 'Tech' || data.industry === 'Technology') {
        factors.push({
            type: 'warning',
            text: `Industry volatility detected (${data.industry})`
        });
    }

    if (data.yearsInBusiness < 3) {
        factors.push({
            type: 'warning',
            text: 'Limited operating history (less than 3 years)'
        });
    }

    return factors;
}

// Export for use in dashboard
window.riskCalculator = {
    calculateCreditScore,
    calculateRevenueStability,
    calculateMarketPosition,
    calculateDebtServiceCoverage,
    generateKeyFactors
};
