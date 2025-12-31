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

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Submitting...';
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

            // Add to Firestore
            const docRef = await db.collection('applications').add(formData);

            console.log('✅ Application submitted with ID:', docRef.id);

            // Store application ID in localStorage for dashboard
            localStorage.setItem('applicationId', docRef.id);
            localStorage.setItem('userEmail', formData.applicantEmail);

            // Show success message
            alert('✅ Application submitted successfully! Redirecting to dashboard...');

            // Redirect to dashboard
            window.location.href = `dashboard.html?id=${docRef.id}`;

        } catch (error) {
            console.error('❌ Error submitting application:', error);
            alert('Error submitting application: ' + error.message);

            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
});
