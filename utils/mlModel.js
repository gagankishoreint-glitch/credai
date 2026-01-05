/**
 * Logistic Regression Model
 * Calculates approval probability based on normalized features.
 */

class LogisticRegression {
    constructor() {
        // Pre-trained weights (Simulated from training process)
        this.weights = {
            normRevenue: 1.5,      // High revenue is good
            normYears: 0.8,        // Experience is good
            normCreditScore: 2.5,  // History is very important
            normProfitMargin: 2.0, // Profitability is key
            normLoanToRev: 1.2     // Low debt ratio (which is inverted in preprocessor) is good
        };
        this.bias = -3.5; // Base threshold (shifts sigmoid)
    }

    sigmoid(z) {
        return 1 / (1 + Math.exp(-z));
    }

    predict(features) {
        let z = this.bias;

        // Linear combination: z = w1x1 + w2x2 + ... + b
        for (const [key, value] of Object.entries(features)) {
            if (this.weights[key] !== undefined) {
                z += this.weights[key] * value;
            }
        }

        const probability = this.sigmoid(z);

        // Calculate Confidence: Distance from 0.5 (Decision Boundary)
        // 0.5 = 0% confident, 1.0 or 0.0 = 100% confident
        const confidence = Math.abs(probability - 0.5) * 2;

        return {
            probability: probability,
            confidence: confidence,
            score: Math.round(probability * 100), // Raw 0-100 score
            creditScore: Math.round(300 + (probability * 550)) // Mapped to 300-850
        };
    }
}

module.exports = new LogisticRegression();
