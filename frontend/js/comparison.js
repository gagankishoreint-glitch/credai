// Loan Comparison Tool Logic

// Priority slider updates
const sliders = [
    { slider: 'emiSlider', display: 'emiWeight' },
    { slider: 'approvalSlider', display: 'approvalWeight' },
    { slider: 'prepaySlider', display: 'prepayWeight' },
    { slider: 'interestSlider', display: 'interestWeight' }
];

sliders.forEach(item => {
    const slider = document.getElementById(item.slider);
    const display = document.getElementById(item.display);

    if (slider && display) {
        slider.addEventListener('input', function () {
            display.textContent = this.value;
        });
    }
});

// EMI Calculation Function
function calculateEMI(principal, rate, tenure) {
    const monthlyRate = rate / 12 / 100;
    const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, tenure)) /
        (Math.pow(1 + monthlyRate, tenure) - 1);
    return emi;
}

// Total Cost Calculation
function calculateTotalCost(principal, rate, tenure, processingFee) {
    const emi = calculateEMI(principal, rate, tenure);
    const totalPayment = emi * tenure;
    const totalInterest = totalPayment - principal;
    return totalPayment + processingFee;
}

// Priority Score Calculation
function calculatePriorityScore(loanData, weights) {
    let score = 0;
    const maxScore = 100;

    // Lower EMI is better (inverse scoring)
    const emiScore = Math.max(0, 100 - (loanData.emi / loanData.amount * 10000));
    score += (emiScore * weights.emi / 100);

    // Faster approval is better (inverse scoring)
    const approvalScore = Math.max(0, 100 - (loanData.approvalTime * 5));
    score += (approvalScore * weights.approval / 100);

    // Lower prepayment charges is better (inverse scoring)
    const prepayScore = Math.max(0, 100 - (loanData.prepayCharge * 20));
    score += (prepayScore * weights.prepay / 100);

    // Lower total interest is better (inverse scoring)
    const interestScore = Math.max(0, 100 - (loanData.totalInterest / loanData.amount * 50));
    score += (interestScore * weights.interest / 100);

    // Normalize to 0-100
    const totalWeight = weights.emi + weights.approval + weights.prepay + weights.interest;
    return (score / totalWeight) * 100;
}

// Compare Button Handler
document.getElementById('compareBtn').addEventListener('click', function () {
    // Get Loan A Data
    const loanA = {
        bank: document.getElementById('bankA').value || 'Loan A',
        amount: parseFloat(document.getElementById('amountA').value) || 0,
        rate: parseFloat(document.getElementById('rateA').value) || 0,
        tenure: parseFloat(document.getElementById('tenureA').value) || 0,
        fee: parseFloat(document.getElementById('feeA').value) || 0,
        prepayCharge: parseFloat(document.getElementById('prepayA').value) || 0,
        approvalTime: parseFloat(document.getElementById('approvalA').value) || 0
    };

    // Get Loan B Data
    const loanB = {
        bank: document.getElementById('bankB').value || 'Loan B',
        amount: parseFloat(document.getElementById('amountB').value) || 0,
        rate: parseFloat(document.getElementById('rateB').value) || 0,
        tenure: parseFloat(document.getElementById('tenureB').value) || 0,
        fee: parseFloat(document.getElementById('feeB').value) || 0,
        prepayCharge: parseFloat(document.getElementById('prepayB').value) || 0,
        approvalTime: parseFloat(document.getElementById('approvalB').value) || 0
    };

    // Validation
    if (loanA.amount === 0 || loanB.amount === 0) {
        alert('Please enter loan amounts for both offers');
        return;
    }

    // Calculate EMI and Total Cost
    loanA.emi = calculateEMI(loanA.amount, loanA.rate, loanA.tenure);
    loanA.totalCost = calculateTotalCost(loanA.amount, loanA.rate, loanA.tenure, loanA.fee);
    loanA.totalInterest = loanA.totalCost - loanA.amount - loanA.fee;

    loanB.emi = calculateEMI(loanB.amount, loanB.rate, loanB.tenure);
    loanB.totalCost = calculateTotalCost(loanB.amount, loanB.rate, loanB.tenure, loanB.fee);
    loanB.totalInterest = loanB.totalCost - loanB.amount - loanB.fee;

    // Get Priority Weights
    const weights = {
        emi: parseFloat(document.getElementById('emiSlider').value),
        approval: parseFloat(document.getElementById('approvalSlider').value),
        prepay: parseFloat(document.getElementById('prepaySlider').value),
        interest: parseFloat(document.getElementById('interestSlider').value)
    };

    // Calculate Priority Scores
    loanA.score = calculatePriorityScore(loanA, weights);
    loanB.score = calculatePriorityScore(loanB, weights);

    // Display Results
    document.getElementById('emiA').textContent = `₹${loanA.emi.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    document.getElementById('totalA').textContent = `₹${loanA.totalCost.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    document.getElementById('scoreA').textContent = loanA.score.toFixed(1);

    document.getElementById('emiB').textContent = `₹${loanB.emi.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    document.getElementById('totalB').textContent = `₹${loanB.totalCost.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    document.getElementById('scoreB').textContent = loanB.score.toFixed(1);

    // Determine Winner
    const winnerA = document.getElementById('winnerA');
    const winnerB = document.getElementById('winnerB');

    if (loanA.score > loanB.score) {
        winnerA.style.display = 'flex';
        winnerB.style.display = 'none';
    } else if (loanB.score > loanA.score) {
        winnerB.style.display = 'flex';
        winnerA.style.display = 'none';
    } else {
        winnerA.style.display = 'none';
        winnerB.style.display = 'none';
    }

    // Smooth scroll to results
    document.getElementById('resultA').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});
