// EMI Calculator Logic

function calculateEMI(principal, rate, tenure) {
    const monthlyRate = rate / 12 / 100;
    const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, tenure)) /
        (Math.pow(1 + monthlyRate, tenure) - 1);
    return emi;
}

document.getElementById('calculateBtn').addEventListener('click', function () {
    // Get input values
    const loanAmount = parseFloat(document.getElementById('loanAmount').value) || 0;
    const interestRate = parseFloat(document.getElementById('interestRate').value) || 0;
    const tenure = parseFloat(document.getElementById('tenure').value) || 0;
    const processingFee = parseFloat(document.getElementById('processingFee').value) || 0;
    const insurance = parseFloat(document.getElementById('insurance').value) || 0;
    const prepayCharge = parseFloat(document.getElementById('prepayCharge').value) || 0;
    const monthlyIncome = parseFloat(document.getElementById('monthlyIncome').value) || 0;

    if (loanAmount === 0 || tenure === 0) {
        alert('Please enter loan amount and tenure');
        return;
    }

    // Calculate Base EMI
    const baseEMI = calculateEMI(loanAmount, interestRate, tenure);

    // Real Monthly Burden
    const realMonthlyBurden = baseEMI + insurance;

    // Total Costs
    const totalPayment = baseEMI * tenure;
    const totalInterest = totalPayment - loanAmount;
    const totalInsurance = insurance * tenure;
    const grandTotal = totalPayment + processingFee + totalInsurance;

    // Affordability Ratio
    const emiRatio = monthlyIncome > 0 ? (realMonthlyBurden / monthlyIncome * 100) : 0;

    // Display Results
    document.getElementById('baseEMI').textContent = `₹${baseEMI.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    document.getElementById('insuranceValue').textContent = `₹${insurance.toLocaleString('en-IN')}`;
    document.getElementById('realEMI').textContent = `₹${realMonthlyBurden.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

    document.getElementById('principalValue').textContent = `₹${loanAmount.toLocaleString('en-IN')}`;
    document.getElementById('totalInterest').textContent = `₹${totalInterest.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    document.getElementById('processingValue').textContent = `₹${processingFee.toLocaleString('en-IN')}`;
    document.getElementById('totalInsurance').textContent = `₹${totalInsurance.toLocaleString('en-IN')}`;
    document.getElementById('grandTotal').textContent = `₹${grandTotal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

    document.getElementById('emiRatio').textContent = `${emiRatio.toFixed(1)}%`;

    // Affordability Message
    const affordabilityMsg = document.getElementById('affordabilityMsg');
    if (emiRatio < 40) {
        affordabilityMsg.innerHTML = '✅ <strong>Good!</strong> Your EMI is within safe limits (under 40% of income).';
        affordabilityMsg.style.color = 'var(--color-success)';
    } else if (emiRatio < 50) {
        affordabilityMsg.innerHTML = '⚠️ <strong>Caution:</strong> EMI is 40-50% of income. Consider reducing loan amount.';
        affordabilityMsg.style.color = 'var(--color-warning)';
    } else {
        affordabilityMsg.innerHTML = '❌ <strong>High Risk:</strong> EMI exceeds 50% of income. This loan may be unaffordable.';
        affordabilityMsg.style.color = 'var(--color-danger)';
    }

    // Show results card
    document.getElementById('resultsCard').style.display = 'block';
    document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Auto-calculate on input change
const inputs = ['loanAmount', 'interestRate', 'tenure', 'processingFee', 'insurance', 'prepayCharge', 'monthlyIncome'];
inputs.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.addEventListener('change', function () {
            const resultsCard = document.getElementById('resultsCard');
            if (resultsCard.style.display === 'block') {
                document.getElementById('calculateBtn').click();
            }
        });
    }
});
