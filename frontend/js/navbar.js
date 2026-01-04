document.addEventListener('DOMContentLoaded', () => {
    console.log('Navbar.js loaded - Version 2.0 (Dropdowns Active)');
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

            if (user) {
                // User is logged in
                console.log('User logged in, updating navbar');
                actionsHtml = `
                    <a href="dashboard.html" class="btn btn-primary" style="margin-right: 12px;">Dashboard</a>
                    <a href="application.html" class="btn btn-outline" style="border: none; color: var(--color-white);">Apply Now</a>
                    
                    <a href="settings.html" class="btn btn-icon" title="Settings" style="color: var(--color-white); font-size: 1.5rem; padding: 8px;">
                        <ion-icon name="settings-outline"></ion-icon>
                    </a>
                    
                    <button onclick="authHelpers.signOut()" class="btn btn-icon" title="Sign Out" style="background: none; border: none; color: var(--color-white); font-size: 1.5rem; padding: 8px; cursor: pointer;">
                        <ion-icon name="log-out-outline"></ion-icon>
                    </button>
                `;
            } else {
                // User is logged out behavior (Default)
                actionsHtml = `
                    <a href="login.html" class="btn btn-outline" style="border: none; color: var(--color-white);">Sign In</a>
                    <a href="signup.html" class="btn btn-primary">Start for Free</a>
                `;
            }

            navActions.innerHTML = actionsHtml;
            navActions.classList.add('is-loaded'); // Reveal navbar actions
        });
    }

    // Load AI Widget script dynamically if not present
    if (!document.querySelector('script[src*="ai-widget.js"]')) {
        const script = document.createElement('script');
        script.src = 'js/ai-widget.js';
        document.body.appendChild(script);
    }
});
