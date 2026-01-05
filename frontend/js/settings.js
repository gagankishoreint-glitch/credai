
// Logic for settings.html

// Logic for settings.html

const API_BASE_URL = window.API_CONFIG ? window.API_CONFIG.BASE_URL : '/api';

document.addEventListener('DOMContentLoaded', async () => {

    const profileForm = document.getElementById('profile-form');
    const passwordForm = document.getElementById('password-form'); // Not implemented on backend yet

    // Load initial data
    try {
        const user = await window.authHelpers.checkAuth();
        if (user) {
            document.getElementById('display-name').value = user.full_name || '';
            document.getElementById('email').value = user.email || '';
        }
    } catch (err) {
        window.location.href = 'login.html';
    }

    // Handle Profile Update
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newName = document.getElementById('display-name').value.trim();
            const token = localStorage.getItem('token');

            try {
                const btn = profileForm.querySelector('button');
                const originalText = btn.textContent;
                btn.textContent = 'Saving...';
                btn.disabled = true;

                const response = await fetch(`${API_BASE_URL}/auth/profile`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ fullName: newName })
                });

                if (!response.ok) throw new Error('Failed to update profile');

                const updatedUser = await response.json();

                // Update local storage
                let currentUser = JSON.parse(localStorage.getItem('user'));
                currentUser.full_name = updatedUser.full_name;
                localStorage.setItem('user', JSON.stringify(currentUser));

                showToast('Profile updated successfully!');

                btn.textContent = originalText;
                btn.disabled = false;
            } catch (error) {
                console.error(error);
                showToast(error.message, true);
                const btn = profileForm.querySelector('button');
                btn.textContent = 'Save Changes';
                btn.disabled = false;
            }
        });
    }

    // Handle Password Update (Mock/Placeholder)
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showToast('Password update not available in this simplified version.', true);
        });
    }
});

// Toast Notification Helper
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = isError ? 'toast error show' : 'toast show';

    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}
