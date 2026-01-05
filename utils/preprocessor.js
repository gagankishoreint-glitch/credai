/**
 * Data Preprocessing Module
 * Handles cleaning, normalization and feature engineering.
 */

const Preprocessor = {
    // 1. Cleaning: Handle missing values
    clean: (data) => {
        return {
            annualRevenue: parseFloat(data.annualRevenue) || 0,
            operatingExpenses: parseFloat(data.operatingExpenses) || 0,
            loanAmount: parseFloat(data.loanAmount) || 0,
            yearsInBusiness: parseInt(data.yearsInBusiness) || 0,
            creditScore: parseInt(data.creditScore) || 650 // Default assumption
        };
    },

    // 2. Feature Engineering: Create Ratios
    engineerFeatures: (cleanedData) => {
        const annualExpenses = cleanedData.operatingExpenses * 12;
        const netIncome = cleanedData.annualRevenue - annualExpenses;

        // Avoid division by zero
        const revenue = cleanedData.annualRevenue || 1;
        const income = netIncome === 0 ? 1 : netIncome;

        return {
            ...cleanedData,
            netIncome: netIncome,
            debtToIncomeRatio: (cleanedData.loanAmount / income),
            loanToRevenueRatio: (cleanedData.loanAmount / revenue),
            profitMargin: (netIncome / revenue)
        };
    },

    // 3. Normalization: Min-Max Scaling (0-1)
    // Based on typical SME bounds: Rev(0-5M), Exp(0-4M), Score(300-850)
    normalize: (features) => {
        const minMax = (val, min, max) => Math.max(0, Math.min(1, (val - min) / (max - min)));

        return {
            normRevenue: minMax(features.annualRevenue, 0, 5000000),
            normYears: minMax(features.yearsInBusiness, 0, 20),
            normCreditScore: minMax(features.creditScore, 300, 850),
            normProfitMargin: minMax(features.profitMargin, -0.5, 0.5), // Range -50% to +50%
            // Inverted: Lower ratio is better, so 1 - norm
            normLoanToRev: 1 - minMax(features.loanToRevenueRatio, 0, 2)
        };
    }
};

module.exports = Preprocessor;
