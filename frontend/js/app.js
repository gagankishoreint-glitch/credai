// Application Form Logic

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

        for (let [key, value] of formData.entries()) {
            // Convert numeric fields
            if (['years_in_operation', 'credit_score', 'existing_loans'].includes(key)) {
                applicationData[key] = parseInt(value);
            } else if (['annual_revenue', 'monthly_cashflow', 'loan_amount_requested',
                'debt_to_income_ratio', 'collateral_value'].includes(key)) {
                applicationData[key] = parseFloat(value);
            } else {
                applicationData[key] = value;
            }
        }

        // Show loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline-block';

        try {
            // Submit application
            const response = await api.createApplication(applicationData);
            currentApplicationId = response.id;

            // Hide form
            form.parentElement.style.display = 'none';

            // Show success message
            document.getElementById('applicationIdText').textContent =
                `Application ID: ${response.applicant_id}`;
            successMessage.style.display = 'block';

            // Scroll to success message
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
            window.location.href = `evaluation.html?id=${evaluation.evaluation_id}`;
        } catch (error) {
            alert(`Error evaluating application: ${error.message}`);
            console.error(error);
            evaluateBtn.disabled = false;
            evaluateBtn.textContent = 'Evaluate Now';
        }
    });

    // Real-time validation feedback
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

            // Show error message
            let errorDiv = field.parentElement.querySelector('.form-error');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'form-error';
                field.parentElement.appendChild(errorDiv);
            }
            errorDiv.textContent = errorMessage;
        } else {
            field.classList.remove('invalid');
            field.style.borderColor = '';

            // Remove error message
            const errorDiv = field.parentElement.querySelector('.form-error');
            if (errorDiv) {
                errorDiv.remove();
            }
        }

        return isValid;
    }
});
