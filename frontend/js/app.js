// Application Form Logic

// Demo Data Profiles
const demoProfiles = {
    safe: {
        business_type: 'Manufacturing',
        years_in_operation: 12,
        loan_amount_requested: 5000000,
        loan_tenure_months: 36,
        loan_purpose: 'Expansion',
        annual_revenue: 40000000,
        monthly_cashflow: 3500000,
        ebitda_margin: 15.5,
        total_debt: 2000000,
        existing_emi: 45000,
        promoter_credit_score: 780,
        promoter_exp_years: 15,
        collateral_type: 'Machinery',
        collateral_value: 6000000,
        existing_loans: 1,
        repayment_history: 'Good'
    },
    medium: {
        business_type: 'Trading',
        years_in_operation: 4,
        loan_amount_requested: 2000000,
        loan_tenure_months: 24,
        loan_purpose: 'Working Capital',
        annual_revenue: 12000000,
        monthly_cashflow: 800000,
        ebitda_margin: 8.0,
        total_debt: 1500000,
        existing_emi: 35000,
        promoter_credit_score: 680,
        promoter_exp_years: 6,
        collateral_type: 'Inventory',
        collateral_value: 1500000,
        existing_loans: 2,
        repayment_history: 'Average'
    },
    risky: {
        business_type: 'Services',
        years_in_operation: 1,
        loan_amount_requested: 5000000,
        loan_tenure_months: 48,
        loan_purpose: 'Debt Consolidation',
        annual_revenue: 8000000,
        monthly_cashflow: 100000,
        ebitda_margin: 2.0,
        total_debt: 4000000,
        existing_emi: 85000,
        promoter_credit_score: 550,
        promoter_exp_years: 2,
        collateral_type: 'None',
        collateral_value: 0,
        existing_loans: 4,
        repayment_history: 'Poor'
    }
};

window.fillDemo = function (profile) {
    const data = demoProfiles[profile];
    if (!data) return;

    // Helper to set value by name or id
    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) {
            el.value = val;
            // Trigger validation/formatting visuals if any
            el.classList.remove('invalid');
            el.style.borderColor = '';
        }
    };

    setVal('businessType', data.business_type);
    setVal('yearsInOperation', data.years_in_operation);
    setVal('loanAmount', data.loan_amount_requested);
    setVal('loanTenure', data.loan_tenure_months);
    setVal('loanPurpose', data.loan_purpose);
    setVal('annualRevenue', data.annual_revenue);
    setVal('monthlyCashflow', data.monthly_cashflow);
    setVal('ebitdaMargin', data.ebitda_margin);
    setVal('totalDebt', data.total_debt);
    setVal('existingEmi', data.existing_emi);
    setVal('promoterScore', data.promoter_credit_score);
    setVal('promoterExp', data.promoter_exp_years);
    setVal('collateralType', data.collateral_type);
    setVal('collateralValue', data.collateral_value);
    setVal('existingLoans', data.existing_loans);
    setVal('repaymentHistory', data.repayment_history);

    // Legacy mapping
    setVal('creditScore', data.promoter_credit_score);
    setVal('debtToIncome', 0.4); // Just fill a dummy as it's hidden/optional now or specific in old logic

    console.log(`Filled demo profile: ${profile}`);
};

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('applicationForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const successMessage = document.getElementById('successMessage');
    const evaluateBtn = document.getElementById('evaluateBtn');

    let currentApplicationId = null;

    // Smooth Scroll Reveal Observer
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal-on-scroll').forEach((element) => {
        observer.observe(element);
    });

    // Form submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(form);
        const applicationData = {};

        // Parse types correctly
        for (let [key, value] of formData.entries()) {
            // Integers
            if (['years_in_operation', 'credit_score', 'existing_loans', 'loan_tenure_months', 'promoter_exp_years', 'promoter_credit_score'].includes(key)) {
                applicationData[key] = parseInt(value) || 0;
            }
            // Floats
            else if (['annual_revenue', 'monthly_cashflow', 'loan_amount_requested',
                'debt_to_income_ratio', 'collateral_value', 'ebitda_margin', 'net_margin', 'total_debt', 'existing_emi'].includes(key)) {
                applicationData[key] = parseFloat(value) || 0.0;
            }
            // Strings
            else {
                applicationData[key] = value;
            }
        }

        // Sync promoter score if needed
        if (!applicationData.credit_score && applicationData.promoter_credit_score) {
            applicationData.credit_score = applicationData.promoter_credit_score;
        }

        // Show loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline-block';

        try {
            // Submit application
            console.log("Submitting:", applicationData);
            const response = await api.createApplication(applicationData);
            console.log("Response:", response);
            currentApplicationId = response.id;

            // Auto-Evaluation trigger (Optional, but good for UX)
            // Wait, standard flow requires clicking "View Evaluation".
            // Let's stick to standard flow.

            // Hide form, show success
            form.parentElement.style.display = 'none';
            document.getElementById('applicationIdText').textContent =
                `Application ID: ${response.applicant_id}`;
            successMessage.style.display = 'block';
            successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });

        } catch (error) {
            alert(`Error submitting application: ${error.message}`);
            console.error(error);
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
        }
    });

    // Evaluate button click
    evaluateBtn.addEventListener('click', async function () {
        if (!currentApplicationId) return;

        evaluateBtn.disabled = true;
        evaluateBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></span> Evaluating...';

        try {
            const evaluation = await api.evaluateApplication(currentApplicationId);

            // Redirect to evaluation page
            window.location.href = `evaluation.html?id=${evaluation.id}`; // Note: Backend returns id, not evaluation_id sometimes, check schema
        } catch (error) {
            alert(`Error evaluating application: ${error.message}`);
            console.error(error);
            evaluateBtn.disabled = false;
            evaluateBtn.textContent = 'View Evaluation';
        }
    });

    // Real-time validation feedback (Keep existing logic)
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function () {
            validateField(this);
        });

        input.addEventListener('input', function () {
            if (this.classList.contains('invalid')) {
                validateField(this);
            }
        });
    });

    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        } else if (field.type === 'number') {
            const numValue = parseFloat(value);
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');

            if (min && numValue < parseFloat(min)) {
                isValid = false;
                errorMessage = `Value must be at least ${min}`;
            } else if (max && numValue > parseFloat(max)) {
                isValid = false;
                errorMessage = `Value must be at most ${max}`;
            }
        }

        // Update UI
        if (!isValid) {
            field.classList.add('invalid');
            field.style.borderColor = 'var(--color-danger)';
            // ... existing error msg logic ...
        } else {
            field.classList.remove('invalid');
            field.style.borderColor = '';
        }

        return isValid;
    }
});
