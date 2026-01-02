// Updated Application Form Submission Handler with more fields
// Handles form submission and saves to Firestore

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('application-form');

    if (!form) {
        console.log('Application form not found on this page');
        return;
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Final validation before submission
        const requiredFields = form.querySelectorAll('input[required], select[required]');
        let hasErrors = false;
        let errorFields = [];

        requiredFields.forEach(field => {
            if (!field.value || field.value.trim() === '') {
                hasErrors = true;
                field.style.borderColor = '#EF4444';
                const label = form.querySelector(`label[for="${field.id}"]`) || field.previousElementSibling;
                errorFields.push(label ? label.textContent : field.name);
            } else {
                field.style.borderColor = '';
            }
        });

        if (hasErrors) {
            alert('❌ Please fill in all required fields:\n\n' + errorFields.join('\n'));
            return;
        }

        // Check if at least one PDF has been uploaded
        if (!window.uploadedFiles || window.uploadedFiles.length === 0) {
            alert('❌ Please upload at least one bank statement (PDF) before submitting your application.');
            // Scroll to documents section
            document.getElementById('step-3').scrollIntoView({ behavior: 'smooth' });
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<ion-icon name="hourglass-outline" style="margin-right: 8px;"></ion-icon> Submitting...';
        submitBtn.disabled = true;

        try {
            // Get form data - using name attributes as fallback if IDs don't exist
            const formData = {
                businessName: document.querySelector('[name="business_name"]').value,
                industry: document.querySelector('[name="industry_type"]').value,
                applicantEmail: document.querySelector('[name="email"]')?.value || 'demo@example.com',
                phoneNumber: document.querySelector('[name="phone"]')?.value || 'N/A',
                loanAmount: parseFloat(document.querySelector('[name="loan_amount"]').value),
                annualRevenue: parseFloat(document.querySelector('[name="annual_revenue"]').value),
                yearsInBusiness: parseInt(document.querySelector('[name="years_in_operation"]').value),
                employeeCount: parseInt(document.querySelector('[name="employees"]')?.value) || 0,
                creditScore: parseInt(document.querySelector('[name="credit_score"]')?.value) || 0,
                loanPurpose: document.querySelector('[name="purpose"]')?.value || 'Business expansion',
                operatingExpenses: parseFloat(document.querySelector('[name="operating_expenses"]')?.value) || 0,
                status: 'received',
                submittedAt: firebase.firestore.FieldValue.serverTimestamp(),
                analyzedAt: null,
                decision: 'pending',
                aiScore: null,
                riskLevel: null
            };

            console.log('📤 Submitting application:', formData);

            // Add to Firestore
            const docRef = await db.collection('applications').add(formData);

            console.log('✅ Application submitted with ID:', docRef.id);

            // Store application ID in localStorage for dashboard
            localStorage.setItem('applicationId', docRef.id);
            localStorage.setItem('userEmail', formData.applicantEmail);

            // Clear session storage (draft data)
            for (let i = 1; i <= 3; i++) {
                sessionStorage.removeItem('applicationStep' + i);
            }

            // Show success message
            alert('✅ Application submitted successfully! Redirecting to dashboard...');

            // Redirect to dashboard
            window.location.href = `dashboard.html?id=${docRef.id}`;

        } catch (error) {
            console.error('❌ Error submitting application:', error);

            // Show detailed error message
            let errorMsg = 'Error submitting application. ';
            if (error.code === 'permission-denied') {
                errorMsg += 'Please check your Firebase permissions.';
            } else if (error.code === 'unavailable') {
                errorMsg += 'Network connection issue. Please check your internet connection.';
            } else {
                errorMsg += error.message || 'Unknown error occurred.';
            }

            alert('❌ ' + errorMsg);

            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
});
