// Theme Toggle Functionality
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    // We need to re-fetch this every time because the DOM might have changed
    const themeIcon = document.getElementById('theme-icon');

    // Check for saved theme preference or default to 'dark'
    const currentTheme = localStorage.getItem('theme') || 'dark';

    // Build the icon if it's missing (happens when navbar.js rewrites HTML)
    // But navbar.js should include the icon in its template.

    // Set theme attribute
    html.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggle) {
        // Remove old event listeners by cloning
        const newToggle = themeToggle.cloneNode(true);
        themeToggle.parentNode.replaceChild(newToggle, themeToggle);

        newToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
}

// Update theme icon based on current theme
function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        if (theme === 'dark') {
            themeIcon.setAttribute('name', 'sunny-outline');
        } else {
            themeIcon.setAttribute('name', 'moon-outline');
        }
    }
}

// Make it global
window.initTheme = initTheme;

// Init on load
document.addEventListener('DOMContentLoaded', initTheme);
