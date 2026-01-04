
// Logic for settings.html

document.addEventListener('DOMContentLoaded', () => {

    const profileForm = document.getElementById('profile-form');
    const passwordForm = document.getElementById('password-form');

    // Load initial data
    auth.onAuthStateChanged((user) => {
        if (user) {
            document.getElementById('display-name').value = user.displayName || '';
            document.getElementById('email').value = user.email || '';
        }
    });

    // Handle Profile Update
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const user = auth.currentUser;
            const newName = document.getElementById('display-name').value.trim();

            if (!user) return;

            try {
                const btn = profileForm.querySelector('button');
                const originalText = btn.textContent;
                btn.textContent = 'Saving...';
                btn.disabled = true;

                await user.updateProfile({
                    displayName: newName
                });

                showToast('Profile updated successfully!');

                // Update navbar greeting immediately if valid
                const navUser = document.getElementById('user-display-name');
                if (navUser) navUser.textContent = `Welcome, ${newName}`;

                btn.textContent = originalText;
                btn.disabled = false;
            } catch (error) {
                console.error(error);
                showToast(error.message, true);
                btn.textContent = 'Save Changes';
                btn.disabled = false;
            }
        });
    }

    // Handle Password Update
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const user = auth.currentUser;
            const newPass = document.getElementById('new-password').value;
            const confirmPass = document.getElementById('confirm-password').value;

            if (newPass !== confirmPass) {
                showToast('Passwords do not match', true);
                return;
            }

            try {
                const btn = passwordForm.querySelector('button');
                btn.textContent = 'Updating...';
                btn.disabled = true;

                await user.updatePassword(newPass);

                showToast('Password updated! Please login again.');
                setTimeout(() => {
                    authHelpers.signOut();
                }, 2000);

            } catch (error) {
                console.error(error);
                if (error.code === 'auth/requires-recent-login') {
                    showToast('Security: Please sign out and sign in again to change password.', true);
                } else {
                    showToast(error.message, true);
                }
                const btn = passwordForm.querySelector('button');
                btn.textContent = 'Update Password';
                btn.disabled = false;
            }
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
