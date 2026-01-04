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
            let actionsHtml = '';

            // Shared Theme Toggle Button
            const themeToggleHtml = `
                <button id="theme-toggle" class="theme-toggle" aria-label="Toggle Theme">
                    <ion-icon name="sunny-outline" id="theme-icon"></ion-icon>
                </button>
            `;

            if (user) {
                // User is logged in
                console.log('User logged in, updating navbar');
                actionsHtml = `
                    ${themeToggleHtml}
                    <a href="application.html" class="btn btn-apply">Apply Now</a>
                    <a href="dashboard.html" class="btn btn-outline" style="border: none; color: var(--color-white);">Dashboard</a>
                    <button onclick="authHelpers.signOut()" class="btn btn-outline" style="border: 1px solid var(--color-border);">Sign Out</button>
                `;
            } else {
                // User is logged out behavior (Default)
                actionsHtml = `
                    ${themeToggleHtml}
                    <a href="login.html" class="btn btn-outline" style="border: none; color: var(--color-white);">Sign In</a>
                    <a href="signup.html" class="btn btn-primary">Start for Free</a>
                `;
            }

            navActions.innerHTML = actionsHtml;
            navActions.classList.add('is-loaded'); // Reveal navbar actions

            // Re-initialize theme logic since we overwrote the DOM
            if (window.initTheme) {
                window.initTheme();
            }
        });
    }
});
