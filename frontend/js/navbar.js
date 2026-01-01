document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar');
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    const navActions = document.querySelector('.nav-actions');

    // Sticky Navbar on Scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            navbar.classList.add('is-sticky');
        } else {
            navbar.classList.remove('is-sticky');
        }
    });

    // Dropdown Logic
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const parent = toggle.closest('.dropdown');

            // Close others
            document.querySelectorAll('.dropdown.is-active').forEach(d => {
                if (d !== parent) d.classList.remove('is-active');
            });

            // Toggle current
            parent.classList.toggle('is-active');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown.is-active').forEach(d => {
                d.classList.remove('is-active');
            });
        }
    });

    // Dynamic Auth State
    // Check if firebase and auth are available
    if (typeof firebase !== 'undefined' && typeof auth !== 'undefined') {
        auth.onAuthStateChanged((user) => {
            if (user) {
                // User is logged in
                console.log('User logged in, updating navbar');
                navActions.innerHTML = `
                    <a href="dashboard.html" class="btn btn-outline" style="margin-right: 12px; border: none; color: var(--color-white);">Dashboard</a>
                    <button onclick="authHelpers.signOut()" class="btn btn-primary">Sign Out</button>
                `;
            } else {
                // User is logged out behavior (Default)
                // We reset it just in case, but usually it starts as signed out
                navActions.innerHTML = `
                    <a href="login.html" class="btn btn-outline" style="margin-right: 12px; border: none; color: var(--color-white);">Sign In</a>
                    <a href="signup.html" class="btn btn-primary">Start for Free</a>
                `;
            }
        });
    }
});
