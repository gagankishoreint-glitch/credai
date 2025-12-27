// Theme Toggle Functionality

// Check for saved theme preference or default to 'light'
const currentTheme = localStorage.getItem('theme') || 'light';
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

// Set initial theme
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeIcon(currentTheme);
updateLogo(currentTheme);

// Theme toggle event listener
if (themeToggle) {
    themeToggle.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        updateLogo(newTheme);
    });
}

function updateLogo(theme) {
    const logos = document.querySelectorAll('.logo-image');
    logos.forEach(logo => {
        if (theme === 'dark') {
            logo.src = 'assets/logo-dark.png';
        } else {
            logo.src = 'assets/logo.png';
        }
    });
}

function updateThemeIcon(theme) {
    if (themeIcon) {
        if (theme === 'light') {
            // Moon icon for light mode (click to go dark)
            themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
        } else {
            // Sun icon for dark mode (click to go light)
            themeIcon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
        }
    }
}
// Auth State Management
document.addEventListener('DOMContentLoaded', () => {
    const userMode = localStorage.getItem('userMode');
    const loginBtn = document.getElementById('navLoginBtn');
    const dashboardBtn = document.getElementById('navDashboardBtn');

    if (loginBtn && dashboardBtn) {
        if (userMode === 'guest' || userMode === 'user') {
            // User is logged in
            loginBtn.style.display = 'none';
            dashboardBtn.style.display = 'inline-flex';
        } else {
            // User is logged out
            loginBtn.style.display = 'inline-flex';
            dashboardBtn.style.display = 'none';
        }
    }

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menuToggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (menuToggle && navbarMenu) {
        menuToggle.addEventListener('click', () => {
            navbarMenu.classList.toggle('active');
            // Change icon if needed
            const isOpened = navbarMenu.classList.contains('active');
            menuToggle.innerHTML = isOpened
                ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'
                : '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
        });
    }
});
